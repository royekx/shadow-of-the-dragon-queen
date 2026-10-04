/**
 * Shadow of the Dragon Queen - Shared Navigation
 * ----------------------------------------------
 * Injects the sidebar and the command bar into any page that loads this
 * script. To change the nav for every page, edit only this file.
 *
 * Usage (in <head>, with defer, after data/standing.js):
 *   <script src="../data/standing.js" defer></script>
 *   <script src="../scripts/nav.js" defer></script>
 *
 * Structure follows the Caelestis nav.js. Two differences:
 *   - the site root is read from this script's own URL, so the site works
 *     at any path (GitHub Pages subfolder, a custom domain, a local server)
 *   - the command bar carries one outside link (the scheduler) and one
 *     inside link (the latest journey) instead of two outside links
 */

(function () {
  'use strict';

  // -- Site root -----------------------------------------------------------
  // This file lives at <root>/scripts/nav.js, so the root is two segments up
  // from its own address. Every link below is built from it.
  var me = document.currentScript ||
           document.querySelector('script[src$="scripts/nav.js"]');
  var base = me ? me.src.replace(/scripts\/nav\.js(\?.*)?$/, '') : './';
  var pathname = window.location.pathname;

  // -- Icons ---------------------------------------------------------------

  var EXT_ICON = '<svg viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 2H2a1 1 0 00-1 1v5a1 1 0 001 1h5a1 1 0 001-1V6M6 1h3v3M9 1L4.5 5.5"/></svg>';
  var GO_ICON = '<svg viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1.5 5h7M6 2.5L8.5 5 6 7.5"/></svg>';
  var MENU_ICON = '<svg viewBox="0 0 18 14" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><line x1="0" y1="1" x2="18" y2="1"/><line x1="0" y1="7" x2="18" y2="7"/><line x1="0" y1="13" x2="18" y2="13"/></svg>';
  var SEARCH_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.5-4.5"/></svg>';
  var CARET = '<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 4l4 4 4-4"/></svg>';

  var SCHEDULER = 'https://rallly.co/invite/D8kMYvewkWxI';

  // -- Sections ------------------------------------------------------------
  // To add, remove, or rename a section: edit this array only.
  //
  //   Muster       - what you do to get the next session on the table
  //   The Company  - what this party has done, met, found and carries
  //   The War      - the wider world, and the search across all of it
  //
  // An item with `href` is external and opens in a new tab; one with `path`
  // is internal and resolves against the site root.

  var groups = [
    {
      label: 'Muster',
      items: [
        { key: 'road-so-far', label: 'The Road So Far', path: 'road-so-far/index.html' },
        { label: 'Schedule Next Session', href: SCHEDULER }
      ]
    },
    {
      label: 'The Company',
      items: [
        { key: 'unexpected-journeys', label: 'Unexpected Journeys', path: 'unexpected-journeys/index.html' },
        { key: 'quests',              label: 'Quest Board',         path: 'quests/index.html'              },
        { key: 'the-embers',          label: 'The Embers',          path: 'the-embers/index.html'          },
        { key: 'dossiers',            label: 'Dossiers',            path: 'dossiers/index.html'            },
        { key: 'atlas',               label: 'The Atlas',           path: 'atlas/index.html'               },
        { key: 'armory',              label: 'Armory',              path: 'armory/index.html'              }
      ]
    },
    {
      label: 'The War',
      items: [
        { key: 'war-intel', label: 'War Intel',        path: 'war-intel/index.html' },
        { key: 'search',    label: 'Search the Record', path: 'search/index.html'    }
      ]
    }
  ];

  // -- Command bar ---------------------------------------------------------
  // Sits at the top of every page: search, two operations, then where the
  // party stands. The strip trims with an ellipsis by design; the caret opens
  // the detail it had to cut.
  //
  // Data comes from data/standing.js. Without that file the bar renders
  // search and the scheduler only, and nothing breaks.

  function buildCommandBar() {
    var s = window.SOTDQ_STANDING;
    var L = (s && s.links) || {};
    var pad = function (n) { return ('00' + n).slice(-3); };

    var search =
      '<form class="cb-search" id="js-cb-search" role="search" autocomplete="off">' +
        '<button type="submit" class="cb-search-go" aria-label="Search">' + SEARCH_ICON + '</button>' +
        '<input type="text" id="js-cb-search-input" ' +
          'placeholder="Search the record — a name, a place, a thing you half remember…" ' +
          'aria-label="Search all records">' +
        '<button type="submit" class="cb-search-tag">Search</button>' +
      '</form>';

    var sched = L.scheduler || SCHEDULER;
    var latest = s
      ? '<a class="cb-op" href="' + base + (L.journey || 'unexpected-journeys/index.html') + '">' +
          '<span class="cb-op-name">Latest Journey</span>' +
          '<span class="cb-op-note">' + pad(s.journey) + ' · ' + s.title + '</span>' + GO_ICON +
        '</a>'
      : '<a class="cb-op" href="' + base + 'unexpected-journeys/index.html">' +
          '<span class="cb-op-name">Unexpected Journeys</span>' +
          '<span class="cb-op-note">Every session on record</span>' + GO_ICON +
        '</a>';

    var ops =
      '<div class="cb-ops">' +
        latest +
        '<a class="cb-op" href="' + sched + '" target="_blank" rel="noopener">' +
          '<span class="cb-op-name">Schedule Next Session</span>' +
          '<span class="cb-op-note">Open Rallly</span>' + EXT_ICON +
        '</a>' +
      '</div>';

    if (!s) return '<div class="command-bar">' + search + ops + '</div>';

    var road = base + (L.standing || 'road-so-far/index.html');
    var strip =
      '<div class="cb-strip">' +
        '<a class="cb-face" href="' + road + '">' +
          '<span class="cb-label">Where We Stand</span>' +
          '<span class="cb-cell"><span class="cb-key">Position</span>' +
            '<span class="cb-val">' + s.position +
            (s.posNote ? ' <span class="cb-note">' + s.posNote + '</span>' : '') + '</span></span>' +
          '<span class="cb-cell"><span class="cb-key">As Of</span>' +
            '<span class="cb-val">Journey ' + pad(s.journey) + '</span></span>' +
          '<span class="cb-cell"><span class="cb-key">Outstanding</span>' +
            '<span class="cb-val">' + s.outstanding + '</span></span>' +
        '</a>' +
        '<button class="cb-expand" id="js-cb-expand" aria-expanded="false" aria-controls="js-cb-detail" aria-label="More detail">' +
          CARET + '</button>' +
      '</div>';

    var d = s.detail || {};
    var quests = (d.quests || []).map(function (q) {
      return '<a class="cb-quest" href="' + base + q.href + '">' + q.name +
             (q.progress ? '<span class="cb-prog">' + q.progress + '</span>' : '') + '</a>';
    }).join('');
    var met = (d.met || []).map(function (m) {
      return '<a class="cb-chip" href="' + base + m.href + '">' + m.name + '</a>';
    }).join('');

    var detail =
      '<div class="cb-detail" id="js-cb-detail" hidden>' +
        (d.consequence ? '<p class="cb-conseq">' + d.consequence + '</p>' : '') +
        (quests ? '<div class="cb-row"><span class="cb-key">Quests</span><div class="cb-quests">' + quests + '</div></div>' : '') +
        (met ? '<div class="cb-row"><span class="cb-key">Faces</span><div class="cb-chips">' + met + '</div></div>' : '') +
        '<a class="cb-more" href="' + road + '">The road so far, in full ›</a>' +
      '</div>';

    return '<div class="command-bar">' + search + ops + strip + detail + '</div>';
  }

  // -- Critical positioning CSS (does not depend on stylesheet load order) --

  var criticalCSS = [
    '.side-nav{position:fixed!important;left:0;top:0;bottom:0;width:244px;z-index:200;',
    'display:flex;flex-direction:column;overflow-y:auto;',
    'background:rgba(8,5,3,0.99);border-right:1px solid rgba(201,150,63,0.15);}',
    '.side-nav-toggle{display:none!important;position:fixed!important;z-index:201;}',
    'body.with-sidebar{padding-left:244px;}',
    '@media(max-width:768px){',
    'body.with-sidebar{padding-left:0!important;padding-top:52px!important;}',
    '.side-nav{transform:translateX(-100%);transition:transform .28s ease;}',
    '.side-nav.open{transform:translateX(0);}',
    '.side-nav-toggle{display:flex!important;top:0;left:0;right:0;height:44px;}',
    '}'
  ].join('');

  var styleEl = document.createElement('style');
  styleEl.textContent = criticalCSS;
  document.head.appendChild(styleEl);

  // -- Build sidebar -------------------------------------------------------

  var sectionLinks = groups.map(function (g) {
    var links = g.items.map(function (s) {
      if (s.href) {
        return '<a class="side-nav-ext-link" href="' + s.href + '" target="_blank" rel="noopener">' +
               s.label + ' ' + EXT_ICON + '</a>';
      }
      return '<a class="side-nav-link" href="' + base + s.path + '" data-section="' + s.key + '">' +
             s.label + '</a>';
    }).join('');
    return '<div class="side-nav-group-label">' + g.label + '</div>' + links;
  }).join('');

  var html = [
    '<button class="side-nav-toggle" id="js-nav-toggle" aria-label="Toggle navigation">',
    MENU_ICON,
    '<span class="side-nav-toggle-label">Dragon Queen</span>',
    '</button>',
    '<nav class="side-nav" id="js-side-nav">',
    '  <div class="side-nav-head">',
    '    <a class="side-nav-logo" href="' + base + 'hub.html">Shadow of the<br>Dragon Queen</a>',
    '    <a class="side-nav-hub" href="' + base + 'hub.html">Command Post</a>',
    '  </div>',
    '  <div class="side-nav-body">',
    sectionLinks,
    '  </div>',
    '</nav>'
  ].join('');

  // -- Inject --------------------------------------------------------------

  document.body.insertAdjacentHTML('afterbegin', html);
  document.body.classList.add('with-sidebar');

  // The bar is chrome, not page material, so on a normal page it goes BEFORE
  // .content and sits on the backdrop rather than on the content scrim. On
  // the hub the column is .hub and the bar goes under the title. The search
  // page names its column .terminal-wrap.
  var head = document.querySelector('.hub-head');
  var col = document.querySelector('.content');
  var term = document.querySelector('.terminal-wrap');
  if (head) {
    head.insertAdjacentHTML('afterend', buildCommandBar());
  } else if (col) {
    col.insertAdjacentHTML('beforebegin', buildCommandBar());
  } else if (term) {
    term.insertAdjacentHTML('afterbegin', buildCommandBar());
  } else {
    document.body.insertAdjacentHTML('afterbegin', buildCommandBar());
  }

  var cbBtn = document.getElementById('js-cb-expand');
  if (cbBtn) {
    cbBtn.addEventListener('click', function () {
      var panel = document.getElementById('js-cb-detail');
      var open = cbBtn.getAttribute('aria-expanded') === 'true';
      cbBtn.setAttribute('aria-expanded', open ? 'false' : 'true');
      panel.hidden = open;
    });
  }

  // -- Active state --------------------------------------------------------

  document.querySelectorAll('.side-nav-link[data-section]').forEach(function (link) {
    if (pathname.indexOf('/' + link.dataset.section + '/') !== -1) {
      link.classList.add('active');
    }
  });

  // -- Mobile toggle -------------------------------------------------------

  var toggle = document.getElementById('js-nav-toggle');
  var nav    = document.getElementById('js-side-nav');

  if (toggle && nav) {
    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      nav.classList.toggle('open');
    });
    document.addEventListener('click', function (e) {
      if (nav.classList.contains('open') && !nav.contains(e.target)) {
        nav.classList.remove('open');
      }
    });
    nav.querySelectorAll('.side-nav-link').forEach(function (link) {
      link.addEventListener('click', function () { nav.classList.remove('open'); });
    });
  }

  // -- Global search field -------------------------------------------------
  // Submitting jumps to the search page with the query already run.

  var searchForm  = document.getElementById('js-cb-search');
  var searchInput = document.getElementById('js-cb-search-input');
  if (searchForm && searchInput) {
    searchForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var term = searchInput.value.trim();
      window.location.href = base + 'search/index.html' +
        (term ? '?q=' + encodeURIComponent(term) : '');
    });
  }

  // -- Portrait lightbox ---------------------------------------------------
  // Any .portrait-frame containing an image becomes click-to-expand, on every
  // page that loads this script. Frames still showing a monogram are skipped
  // and pick the behaviour up the day an image is dropped in.

  (function () {
    var frames = document.querySelectorAll('.portrait-frame');
    var targets = [];

    frames.forEach(function (frame) {
      var img = frame.querySelector('img');
      if (!img) return;
      if (frame.hasAttribute('onclick')) return;
      if (frame.classList.contains('map-thumb')) return;
      targets.push({ frame: frame, img: img });
    });

    // Maps, handouts and any other standing image expand the same way.
    document.querySelectorAll('.survey, .expandable, figure.plate').forEach(function (frame) {
      var img = frame.querySelector('img');
      if (!img || frame.hasAttribute('onclick')) return;
      frame.classList.add('is-expandable');
      targets.push({ frame: frame, img: img });
    });

    if (!targets.length) return;

    var box = document.createElement('div');
    box.className = 'cae-lightbox';
    box.innerHTML =
      '<button class="cae-lightbox-close" type="button" aria-label="Close">Close ✕</button>' +
      '<img alt="">';
    document.body.appendChild(box);

    var boxImg = box.querySelector('img');

    // Drive serves thumbnails small by default; ask for a wide render instead.
    function fullSize(src) {
      if (src.indexOf('googleusercontent.com') === -1) return src;
      return src.replace(/=[swh]\d+.*$/, '') + '=w1600';
    }

    function open(t) {
      boxImg.src = fullSize(t.img.getAttribute('src'));
      boxImg.alt = t.img.getAttribute('alt') || '';
      box.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    function close() {
      box.classList.remove('open');
      document.body.style.overflow = '';
    }

    targets.forEach(function (t) {
      t.frame.classList.add('cae-expandable');
      t.frame.setAttribute('role', 'button');
      t.frame.setAttribute('tabindex', '0');
      t.frame.setAttribute('aria-label', 'Expand ' + (t.img.getAttribute('alt') || 'image'));
      t.frame.addEventListener('click', function () { open(t); });
      t.frame.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(t); }
      });

      if (!t.frame.nextElementSibling ||
          !t.frame.nextElementSibling.classList.contains('portrait-label')) {
        var label = document.createElement('div');
        label.className = 'portrait-label';
        label.setAttribute('data-pagefind-ignore', '');
        label.textContent = 'Tap to Expand';
        t.frame.parentNode.insertBefore(label, t.frame.nextSibling);
      }
    });

    box.addEventListener('click', function (e) { if (e.target !== boxImg) close(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && box.classList.contains('open')) close();
    });
  })();

})();
