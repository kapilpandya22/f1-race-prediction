(() => {
  // Minimal, self-contained floating chat button.
  // No external deps. Safe to include on every page.

  if (window.__cgChatWidgetMounted) return;
  window.__cgChatWidgetMounted = true;

  const STYLE_ID = "cg-chat-widget-style";
  if (!document.getElementById(STYLE_ID)) {
    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = `
      :root{--cg-chat-accent:#00d4ff;--cg-chat-bg:#080b18;--cg-chat-b1:#1a2340;--cg-chat-text:#eef2ff;--cg-chat-muted:rgba(160,178,215,.9)}
      #cg-chat-widget{position:fixed;right:18px;bottom:18px;z-index:9999;font-family:Formula1,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}
      #cg-chat-fab{width:52px;height:52px;border-radius:999px;display:flex;align-items:center;justify-content:center;cursor:pointer;
        background:linear-gradient(180deg,rgba(0,212,255,.18),rgba(0,212,255,.06));
        border:1px solid rgba(0,212,255,.55);
        box-shadow:0 10px 30px rgba(0,0,0,.45),0 0 22px rgba(0,212,255,.10);
        color:var(--cg-chat-text);
        transition:transform .12s ease, box-shadow .12s ease, background .12s ease;
        user-select:none;
      }
      #cg-chat-fab:hover{transform:translateY(-1px);box-shadow:0 14px 34px rgba(0,0,0,.52),0 0 26px rgba(0,212,255,.14)}
      #cg-chat-fab:active{transform:translateY(0px) scale(.99)}
      #cg-chat-fab svg{width:22px;height:22px;opacity:.95}

      #cg-chat-panel{position:absolute;right:0;bottom:64px;width:min(360px, calc(100vw - 36px));
        background:rgba(8,11,24,.96);border:1px solid rgba(26,35,64,.9);border-radius:10px;
        box-shadow:0 22px 60px rgba(0,0,0,.60);
        overflow:hidden;
        transform-origin:bottom right;
        transform:scale(.98);
        opacity:0;
        pointer-events:none;
        transition:opacity .14s ease, transform .14s ease;
      }
      #cg-chat-panel.open{opacity:1;transform:scale(1);pointer-events:auto}
      #cg-chat-head{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 12px;
        border-bottom:1px solid rgba(255,255,255,.06);
        background:linear-gradient(135deg,rgba(232,0,45,.12),rgba(0,212,255,.06));
      }
      #cg-chat-title{font-weight:800;letter-spacing:1.5px;text-transform:uppercase;font-size:11px;color:var(--cg-chat-text)}
      #cg-chat-sub{font-size:11px;color:var(--cg-chat-muted)}
      #cg-chat-close{cursor:pointer;border:1px solid rgba(255,255,255,.10);background:rgba(255,255,255,.04);
        color:var(--cg-chat-text);border-radius:8px;padding:6px 8px;font-size:12px}
      #cg-chat-body{padding:12px;color:var(--cg-chat-muted);font-size:12px;line-height:1.35}
      #cg-chat-body b{color:var(--cg-chat-text)}
    `;
    document.head.appendChild(style);
  }

  const root = document.getElementById("cg-chat-widget") || (() => {
    const el = document.createElement("div");
    el.id = "cg-chat-widget";
    document.body.appendChild(el);
    return el;
  })();

  root.innerHTML = `
    <div id="cg-chat-panel" role="dialog" aria-label="Chat">
      <div id="cg-chat-head">
        <div>
          <div id="cg-chat-title">Chat</div>
          <div id="cg-chat-sub">Coming soon</div>
        </div>
        <button id="cg-chat-close" type="button" aria-label="Close">Close</button>
      </div>
      <div id="cg-chat-body">
        <b>Chat widget placeholder</b><br/>
        You can wire this to your chatbot backend later.
      </div>
    </div>
    <div id="cg-chat-fab" title="Chat" aria-label="Open chat" role="button" tabindex="0">
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path d="M7 18l-3 3V7a3 3 0 013-3h10a3 3 0 013 3v7a3 3 0 01-3 3H7z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
        <path d="M8 9h8M8 12h6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
      </svg>
    </div>
  `;

  const panel = root.querySelector("#cg-chat-panel");
  const fab = root.querySelector("#cg-chat-fab");
  const closeBtn = root.querySelector("#cg-chat-close");

  const setOpen = (open) => {
    panel.classList.toggle("open", open);
  };

  const toggle = () => setOpen(!panel.classList.contains("open"));

  fab.addEventListener("click", toggle);
  fab.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      toggle();
    }
  });
  closeBtn.addEventListener("click", () => setOpen(false));

  // Close on ESC
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") setOpen(false);
  });
})();
