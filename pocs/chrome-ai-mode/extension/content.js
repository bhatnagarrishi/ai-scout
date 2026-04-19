// content.js — Runs in every tab at document_idle
// Extracts page structure and reports to the background service worker.

(function () {
  "use strict";

  // Avoid double-injection
  if (window.__aiModeInjected) return;
  window.__aiModeInjected = true;

  const getMetaContent = (name) => {
    const el = document.querySelector(
      `meta[name="${name}"], meta[property="${name}"]`
    );
    return el ? el.getAttribute("content") ?? "" : "";
  };

  function extractPageData() {
    const headings = Array.from(document.querySelectorAll("h1,h2,h3,h4"))
      .map((h) => ({ level: h.tagName.toLowerCase(), text: h.innerText.trim() }))
      .filter((h) => h.text.length > 0)
      .slice(0, 40);

    // Prefer semantic containers; fall back to all <p>
    const containers = document.querySelectorAll(
      "article, main, [role=main], .post-content, .entry-content, #content"
    );
    const scope = containers.length > 0 ? containers[0] : document.body;

    const paragraphs = Array.from(scope.querySelectorAll("p"))
      .map((p) => p.innerText.trim())
      .filter((t) => t.length > 50)
      .slice(0, 80);

    const links = Array.from(document.querySelectorAll("a[href]"))
      .map((a) => ({ text: a.innerText.trim().slice(0, 100), href: a.href }))
      .filter((l) => l.text.length > 2 && l.href.startsWith("http"))
      .slice(0, 60);

    const tables = Array.from(document.querySelectorAll("table")).map((table) => {
      const headers = Array.from(table.querySelectorAll("th")).map((th) =>
        th.innerText.trim()
      );
      const rows = Array.from(table.querySelectorAll("tr"))
        .slice(0, 15)
        .map((tr) =>
          Array.from(tr.querySelectorAll("td")).map((td) => td.innerText.trim())
        )
        .filter((row) => row.some((cell) => cell.length > 0));
      return { headers, rows };
    });

    return {
      url: window.location.href,
      title: document.title,
      description:
        getMetaContent("description") ||
        getMetaContent("og:description") ||
        "",
      ogImage: getMetaContent("og:image"),
      author: getMetaContent("author") || getMetaContent("article:author"),
      publishedDate:
        getMetaContent("article:published_time") || getMetaContent("date"),
      text: paragraphs.join("\n\n"),
      wordCount: paragraphs.join(" ").split(/\s+/).length,
      headings,
      links,
      tables,
      extractedAt: Date.now(),
    };
  }

  function sendToBackground() {
    try {
      const payload = extractPageData();
      chrome.runtime.sendMessage({ type: "PAGE_CONTENT", payload }, (response) => {
        if (chrome.runtime.lastError) {
          // Background worker may not be ready yet — that's OK
        }
      });
    } catch (e) {
      // Fail silently — restricted page or extension context issue
    }
  }

  // Send once on load
  sendToBackground();

  // Re-send on SPA navigation (pushState / replaceState)
  const originalPushState = history.pushState.bind(history);
  const originalReplaceState = history.replaceState.bind(history);

  history.pushState = function (...args) {
    originalPushState(...args);
    setTimeout(sendToBackground, 1500);
  };
  history.replaceState = function (...args) {
    originalReplaceState(...args);
    setTimeout(sendToBackground, 1500);
  };

  window.addEventListener("popstate", () => setTimeout(sendToBackground, 1500));
})();
