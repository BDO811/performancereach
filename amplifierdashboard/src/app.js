function mountLedger(R, OPT) {
  const NOW = OPT.now || Date.now();
  const ALLOWED = ["mehta@helix.harvard7.net", "amit@amplifierhealth.com"];
  const STAGES = [
    ["active", "Active", "Active / paying", "var(--mint)"],
    ["advanced", "Pilots", "Advanced / pilot", "var(--lav)"],
    ["early", "Early", "Early discussion", "var(--sky)"],
    ["proposal", "Proposals", "Proposal out", "var(--gold)"],
    ["partner", "Partners", "Grant / partner", "#d7a6ff"],
    ["stalled", "Stalled", "Stalled", "var(--rose)"],
    ["target", "Targets", "Target", "var(--faint)"]];
  const S = Object.fromEntries(STAGES.map(s => [s[0], s]));
  const INIT = { Amit: "AM", Jeremy: "JB", Camille: "CN", Troy: "TA", Maxwell: "MS", Max: "MM", Derek: "DD", Bryan: "BR" };
  const DIR = { out: "Sent", in: "Received", int: "Internal", cal: "Calendar" };
  const st = { nav: "all", chip: "all", sort: "recent", q: "", open: null, data: [], user: null, firstPaint: true };
  const esc = s => String(s ?? "").replace(/[&<>"]/g, m => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[m]));
  const days = t => Math.floor((NOW - t) / 864e5);
  const rel = t => !t ? "—" : days(t) <= 0 ? "Today" : days(t) === 1 ? "1d ago" : days(t) < 60 ? days(t) + "d ago" : new Date(t).toLocaleDateString("en-US", { month: "short", day: "numeric" });
  const fmt = t => new Date(t).toLocaleDateString("en-US", { month: "short", day: "numeric" });
  const initials = n => n.replace(/[^A-Za-z0-9 &/]/g, "").split(/[\s/&]+/).filter(Boolean).slice(0, 2).map(w => w[0]).join("").toUpperCase() || "?";
  const awaiting = c => c.threads.length && c.threads[0].d === "out" && days(c.last) >= 7;
  const ICON = {
    bolt: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>',
    flask: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6M10 3v6L4 19a2 2 0 0 0 2 3h12a2 2 0 0 0 2-3l-6-10V3"/></svg>',
    doc: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/></svg>',
    clock: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    search: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    bell: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9M10 21h4"/></svg>',
    wave: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M3 12h2M7 8v8M11 5v14M15 9v6M19 11v2"/></svg>',
    x: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>',
    plus: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>' };

  R.innerHTML = `<div class="shell"><div class="atmo"><i></i><i></i><i></i></div><div class="wrap" id="wrap"></div>
    <div class="scrim" id="scrim"></div><aside class="drawer" id="drawer" aria-hidden="true"></aside></div>`;
  const $ = s => R.querySelector(s), $$ = s => [...R.querySelectorAll(s)];
  const wrap = $("#wrap");

  /* ---------- liquid pill: leading edge moves first and faster, trailing edge catches up ---------- */
  function slidePill(bar, instant) {
    const pill = bar.querySelector(".pill"), t = bar.querySelector('[aria-pressed="true"]');
    if (!pill || !t) return;
    const l = t.offsetLeft, r = bar.scrollWidth - (t.offsetLeft + t.offsetWidth);
    const prev = pill.__st || { l, r };
    const fwd = l > prev.l;
    const out = "cubic-bezier(.215,.61,.355,1)", inout = "cubic-bezier(.645,.045,.355,1)";
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    pill.style.transition = instant || reduce ? "none" : fwd
      ? `right .36s ${out}, left .55s ${inout}` : `left .36s ${out}, right .55s ${inout}`;
    pill.style.left = l + "px"; pill.style.right = r + "px";
    pill.__st = { l, r };
    const sl = l - bar.clientWidth / 2 + t.offsetWidth / 2;
    if (bar.scrollWidth > bar.clientWidth) bar.scrollTo({ left: sl, behavior: reduce ? "auto" : "smooth" });
  }

  function spark(c) {
    const W = 104, H = 40, N = 20, b = new Array(N).fill(0);
    c.threads.forEach(t => { const w = Math.floor((NOW - t.t) / (7 * 864e5)); if (w >= 0 && w < N) b[N - 1 - w]++; });
    const col = S[c.stage][3];
    if (!c.threads.length) return `<svg class="spark" viewBox="0 0 ${W} ${H}" aria-hidden="true"><path d="M2 ${H - 6} H${W - 2}" stroke="var(--line-hi)" stroke-width="1.5" stroke-dasharray="3 4" fill="none"/></svg>`;
    const sm = b.map((v, i) => (b[i - 1] || 0) * .25 + v * .5 + (b[i + 1] || 0) * .25);
    const mx = Math.max(1, ...sm);
    const pts = sm.map((v, i) => [2 + i * (W - 4) / (N - 1), H - 4 - v / mx * (H - 10)]);
    const d = pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" ");
    const id = "g" + Math.random().toString(36).slice(2, 8), e = pts[N - 1];
    return `<svg class="spark" viewBox="0 0 ${W} ${H}" aria-hidden="true"><defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${col}" stop-opacity=".45"/><stop offset="1" stop-color="${col}" stop-opacity="0"/></linearGradient></defs>
      <path d="${d} L${W - 2} ${H} L2 ${H} Z" fill="url(#${id})"/><path d="${d}" fill="none" stroke="${col}" stroke-width="1.6" stroke-linejoin="round"/><circle cx="${e[0]}" cy="${e[1]}" r="2.4" fill="${col}"/></svg>`;
  }

  /* ---------- views ---------- */
  function gate(msg) {
    wrap.innerHTML = `<div class="gate glass"><div class="logo">${ICON.wave}</div><h1>Amplifier Ledger</h1>
      <p>Sign in with your Google account to open the client pipeline.</p>
      <button class="cta" id="signin">Continue with Google</button><div class="err" role="alert">${esc(msg || "")}</div></div>`;
    $("#signin").onclick = () => OPT.signIn().catch(e => gate(e.code === "auth/popup-closed-by-user" ? "" : "Sign-in did not complete: " + (e.message || e)));
  }

  function filtered() {
    const q = st.q.toLowerCase();
    let rows = st.data.filter(c =>
      (st.nav === "all" || c.stage === st.nav) &&
      (st.chip === "all" || (st.chip === "wait" ? awaiting(c) : c.origin === st.chip)) &&
      (!q || [c.name, c.contact, c.status, c.next, c.owner, ...c.threads.map(t => t.s)].join(" ").toLowerCase().includes(q)));
    const k = { recent: (a, b) => (b.last || 0) - (a.last || 0), activity: (a, b) => b.threads.length - a.threads.length || (b.last || 0) - (a.last || 0), az: (a, b) => a.name.localeCompare(b.name) }[st.sort];
    return rows.sort(k);
  }

  function shell() {
    const all = st.data, n = s => all.filter(c => c.stage === s).length;
    const wait = all.filter(awaiting).length, gtm = all.filter(c => c.origin === "gtm").length;
    const thr = all.reduce((a, c) => a + c.threads.length, 0);
    const tile = (k, ic, col, label, val, sub, i) => `<button class="tile glass" data-tile="${k}" style="--i:${i}"><span class="ic" style="background:${col}">${ICON[ic]}</span><span><small>${label}</small><b>${val}</b><span class="sub">${sub}</span></span></button>`;
    const ownerInit = st.user ? (st.user.displayName || st.user.email || "AM").split(/[\s@.]/).slice(0, 2).map(w => w[0]).join("").toUpperCase() : "AM";
    wrap.innerHTML = `
      <header class="bar glass">
        <div class="brand"><span class="logo">${ICON.wave}</span><span><b>Amplifier</b><small>Client Ledger</small></span></div>
        <nav class="nav" id="nav" aria-label="Stage"><span class="pill"></span>
          <button data-nav="all" aria-pressed="${st.nav === "all"}">All<span class="ct">${all.length}</span></button>
          ${STAGES.map(s => `<button data-nav="${s[0]}" aria-pressed="${st.nav === s[0]}">${s[1]}<span class="ct">${n(s[0])}</span></button>`).join("")}
        </nav>
        <div class="tools">
          <button class="iconbtn hide-sm" id="bell" title="Awaiting reply 7+ days">${ICON.bell}${wait ? `<span class="dot">${wait}</span>` : ""}</button>
          <button class="avatar" id="me" title="${esc(st.user ? st.user.email + " · sign out" : "Preview")}">${esc(ownerInit)}</button>
        </div>
      </header>
      <section class="head">
        <div><h1>Opportunities</h1><p>${all.length} companies across ${STAGES.length} stages · ${thr} email threads · ${gtm} with the GTM team</p></div>
        ${OPT.mode === "preview" ? `<span class="tag">Preview · snapshot Oct 31</span>` : `<span class="tag mono" id="sync">Live · Firestore</span>`}
      </section>
      <div id="banner"></div>
      <section class="tiles anim">
        ${tile("active", "bolt", "var(--mint)", "Active / paying", n("active"), "customers live today", 0)}
        ${tile("advanced", "flask", "var(--lav)", "Advanced / pilot", n("advanced"), "pilots and scoped deals", 1)}
        ${tile("proposal", "doc", "var(--gold)", "Proposal out", n("proposal"), "awaiting first reply", 2)}
        ${tile("wait", "clock", "var(--coral)", "Awaiting reply", wait, "our email last, 7+ days", 3)}
      </section>
      <section class="rail">
        ${[["all", "All"], ["email", "Email"], ["gtm", "GTM team"], ["drive", "Drive proposal"], ["wait", "Awaiting reply"]].map(([k, l]) => `<button class="chip" data-chip="${k}" aria-pressed="${st.chip === k}">${l}</button>`).join("")}
        <label class="search glass">${ICON.search}<input id="q" type="search" placeholder="Company, contact or subject" value="${esc(st.q)}"></label>
        <div class="seg" id="seg"><span class="pill"></span>
          ${[["recent", "Recent"], ["activity", "Activity"], ["az", "A–Z"]].map(([k, l]) => `<button data-sort="${k}" aria-pressed="${st.sort === k}">${l}</button>`).join("")}
        </div>
      </section>
      <section class="grid" id="grid"></section>
      <p class="foot-note">${OPT.mode === "preview" ? "Preview build with this morning's data. The live page signs in with Google and reads Firestore." : "Synced nightly from Gmail, Slack and Notion. GTM team = surfaced in Slack, no email thread yet."}</p>`;
    $$("[data-nav]").forEach(b => b.onclick = () => { st.nav = b.dataset.nav; $$("[data-nav]").forEach(x => x.setAttribute("aria-pressed", x === b)); slidePill($("#nav")); grid(true); });
    $$("[data-sort]").forEach(b => b.onclick = () => { st.sort = b.dataset.sort; $$("[data-sort]").forEach(x => x.setAttribute("aria-pressed", x === b)); slidePill($("#seg")); grid(true); });
    $$("[data-chip]").forEach(b => b.onclick = () => { st.chip = b.dataset.chip; $$("[data-chip]").forEach(x => x.setAttribute("aria-pressed", x === b)); grid(true); });
    $$("[data-tile]").forEach(b => b.onclick = () => {
      const k = b.dataset.tile;
      if (k === "wait") { st.chip = "wait"; st.nav = "all"; } else { st.nav = k; st.chip = "all"; }
      $$("[data-nav]").forEach(x => x.setAttribute("aria-pressed", x.dataset.nav === st.nav));
      $$("[data-chip]").forEach(x => x.setAttribute("aria-pressed", x.dataset.chip === st.chip));
      slidePill($("#nav")); grid(true);
    });
    $("#bell").onclick = () => R.querySelector('[data-tile="wait"]').click();
    $("#q").oninput = e => { st.q = e.target.value; grid(false); };
    $("#me").onclick = () => { if (OPT.signOut && st.user) OPT.signOut(); };
    requestAnimationFrame(() => { slidePill($("#nav"), true); slidePill($("#seg"), true); });
    grid(true);
  }

  function grid(animate) {
    const g = $("#grid"); if (!g) return;
    const rows = filtered();
    g.classList.toggle("anim", !!animate);
    g.innerHTML = rows.map((c, i) => {
      const s = S[c.stage], aw = awaiting(c), own = (c.owner || "").split(" / ")[0];
      const flag = c.origin === "gtm" ? `<span class="tag flag gtm">GTM team</span>` : c.origin === "drive" ? `<span class="tag flag drive">Not sent</span>` : aw ? `<span class="tag flag wait">Awaiting ${days(c.last)}d</span>` : `<span class="tag flag" style="color:${s[3]}">${c.threads.length} thread${c.threads.length === 1 ? "" : "s"}</span>`;
      return `<button class="card" data-id="${esc(c.id)}" style="--i:${Math.min(i, 24)}">
        <span class="top"><span class="mono-av">${esc(initials(c.name))}</span><span class="nm"><b>${esc(c.name)}</b><small>${esc(c.contact || c.status)}</small></span></span>
        <span class="mid"><span><small>Last touch</small><b class="${aw ? "stale" : ""}">${rel(c.last)}</b></span>${spark(c)}</span>
        <span class="foot"><span class="tag">${s[1]}</span>${flag}<span class="own" title="${esc(c.owner)}">${INIT[own] || initials(own || "?")}</span></span>
      </button>`; }).join("") || `<div class="empty glass">No opportunities match these filters.</div>`;
    $$(".card").forEach(b => b.onclick = () => drawer(b.dataset.id));
  }

  function drawer(id) {
    const c = st.data.find(x => x.id === id); if (!c) return;
    const s = S[c.stage], aw = awaiting(c);
    const th = c.threads.length ? c.threads.map(t => `<a class="th" target="_blank" rel="noopener" href="https://mail.google.com/mail/u/0/#all/${esc(t.id)}"><span class="d mono">${fmt(t.t)}</span><span class="k">${DIR[t.d] || t.d}</span><span class="s">${esc(t.s)}</span></a>`).join("")
      : `<div class="note">${c.origin === "gtm" ? "GTM team opportunity. Surfaced in #customers-discovery-insights with no email thread yet; the nightly sync attaches threads when they appear." : "Proposal drafted in Drive. No send found in email."}</div>`;
    const d = $("#drawer");
    d.innerHTML = `<button class="iconbtn x" id="close" aria-label="Close">${ICON.x}</button>
      <span class="mono-av" style="width:48px;height:48px;font-size:15px">${esc(initials(c.name))}</span>
      <h2>${esc(c.name)}</h2>
      <div class="tags"><span class="tag" style="color:${s[3]}">${s[2]}</span>${c.origin === "gtm" ? '<span class="tag flag gtm">GTM team</span>' : ""}${aw ? `<span class="tag flag wait">Awaiting reply · ${days(c.last)}d</span>` : ""}<span class="tag">${esc(c.owner)}</span></div>
      <div class="kv glass"><div><span>Status</span><p>${esc(c.status)}</p></div><div><span>Next step</span><p>${esc(c.next)}</p></div>
        ${c.contact ? `<div><span>Contacts</span><p>${esc(c.contact)}</p></div>` : ""}
        ${c.drive ? `<div><span>Proposal</span><p><a href="${esc(c.drive)}" target="_blank" rel="noopener">Open in Drive</a></p></div>` : ""}
        <div><span>Last touch</span><p>${c.last ? fmt(c.last) + " · " + rel(c.last) : "No email yet"}</p></div></div>
      <div class="threads"><h3>Email threads · ${c.threads.length}</h3>${th}</div>`;
    d.classList.add("on"); d.setAttribute("aria-hidden", "false"); $("#scrim").classList.add("on");
    const close = () => { d.classList.remove("on"); d.setAttribute("aria-hidden", "true"); $("#scrim").classList.remove("on"); };
    $("#close").onclick = close; $("#scrim").onclick = close; $("#close").focus();
    R.addEventListener("keydown", e => { if (e.key === "Escape") close(); }, { once: true });
  }

  addEventListener("resize", () => { const n = $("#nav"), g = $("#seg"); n && slidePill(n, true); g && slidePill(g, true); });

  return {
    gate, setUser(u) { st.user = u; },
    setData(rows) { st.data = rows; if (!$("#grid")) shell(); else { const keepQ = st.q; shell(); st.q = keepQ; } },
    banner(html) { const b = $("#banner"); if (b) b.innerHTML = html; return b; }
  };
}

/* ---------- boot ---------- */
(function boot() {
  const R = window.__LEDGER_ROOT__ || document.getElementById("app-root");
  const CFG = window.__LEDGER_CFG__;
  const norm = c => ({ ...c, threads: (c.threads || []).slice().sort((a, b) => b.t - a.t), last: (c.threads && c.threads.length) ? Math.max(...c.threads.map(t => t.t)) : (c.last || null) });
  if (CFG.mode === "preview") {
    const ui = mountLedger(R, { mode: "preview", now: CFG.now });
    ui.setData(CFG.seed.map(norm));
    return;
  }
  const V = "10.12.2", base = `https://www.gstatic.com/firebasejs/${V}/`;
  const load = src => new Promise((ok, no) => { const s = document.createElement("script"); s.src = src; s.onload = ok; s.onerror = () => no(new Error("Could not load " + src)); document.head.appendChild(s); });
  let ui;
  (async () => {
    await load(base + "firebase-app-compat.js");
    await Promise.all([load(base + "firebase-auth-compat.js"), load(base + "firebase-firestore-compat.js")]);
    const app = firebase.apps.length ? firebase.app() : firebase.initializeApp(CFG.firebase);
    const auth = firebase.auth(), db = firebase.firestore();
    const provider = new firebase.auth.GoogleAuthProvider(); provider.setCustomParameters({ prompt: "select_account" });
    ui = mountLedger(R, { mode: "live", signIn: () => auth.signInWithPopup(provider), signOut: () => auth.signOut() });
    let unsub = null;
    auth.onAuthStateChanged(user => {
      if (unsub) { unsub(); unsub = null; }
      if (!user) { ui.gate(); return; }
      ui.setUser(user);
      unsub = db.collection("opportunities").onSnapshot(snap => {
        const rows = snap.docs.map(d => norm({ id: d.id, ...d.data() }));
        ui.setData(rows);
        if (!rows.length && CFG.seed && CFG.seed.length) {
          const b = ui.banner(`<div class="banner glass"><span><b>Firestore is empty.</b> Load the ${CFG.seed.length} opportunities from the Oct 31 build.</span><button class="cta" id="import">Load ${CFG.seed.length} opportunities</button></div>`);
          b.querySelector("#import").onclick = async e => {
            e.target.disabled = true; e.target.textContent = "Loading…";
            const batch = db.batch();
            CFG.seed.forEach(c => { const { id, ...rest } = c; batch.set(db.collection("opportunities").doc(id), { ...rest, syncedAt: firebase.firestore.FieldValue.serverTimestamp() }, { merge: true }); });
            try { await batch.commit(); } catch (err) { e.target.disabled = false; e.target.textContent = "Retry"; b.querySelector("span").textContent = "Import failed: " + err.message; }
          };
        }
      }, err => {
        auth.signOut();
        ui.gate(err.code === "permission-denied" ? `${user.email} does not have access. Sign in with mehta@helix.harvard7.net or amit@amplifierhealth.com.` : "Could not load data: " + err.message);
      });
    });
  })().catch(e => { (ui || mountLedger(R, { mode: "live" })).gate("Could not start: " + e.message); });
})();
