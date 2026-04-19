// panel.js — AI Mode Side Panel Logic
// Manages page analysis, chat loop, command dispatch, and D3.js visualization.

"use strict";

const API_BASE = "http://localhost:8000";

// ── DOM References ────────────────────────────────────────────────────────────
const $statusBadge    = document.getElementById("status-badge");
const $pageCard       = document.getElementById("page-card");
const $pageCardHeader = document.getElementById("page-card-header");
const $cardBody       = document.getElementById("page-card-body");
const $btnCollapse    = document.getElementById("btn-collapse");
const $pageSkeleton   = document.getElementById("page-skeleton");
const $pageContent    = document.getElementById("page-content");
const $pageError      = document.getElementById("page-error");
const $errorMsg       = document.getElementById("error-msg");
const $pageTitle      = document.getElementById("page-title");
const $pageSummary    = document.getElementById("page-summary");
const $contentType    = document.getElementById("content-type-badge");
const $readTime       = document.getElementById("read-time");
const $sentiment      = document.getElementById("sentiment-badge");
const $topicPills     = document.getElementById("topic-pills");
const $chatMessages   = document.getElementById("chat-messages");
const $chatInput      = document.getElementById("chat-input");
const $btnSend        = document.getElementById("btn-send");
const $btnRetry       = document.getElementById("btn-retry");
const $graphSection   = document.getElementById("graph-section");
const $graphLoading   = document.getElementById("graph-loading");
const $graphSvg       = document.getElementById("graph-svg");
const $btnCloseGraph  = document.getElementById("btn-close-graph");

// ── State ─────────────────────────────────────────────────────────────────────
let currentPageData = null;
let isLoading = false;

// ── Init ──────────────────────────────────────────────────────────────────────
async function init() {
  setStatus("idle");

  // Check if there's already cached analysis for the current tab
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) return;

  const cached = await chrome.runtime.sendMessage({
    type: "GET_CACHED_ANALYSIS",
    tabId: tab.id,
  });

  if (cached) {
    currentPageData = cached.payload;
    renderAnalysis(cached);
    setStatus("ready");
  } else {
    // Trigger extraction on the active tab
    triggerPageExtraction(tab.id);
  }
}

async function triggerPageExtraction(tabId) {
  setStatus("analyzing");
  showSkeleton();

  chrome.scripting.executeScript({
    target: { tabId },
    func: extractPageAndSend,
  }).catch((err) => {
    showError("Cannot analyze this page (restricted URL).");
    setStatus("error");
  });
}

// This function runs IN the tab context
function extractPageAndSend() {
  const getMetaContent = (name) => {
    const el = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
    return el ? el.getAttribute("content") ?? "" : "";
  };

  const headings = Array.from(document.querySelectorAll("h1,h2,h3"))
    .map((h) => ({ level: h.tagName.toLowerCase(), text: h.innerText.trim() }))
    .filter((h) => h.text.length > 0).slice(0, 30);

  const scope = document.querySelector("article, main, [role=main]") || document.body;
  const paragraphs = Array.from(scope.querySelectorAll("p"))
    .map((p) => p.innerText.trim()).filter((t) => t.length > 50).slice(0, 80);

  const links = Array.from(document.querySelectorAll("a[href]"))
    .map((a) => ({ text: a.innerText.trim().slice(0,100), href: a.href }))
    .filter((l) => l.text.length > 2 && l.href.startsWith("http")).slice(0, 50);

  const tables = Array.from(document.querySelectorAll("table")).map((t) => ({
    headers: Array.from(t.querySelectorAll("th")).map((th) => th.innerText.trim()),
    rows: Array.from(t.querySelectorAll("tr")).slice(1, 10).map((tr) =>
      Array.from(tr.querySelectorAll("td")).map((td) => td.innerText.trim())
    ),
  }));

  const payload = {
    url: window.location.href,
    title: document.title,
    description: getMetaContent("description") || getMetaContent("og:description"),
    author: getMetaContent("author"),
    publishedDate: getMetaContent("article:published_time"),
    text: paragraphs.join("\n\n"),
    wordCount: paragraphs.join(" ").split(/\s+/).length,
    headings,
    links,
    tables,
  };

  chrome.runtime.sendMessage({ type: "PAGE_CONTENT", payload });
}

// ── Message Listener (from background.js) ────────────────────────────────────
chrome.runtime.onMessage.addListener((message) => {
  if (message.type === "PAGE_CONTENT") {
    currentPageData = message.payload;
    analyzeWithBackend(message.payload);
  }
});

// ── Backend Communication ─────────────────────────────────────────────────────
async function analyzeWithBackend(payload) {
  setStatus("analyzing");
  showSkeleton();

  try {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();
    renderAnalysis(data);
    setStatus("ready");
  } catch (err) {
    if (err.message.includes("fetch") || err.message.includes("Failed")) {
      showError("⚡ Backend offline. Start the server: cd pocs/chrome-ai-mode && .\\start_server.ps1");
    } else {
      showError(err.message);
    }
    setStatus("error");
  }
}

async function sendExploreCommand(command) {
  if (!currentPageData) {
    appendAIMessage("⚠️ No page data yet. Navigate to a webpage first.");
    return;
  }

  const typingId = appendTypingIndicator();
  setLoading(true);

  try {
    if (command === "visualize") {
      removeTypingIndicator(typingId);
      setLoading(false);
      await showGraph();
      return;
    }

    const res = await fetch(`${API_BASE}/explore`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command, page: currentPageData }),
    });

    removeTypingIndicator(typingId);

    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();
    appendAIMessage(data.result);
  } catch (err) {
    removeTypingIndicator(typingId);
    appendAIMessage(`❌ Error: ${err.message}`);
  } finally {
    setLoading(false);
  }
}

// ── D3.js Graph ───────────────────────────────────────────────────────────────
async function showGraph() {
  $graphSection.style.display = "block";
  $graphLoading.style.display = "flex";
  $graphSvg.style.display = "none";

  // Scroll graph into view
  $graphSection.scrollIntoView({ behavior: "smooth", block: "nearest" });

  try {
    const res = await fetch(`${API_BASE}/graph`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ page: currentPageData }),
    });

    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const graphData = await res.json();
    renderD3Graph(graphData);
  } catch (err) {
    $graphLoading.innerHTML = `<span style="color:var(--error)">Failed to build graph: ${err.message}</span>`;
  }
}

function renderD3Graph(data) {
  $graphLoading.style.display = "none";
  $graphSvg.style.display = "block";

  // Clear previous graph
  d3.select($graphSvg).selectAll("*").remove();

  const width = $graphSvg.clientWidth || 320;
  const height = 260;

  const svg = d3.select($graphSvg)
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("width", width)
    .attr("height", height);

  const nodeColorMap = {
    topic:   "#6366f1",
    concept: "#8b5cf6",
    entity:  "#06b6d4",
    claim:   "#f59e0b",
    source:  "#22c55e",
  };

  // Simulation
  const simulation = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.links).id((d) => d.id).distance(80))
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide(22));

  // Defs: arrow marker
  svg.append("defs").append("marker")
    .attr("id", "arrowhead")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 20)
    .attr("refY", 0)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("fill", "rgba(255,255,255,0.15)");

  // Links
  const link = svg.append("g")
    .selectAll("line")
    .data(data.links)
    .join("line")
    .attr("class", "graph-link")
    .attr("marker-end", "url(#arrowhead)");

  // Link labels
  const linkLabel = svg.append("g")
    .selectAll("text")
    .data(data.links)
    .join("text")
    .attr("class", "graph-link-label")
    .text((d) => d.label || "");

  // Nodes
  const node = svg.append("g")
    .selectAll("g")
    .data(data.nodes)
    .join("g")
    .attr("class", "graph-node")
    .call(
      d3.drag()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on("drag", (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on("end", (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null; d.fy = null;
        })
    );

  node.append("circle")
    .attr("r", 10)
    .attr("fill", (d) => nodeColorMap[d.type] || "#6366f1")
    .attr("opacity", 0.85);

  node.append("text")
    .attr("dy", 22)
    .attr("text-anchor", "middle")
    .text((d) => (d.label || d.id).slice(0, 18));

  node.append("title").text((d) => d.label || d.id);

  // Tick
  simulation.on("tick", () => {
    const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

    link
      .attr("x1", (d) => clamp(d.source.x, 10, width - 10))
      .attr("y1", (d) => clamp(d.source.y, 10, height - 10))
      .attr("x2", (d) => clamp(d.target.x, 10, width - 10))
      .attr("y2", (d) => clamp(d.target.y, 10, height - 10));

    linkLabel
      .attr("x", (d) => (d.source.x + d.target.x) / 2)
      .attr("y", (d) => (d.source.y + d.target.y) / 2);

    node.attr("transform", (d) => `translate(${clamp(d.x, 14, width-14)},${clamp(d.y, 14, height-14)})`);
  });
}

// ── Render Functions ──────────────────────────────────────────────────────────
function renderAnalysis(data) {
  // Always show meta row (stays visible when collapsed)
  $contentType.textContent = (data.content_type || "page").replace(/_/g, " ");
  $readTime.textContent = `${(data.reading_time_minutes || 0).toFixed(1)} min read`;
  $sentiment.textContent = sentimentEmoji(data.sentiment) + " " + (data.sentiment || "");

  // Show body content
  $pageSkeleton.style.display = "none";
  $pageError.style.display = "none";
  $pageContent.style.display = "block";

  $pageTitle.textContent = currentPageData?.title || "Analyzed Page";
  $pageSummary.textContent = data.summary || "";

  $topicPills.innerHTML = "";
  (data.key_topics || []).forEach((topic) => {
    const pill = document.createElement("span");
    pill.className = "topic-pill";
    pill.textContent = topic;
    $topicPills.appendChild(pill);
  });
}

function showSkeleton() {
  // Show skeleton inside the body (card stays open)
  $pageCard.classList.remove("is-collapsed");
  $pageSkeleton.style.display = "flex";
  $pageContent.style.display = "none";
  $pageError.style.display = "none";
  // Reset meta badges to placeholder
  $contentType.textContent = "—";
  $readTime.textContent = "— min read";
  $sentiment.textContent = "—";
}

function showError(msg) {
  $pageSkeleton.style.display = "none";
  $pageContent.style.display = "none";
  $pageError.style.display = "flex";
  $errorMsg.textContent = msg;
}

// ── Chat Helpers ──────────────────────────────────────────────────────────────
function appendUserMessage(text) {
  const msg = document.createElement("div");
  msg.className = "chat-message chat-message--user";
  msg.innerHTML = `
    <div class="msg-avatar">You</div>
    <div class="msg-bubble">${escapeHtml(text)}</div>
  `;
  $chatMessages.appendChild(msg);
  scrollChat();
  return msg;
}

function appendAIMessage(text) {
  const msg = document.createElement("div");
  msg.className = "chat-message chat-message--ai";
  msg.innerHTML = `
    <div class="msg-avatar">AI</div>
    <div class="msg-bubble">${renderMarkdown(text)}</div>
  `;
  $chatMessages.appendChild(msg);
  scrollChat();
  return msg;
}

function appendTypingIndicator() {
  const id = `typing-${Date.now()}`;
  const msg = document.createElement("div");
  msg.className = "chat-message chat-message--ai typing-indicator";
  msg.id = id;
  msg.innerHTML = `
    <div class="msg-avatar">AI</div>
    <div class="msg-bubble">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>
  `;
  $chatMessages.appendChild(msg);
  scrollChat();
  return id;
}

function removeTypingIndicator(id) {
  document.getElementById(id)?.remove();
}

function scrollChat() {
  $chatMessages.scrollTop = $chatMessages.scrollHeight;
}

// ── Utilities ────────────────────────────────────────────────────────────────
function setStatus(state) {
  const states = {
    idle:      { text: "Idle",      cls: "" },
    analyzing: { text: "Analyzing", cls: "badge--analyzing" },
    ready:     { text: "Ready",     cls: "badge--ready" },
    error:     { text: "Error",     cls: "badge--error" },
  };
  const s = states[state] || states.idle;
  $statusBadge.textContent = s.text;
  $statusBadge.className = `badge badge--status ${s.cls}`;
}

function setLoading(val) {
  isLoading = val;
  $btnSend.disabled = val;
  $chatInput.disabled = val;
}

function sentimentEmoji(s) {
  return { positive: "😊", negative: "😟", neutral: "😐", mixed: "🤔" }[s] || "💬";
}

function escapeHtml(str) {
  return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

// Minimal markdown renderer (bold, italic, headers, bullets, code)
function renderMarkdown(text) {
  return text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/^#### (.+)$/gm, "<h4>$1</h4>")
    .replace(/^### (.+)$/gm,  "<h3>$1</h3>")
    .replace(/^## (.+)$/gm,   "<h2>$1</h2>")
    .replace(/^# (.+)$/gm,    "<h2>$1</h2>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g,     "<em>$1</em>")
    .replace(/`(.+?)`/g,       "<code>$1</code>")
    .replace(/^[-*] (.+)$/gm,  "<li>$1</li>")
    .replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br>");
}

// ── Event Listeners ───────────────────────────────────────────────────────────
// Collapse / expand the page summary card
$pageCardHeader.addEventListener("click", (e) => {
  // Don't collapse if clicking the retry button inside the header
  if (e.target.closest(".btn-retry")) return;
  $pageCard.classList.toggle("is-collapsed");
  const isNowCollapsed = $pageCard.classList.contains("is-collapsed");
  $btnCollapse.setAttribute("aria-expanded", String(!isNowCollapsed));
});

// Command chip clicks
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    const command = chip.dataset.command;
    appendUserMessage(chip.querySelector("span:last-child").textContent.trim());
    sendExploreCommand(command);
  });
});

// Send button
$btnSend.addEventListener("click", sendUserInput);

// Enter key (no shift)
$chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendUserInput();
  }
});

// Auto-resize textarea
$chatInput.addEventListener("input", () => {
  $chatInput.style.height = "auto";
  $chatInput.style.height = Math.min($chatInput.scrollHeight, 100) + "px";
});

// Retry button
$btnRetry.addEventListener("click", () => {
  if (currentPageData) {
    analyzeWithBackend(currentPageData);
  } else {
    init();
  }
});

// Close graph
$btnCloseGraph.addEventListener("click", () => {
  $graphSection.style.display = "none";
});

// Tab changes → re-analyze
chrome.tabs.onActivated.addListener(() => init());
chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.status === "complete") init();
});

function sendUserInput() {
  const text = $chatInput.value.trim();
  if (!text || isLoading) return;
  $chatInput.value = "";
  $chatInput.style.height = "auto";
  appendUserMessage(text);
  sendExploreCommand(text);
}

// ── Start ─────────────────────────────────────────────────────────────────────
init();
