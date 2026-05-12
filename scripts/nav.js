(function () {

  // ─── PATH DEPTH DETECTION ─────────────────────────────────────────────────
  const depth1Dirs = [
    'unexpected-journeys',
    'the-embers',
    'dossiers',
    'war-intel',
    'atlas',
    'armory',
    'command-post'
  ];
  const depth2Dirs = [
    'unexpected-journey-brief-account',
    'unexpected-journey-full-account'
  ];

  const parts = window.location.pathname.split('/').filter(Boolean);
  let depth = 0;
  parts.forEach(function (p) {
    if (depth1Dirs.includes(p)) depth = Math.max(depth, 1);
    if (depth2Dirs.includes(p))  depth = Math.max(depth, 2);
  });

  var root = '';
  for (var i = 0; i < depth; i++) root += '../';

  // ─── CRITICAL POSITIONING CSS ─────────────────────────────────────────────
  document.head.insertAdjacentHTML('beforeend', `
    <style>
      .side-nav {
        position: fixed !important;
        left: 0; top: 0; bottom: 0;
        width: 220px; z-index: 200;
        background: #0a0704;
        display: flex; flex-direction: column;
        overflow-y: auto;
      }
      .side-nav-toggle {
        display: none !important;
        position: fixed !important;
        z-index: 201;
      }
      body.with-sidebar { padding-left: 220px; }
      @media (max-width: 768px) {
        body.with-sidebar { padding-left: 0 !important; padding-top: 52px !important; }
        .side-nav { transform: translateX(-100%); transition: transform .28s ease; height: 100vh; }
        .side-nav.open { transform: translateX(0); }
        .side-nav-toggle {
          display: flex !important;
          top: 0; left: 0; right: 0; height: 44px;
          align-items: center; justify-content: space-between;
          padding: 0 1rem;
          background: #0a0704;
          border-bottom: 1px solid rgba(139,26,26,0.2);
        }
      }
    </style>
  `);

  // ─── SIDEBAR HTML ──────────────────────────────────────────────────────────
  document.body.insertAdjacentHTML('afterbegin', `
    <div class="side-nav-toggle">
      <span style="font-family:'Cinzel',serif;font-size:.9rem;color:#8b1a1a;letter-spacing:.1em;">MENU</span>
      <button class="side-nav-close" style="background:none;border:none;color:#b8832a;cursor:pointer;font-size:1.5rem;">&times;</button>
    </div>
    <nav class="side-nav" id="main-sidebar">
      <div style="padding:1.5rem 1rem 1rem;">
        <a href="${root}index.html" style="color:#e8dcc8;text-decoration:none;font-family:'Cinzel',serif;font-size:.8rem;letter-spacing:.1em;text-transform:uppercase;display:block;line-height:1.4;">Shadow of the<br>Dragon Queen</a>
      </div>
      <div style="flex:1;overflow-y:auto;padding:0 .5rem;">
        <a href="${root}unexpected-journeys/index.html" class="nav-link" data-section="unexpected-journeys" style="color:#e8dcc8;text-decoration:none;display:block;padding:.75rem 1rem;font-size:.9rem;border-left:3px solid transparent;transition:all .2s;">Unexpected Journeys</a>
        <a href="${root}the-embers/index.html"          class="nav-link" data-section="the-embers"          style="color:#e8dcc8;text-decoration:none;display:block;padding:.75rem 1rem;font-size:.9rem;border-left:3px solid transparent;transition:all .2s;">The Embers</a>
        <a href="${root}dossiers/index.html"            class="nav-link" data-section="dossiers"            style="color:#e8dcc8;text-decoration:none;display:block;padding:.75rem 1rem;font-size:.9rem;border-left:3px solid transparent;transition:all .2s;">Dossiers</a>
        <a href="${root}war-intel/index.html"           class="nav-link" data-section="war-intel"           style="color:#e8dcc8;text-decoration:none;display:block;padding:.75rem 1rem;font-size:.9rem;border-left:3px solid transparent;transition:all .2s;">War Intel</a>
        <a href="${root}atlas/index.html"               class="nav-link" data-section="atlas"               style="color:#e8dcc8;text-decoration:none;display:block;padding:.75rem 1rem;font-size:.9rem;border-left:3px solid transparent;transition:all .2s;">The Atlas</a>
        <a href="${root}armory/index.html"              class="nav-link" data-section="armory"              style="color:#e8dcc8;text-decoration:none;display:block;padding:.75rem 1rem;font-size:.9rem;border-left:3px solid transparent;transition:all .2s;">Armory</a>
      </div>
      <div style="border-top:1px solid rgba(139,26,26,.2);padding:1rem;">
        <a href="https://rallly.co/invite/D8kMYvewkWxI" target="_blank" class="nav-action-link"
           style="color:#b8832a;text-decoration:none;display:block;padding:.6rem;text-align:center;font-size:.85rem;border:1px solid rgba(184,131,42,.3);transition:all .2s;">
          Schedule Next Session
        </a>
      </div>
    </nav>
  `);

  document.body.classList.add('with-sidebar');

  // ─── ACTIVE LINK ──────────────────────────────────────────────────────────
  var path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(function (link) {
    if (path.includes('/' + link.dataset.section)) {
      link.style.borderLeftColor  = '#8b1a1a';
      link.style.backgroundColor  = 'rgba(139,26,26,.1)';
      link.style.color            = '#b8832a';
    }
  });

  // ─── MOBILE TOGGLE ────────────────────────────────────────────────────────
  var sidebar  = document.getElementById('main-sidebar');
  var toggle   = document.querySelector('.side-nav-toggle');
  var closeBtn = document.querySelector('.side-nav-close');
  toggle  && toggle.addEventListener('click',   function (e) { if (e.target !== closeBtn) sidebar.classList.toggle('open'); });
  closeBtn && closeBtn.addEventListener('click', function ()  { sidebar.classList.remove('open'); });
  document.querySelectorAll('.nav-link,.nav-action-link').forEach(function (l) {
    l.addEventListener('click', function () { sidebar.classList.remove('open'); });
  });

  // ─── HOVER EFFECTS ────────────────────────────────────────────────────────
  document.querySelectorAll('.nav-link').forEach(function (link) {
    link.addEventListener('mouseenter', function () {
      if (!this.style.borderLeftColor || this.style.borderLeftColor === 'transparent')
        this.style.backgroundColor = 'rgba(139,26,26,.08)';
    });
    link.addEventListener('mouseleave', function () {
      if (!this.style.borderLeftColor || this.style.borderLeftColor === 'transparent')
        this.style.backgroundColor = 'transparent';
    });
  });
  document.querySelectorAll('.nav-action-link').forEach(function (link) {
    link.addEventListener('mouseenter', function () { this.style.backgroundColor='rgba(184,131,42,.1)'; this.style.borderColor='rgba(184,131,42,.6)'; });
    link.addEventListener('mouseleave', function () { this.style.backgroundColor='transparent'; this.style.borderColor='rgba(184,131,42,.3)'; });
  });

})();
