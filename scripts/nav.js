// Shadow of the Dragon Queen — Shared Sidebar Navigation Component
// Injects into every subpage (except index.html)
// Detects path depth and builds correct relative paths automatically

(function() {
  // Detect path depth from window.location.pathname
  const pathname = window.location.pathname;
  const pathParts = pathname.split('/').filter(p => p);
  
  // Find repo name in path (shadow-of-the-dragon-queen or similar)
  const repoIndex = pathParts.findIndex(p => p.includes('shadow'));
  const depth = pathParts.length - repoIndex - 1; // How many folders deep are we?
  
  // Build relative path to root based on depth
  let rootPath = '';
  for (let i = 0; i < depth; i++) {
    rootPath += '../';
  }
  
  // Inject critical CSS (positioning only — visual styling in sotdq.css)
  const criticalCSS = `
    <style>
      .side-nav {
        position: fixed !important;
        left: 0;
        top: 0;
        bottom: 0;
        width: 220px;
        z-index: 200;
        background: #0a0704;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
      }
      .side-nav-toggle {
        display: none !important;
        position: fixed !important;
        z-index: 201;
      }
      body.with-sidebar {
        padding-left: 220px;
      }
      @media(max-width: 768px) {
        body.with-sidebar {
          padding-left: 0 !important;
          padding-top: 52px !important;
        }
        .side-nav {
          position: fixed;
          transform: translateX(-100%);
          transition: transform .28s ease;
          height: 100vh;
        }
        .side-nav.open {
          transform: translateX(0);
        }
        .side-nav-toggle {
          display: flex !important;
          top: 0;
          left: 0;
          right: 0;
          height: 44px;
          align-items: center;
          justify-content: space-between;
          padding: 0 1rem;
          background: #0a0704;
          border-bottom: 1px solid rgba(139, 26, 26, 0.2);
        }
      }
    </style>
  `;
  
  // Build sidebar HTML
  const sidebarHTML = `
    <div class="side-nav-toggle">
      <span style="font-family: 'Cinzel', serif; font-size: 0.9rem; color: #8b1a1a; letter-spacing: 0.1em;">MENU</span>
      <button class="side-nav-close" style="background: none; border: none; color: #b8832a; cursor: pointer; font-size: 1.5rem;">&times;</button>
    </div>
    <nav class="side-nav" id="main-sidebar">
      <div style="padding: 1.5rem 1rem;">
        <a href="${rootPath}index.html" style="color: #e8dcc8; text-decoration: none; font-family: 'Cinzel', serif; font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase; display: block; margin-bottom: 0.5rem;">Shadow of the Dragon Queen</a>
      </div>
      
      <div style="flex: 1; overflow-y: auto;">
        <div style="padding: 0 0.5rem;">
          <a href="${rootPath}unexpected-journeys/index.html" class="nav-link" data-section="unexpected-journeys" style="color: #e8dcc8; text-decoration: none; display: block; padding: 0.8rem 1rem; font-size: 0.9rem; border-left: 3px solid transparent; transition: all 0.2s;">Unexpected Journeys</a>
          <a href="${rootPath}the-embers/index.html" class="nav-link" data-section="the-embers" style="color: #e8dcc8; text-decoration: none; display: block; padding: 0.8rem 1rem; font-size: 0.9rem; border-left: 3px solid transparent; transition: all 0.2s;">The Embers</a>
          <a href="${rootPath}war-intel/index.html" class="nav-link" data-section="war-intel" style="color: #e8dcc8; text-decoration: none; display: block; padding: 0.8rem 1rem; font-size: 0.9rem; border-left: 3px solid transparent; transition: all 0.2s;">War Intel</a>
          <a href="${rootPath}theatre-of-war/index.html" class="nav-link" data-section="theatre-of-war" style="color: #e8dcc8; text-decoration: none; display: block; padding: 0.8rem 1rem; font-size: 0.9rem; border-left: 3px solid transparent; transition: all 0.2s;">Theatre of War</a>
          <a href="${rootPath}armory/index.html" class="nav-link" data-section="armory" style="color: #e8dcc8; text-decoration: none; display: block; padding: 0.8rem 1rem; font-size: 0.9rem; border-left: 3px solid transparent; transition: all 0.2s;">Armory</a>
          <a href="${rootPath}field-manual/index.html" class="nav-link" data-section="field-manual" style="color: #e8dcc8; text-decoration: none; display: block; padding: 0.8rem 1rem; font-size: 0.9rem; border-left: 3px solid transparent; transition: all 0.2s;">Field Manual</a>
        </div>
      </div>
      
      <div style="border-top: 1px solid rgba(139, 26, 26, 0.2); padding: 1rem;">
        <a href="https://royek.foundryserver.com/game" target="_blank" class="nav-action-link" style="color: #b8832a; text-decoration: none; display: block; padding: 0.6rem; text-align: center; font-size: 0.85rem; border: 1px solid rgba(184, 131, 42, 0.3); margin-bottom: 0.5rem; transition: all 0.2s;">Take the Helm</a>
        <a href="https://rallly.co/invite/D8kMYvewkWxI" target="_blank" class="nav-action-link" style="color: #b8832a; text-decoration: none; display: block; padding: 0.6rem; text-align: center; font-size: 0.85rem; border: 1px solid rgba(184, 131, 42, 0.3); transition: all 0.2s;">Plot the Next</a>
      </div>
    </nav>
  `;
  
  // Insert critical CSS into head
  document.head.insertAdjacentHTML('beforeend', criticalCSS);
  
  // Insert sidebar HTML at beginning of body
  document.body.insertAdjacentHTML('afterbegin', sidebarHTML);
  
  // Add sidebar class to body
  document.body.classList.add('with-sidebar');
  
  // Highlight active link based on current path
  function highlightActiveLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      const resolvedHref = new URL(href, window.location.href).pathname;
      
      if (currentPath.includes(link.dataset.section)) {
        link.style.borderLeftColor = '#8b1a1a';
        link.style.backgroundColor = 'rgba(139, 26, 26, 0.1)';
        link.style.color = '#b8832a';
      } else {
        link.style.borderLeftColor = 'transparent';
        link.style.backgroundColor = 'transparent';
        link.style.color = '#e8dcc8';
      }
    });
  }
  
  // Mobile toggle functionality
  const toggle = document.querySelector('.side-nav-toggle');
  const sidebar = document.querySelector('.side-nav');
  const closeBtn = document.querySelector('.side-nav-close');
  
  if (toggle) {
    toggle.addEventListener('click', (e) => {
      if (e.target !== closeBtn) {
        sidebar.classList.toggle('open');
      }
    });
  }
  
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      sidebar.classList.remove('open');
    });
  }
  
  // Close sidebar when clicking a link
  document.querySelectorAll('.nav-link, .nav-action-link').forEach(link => {
    link.addEventListener('click', () => {
      sidebar.classList.remove('open');
    });
  });
  
  // Highlight active on load
  highlightActiveLink();
  
  // Add hover effects
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('mouseenter', function() {
      if (!this.style.borderLeftColor || this.style.borderLeftColor === 'transparent') {
        this.style.backgroundColor = 'rgba(139, 26, 26, 0.08)';
      }
    });
    link.addEventListener('mouseleave', function() {
      if (!this.style.borderLeftColor || this.style.borderLeftColor === 'transparent') {
        this.style.backgroundColor = 'transparent';
      }
    });
  });
  
  document.querySelectorAll('.nav-action-link').forEach(link => {
    link.addEventListener('mouseenter', function() {
      this.style.backgroundColor = 'rgba(184, 131, 42, 0.1)';
      this.style.borderColor = 'rgba(184, 131, 42, 0.6)';
    });
    link.addEventListener('mouseleave', function() {
      this.style.backgroundColor = 'transparent';
      this.style.borderColor = 'rgba(184, 131, 42, 0.3)';
    });
  });
})();
