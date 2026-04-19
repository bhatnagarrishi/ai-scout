// background.js — AI Mode Service Worker (Manifest V3)
// Manages tab events, content script communication, and API routing.

const API_BASE = "http://localhost:8000";

// ── Open side panel when the toolbar icon is clicked ──────────────────────────
chrome.action.onClicked.addListener((tab) => {
  chrome.sidePanel.open({ tabId: tab.id });
});

// ── Listen for messages from content.js and panel.js ─────────────────────────
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "PAGE_CONTENT") {
    handlePageContent(message.payload, sender.tab?.id)
      .then((result) => sendResponse({ ok: true, data: result }))
      .catch((err) => sendResponse({ ok: false, error: err.message }));
    return true; // keep channel open for async response
  }

  if (message.type === "EXPLORE_COMMAND") {
    handleExploreCommand(message.payload)
      .then((result) => sendResponse({ ok: true, data: result }))
      .catch((err) => sendResponse({ ok: false, error: err.message }));
    return true;
  }

  if (message.type === "GRAPH_REQUEST") {
    handleGraphRequest(message.payload)
      .then((result) => sendResponse({ ok: true, data: result }))
      .catch((err) => sendResponse({ ok: false, error: err.message }));
    return true;
  }

  if (message.type === "GET_CACHED_ANALYSIS") {
    getCachedAnalysis(message.tabId).then(sendResponse);
    return true;
  }
});

// ── Auto-extract page content on navigation ───────────────────────────────────
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url && !tab.url.startsWith("chrome://")) {
    // Inject content script to extract page data
    chrome.scripting.executeScript({
      target: { tabId },
      func: extractAndSend,
    }).catch(() => {}); // Silently fail on restricted pages
  }
});

// This function runs IN the tab context (not the service worker)
function extractAndSend() {
  const getMetaContent = (name) => {
    const el = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
    return el ? el.getAttribute("content") : "";
  };

  const headings = Array.from(document.querySelectorAll("h1,h2,h3"))
    .map((h) => ({ level: h.tagName, text: h.innerText.trim() }))
    .filter((h) => h.text.length > 0)
    .slice(0, 30);

  const paragraphs = Array.from(
    document.querySelectorAll("article p, main p, .content p, p")
  )
    .map((p) => p.innerText.trim())
    .filter((t) => t.length > 40)
    .slice(0, 60);

  const links = Array.from(document.querySelectorAll("a[href]"))
    .map((a) => ({ text: a.innerText.trim(), href: a.href }))
    .filter((l) => l.text.length > 2 && l.href.startsWith("http"))
    .slice(0, 50);

  const tables = Array.from(document.querySelectorAll("table")).map((table) => {
    const headers = Array.from(table.querySelectorAll("th")).map((th) => th.innerText.trim());
    const rows = Array.from(table.querySelectorAll("tr")).slice(1, 10).map((tr) =>
      Array.from(tr.querySelectorAll("td")).map((td) => td.innerText.trim())
    );
    return { headers, rows };
  }).slice(0, 5);

  const payload = {
    url: window.location.href,
    title: document.title,
    description: getMetaContent("description") || getMetaContent("og:description"),
    ogImage: getMetaContent("og:image"),
    text: paragraphs.join("\n"),
    headings,
    links,
    tables,
    extractedAt: Date.now(),
  };

  chrome.runtime.sendMessage({ type: "PAGE_CONTENT", payload });
}

// ── API Handlers ──────────────────────────────────────────────────────────────
async function handlePageContent(payload, tabId) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Backend error: ${res.status}`);
  const data = await res.json();

  // Cache per-tab so reopening the panel is instant
  if (tabId) {
    await chrome.storage.session.set({ [`analysis_${tabId}`]: { ...data, payload } });
  }
  return data;
}

async function handleExploreCommand(payload) {
  const res = await fetch(`${API_BASE}/explore`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Backend error: ${res.status}`);
  return res.json();
}

async function handleGraphRequest(payload) {
  const res = await fetch(`${API_BASE}/graph`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Backend error: ${res.status}`);
  return res.json();
}

async function getCachedAnalysis(tabId) {
  const key = `analysis_${tabId}`;
  const result = await chrome.storage.session.get(key);
  return result[key] || null;
}
