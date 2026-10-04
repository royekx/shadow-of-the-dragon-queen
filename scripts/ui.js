/* ════════════════════════════════════════════════════════════════
   ui.js — the interaction shared across the site. Everything here is
   progressive: without JS, tabs render stacked and panels render open,
   which is also why Pagefind can index content that is off screen.

   Wires itself up from data attributes, so no page passes it config.
   ════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  /* ── Tabbed panels ──
     Used by voyage accounts, the quest board, and navigation records.
     Any [data-panel] button drives the panel with the matching id. */
  function initTabs(tabSel, panelSel) {
    var tabs = document.querySelectorAll(tabSel);
    var panels = document.querySelectorAll(panelSel);
    // Both halves are required. The Inventory ledger uses .board-tab to switch
    // a filter rather than a panel, and without this guard that page picked up
    // the panel machinery, got .js-tabs on <html>, and fought its own handler.
    if (!tabs.length || !panels.length) return;
    document.documentElement.classList.add('js-tabs');

    var names = Array.prototype.map.call(tabs, function (t) { return t.dataset.panel; });

    function show(name, push) {
      if (names.indexOf(name) === -1) name = names[0];
      tabs.forEach(function (t) {
        var on = t.dataset.panel === name;
        t.classList.toggle('is-active', on);
        t.setAttribute('aria-selected', on ? 'true' : 'false');
      });
      panels.forEach(function (p) {
        p.classList.toggle('is-active', p.dataset.panel === name);
      });
      if (push && history.replaceState) history.replaceState(null, '', '#' + name);
    }

    tabs.forEach(function (t) {
      t.addEventListener('click', function () { show(t.dataset.panel, true); });
    });

    var hash = location.hash.replace('#', '');
    if (hash) show(hash, false);
    window.addEventListener('hashchange', function () {
      var h = location.hash.replace('#', '');
      if (h) show(h, false);
    });
  }

  initTabs('.account-tab', '.account-panel');
  initTabs('.board-tab', '.board-panel');

  /* ── Expandable rows ──
     A button with aria-controls toggles the element it names. Used by
     the voyage index, the quest board, and the location register. */
  document.querySelectorAll('[aria-controls]').forEach(function (btn) {
    if (!btn.matches('.log-toggle, .ent-row')) return;
    var body = document.getElementById(btn.getAttribute('aria-controls'));
    if (!body) return;
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
      body.hidden = open;
    });
  });

  /* ── Filter pills ──
     Each pill filters siblings carrying the matching data-kind. */
  var pills = document.querySelectorAll('.filter-tag');
  if (pills.length) {
    var targets = document.querySelectorAll('[data-kind]');
    pills.forEach(function (p) {
      p.addEventListener('click', function () {
        var want = p.dataset.filter;
        pills.forEach(function (o) { o.classList.toggle('is-active', o === p); });
        targets.forEach(function (t) {
          t.hidden = !(want === 'all' || t.dataset.kind === want);
        });
      });
    });
  }

  /* ── Sphere chart ──
     Selecting a body on the schematic filters the register to it. The
     list starts complete; "Show all" restores it.

     Only nodes carrying data-body are chart nodes. The register rows mark
     their glyph .ent-glyph.body too, and without this the block bound those
     eight spans, called filterTo(undefined) on a glyph click — hiding every
     entry and labelling the filter "undefined" — and bound "Show all" a
     second time alongside the page's own chart script. */
  var nodes = document.querySelectorAll('.body[data-body]');
  var ents = document.querySelectorAll('.ent');
  if (nodes.length && ents.length) {
    var clearBtn = document.querySelector('.clear-btn');
    var stateLbl = document.querySelector('.filter-state');

    function showAll() {
      nodes.forEach(function (b) { b.classList.remove('is-selected'); });
      ents.forEach(function (e) {
        e.hidden = false;
        e.classList.remove('is-selected');
      });
      if (clearBtn) clearBtn.hidden = true;
      if (stateLbl) stateLbl.textContent = 'Showing all entries';
    }

    function filterTo(name) {
      nodes.forEach(function (b) { b.classList.toggle('is-selected', b.dataset.body === name); });
      ents.forEach(function (e) {
        // Selecting a body narrows the register to it. The entry's own
        // account is already on the row — there is nothing left to expand.
        var on = e.dataset.entry === name;
        e.hidden = !on;
        e.classList.toggle('is-selected', on);
      });
      if (clearBtn) clearBtn.hidden = false;
      if (stateLbl) stateLbl.textContent = name;
    }

    nodes.forEach(function (b) {
      b.addEventListener('click', function () { filterTo(b.dataset.body); });
      b.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); filterTo(b.dataset.body); }
      });
    });
    if (clearBtn) clearBtn.addEventListener('click', showAll);
  }
})();
