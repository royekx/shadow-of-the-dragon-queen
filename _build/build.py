#!/usr/bin/env python3
"""
build.py - write every page of the site from the campaign data.

    python3 _build/build.py

Reads  : _build/campaign_people.py, _build/campaign_world.py
         _build/campaign_guests.py
         _build/journeys/NNN.brief.html, NNN.full.html
Writes : every .html page, data/standing.js, data/journeys.js,
         data/vocabulary.js

The pages are plain static HTML and are committed. Nothing runs this on
deploy: the GitHub Action only builds the search index and publishes. Run it
by hand after editing the data, then commit what changed.

To add a session:
  1. write _build/journeys/012.brief.html and 012.full.html
  2. add the JOURNEYS entry in campaign_world.py
  3. add a "12:" line under `records` for anyone and anything it touched,
     and bump their `last`
  4. update QUESTS and STANDING
  5. run this, look at the result, commit

Markup follows the Caelestis site so its stylesheets apply unchanged.
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from campaign_people import PCS, NPCS, UNFILED, AFF_LABELS, MET_LABELS   # noqa: E402
from campaign_world import (CAMPAIGN, JOURNEYS, REGIONS, ATLAS_MAP, PLACES, PLACES_UNLINKED,  # noqa: E402
                            ITEMS, ITEM_TABS, FACTIONS, FACTION_BANDS, QUESTS, STANDING, EXTRA_VOCAB)
from campaign_guests import GUEST_PAGES   # noqa: E402

SITE = CAMPAIGN['title']
written = []

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def e(s):
    return html.escape(str(s), quote=True)


def pad(n):
    return '%03d' % int(n)


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def rel(path):
    """Prefix that takes a page at `path` back to the site root."""
    depth = path.count('/')
    return '../' * depth


def write(path, text):
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding='utf-8')
    written.append(path)


# -- registry: every record addressable as "kind:slug" ----------------------

DIRS = {'pc': 'the-embers', 'npc': 'dossiers', 'item': 'armory', 'place': 'atlas',
        'fac': 'war-intel', 'quest': 'quests'}
SECTION_LABELS = {
    'unexpected-journeys': 'Unexpected Journeys', 'quests': 'Quest Board', 'the-embers': 'The Embers',
    'dossiers': 'Dossiers', 'atlas': 'The Atlas', 'armory': 'Armory', 'war-intel': 'War Intel',
    'road-so-far': 'The Road So Far',
}

REG = {}
for kind, rows in (('pc', PCS), ('npc', NPCS), ('item', ITEMS), ('place', PLACES),
                   ('fac', FACTIONS), ('quest', QUESTS)):
    for r in rows:
        r['kind_'] = kind
        r['ref'] = '%s:%s' % (kind, r['slug'])
        assert r['ref'] not in REG, 'duplicate ' + r['ref']
        REG[r['ref']] = r


def get(ref):
    assert ref in REG, 'unknown reference: ' + ref
    return REG[ref]


def url(ref):
    r = get(ref)
    return '%s/%s.html' % (DIRS[r['kind_']], r['slug'])


def label(ref):
    r = get(ref)
    return r.get('short') or r['name']


# back-links: if A lists B, B lists A
for r in list(REG.values()):
    for t in r.get('links', []):
        get(t)
LINKS = {ref: list(r.get('links', [])) for ref, r in REG.items()}
for ref, r in REG.items():
    for t in r.get('links', []):
        if ref not in LINKS[t]:
            LINKS[t].append(ref)
    for extra in ('giver', 'holder_ref'):
        t = r.get(extra)
        if t:
            if t not in LINKS[ref]:
                LINKS[ref].append(t)
            if ref not in LINKS[t]:
                LINKS[t].append(ref)
    if r.get('parent'):
        p = 'quest:' + r['parent']
        for a, b in ((ref, p), (p, ref)):
            if b not in LINKS[a]:
                LINKS[a].append(b)

JBY = {j['num']: j for j in JOURNEYS}
LATEST = max(JBY)

# ---------------------------------------------------------------------------
# shared fragments
# ---------------------------------------------------------------------------

EMBLEM = ('<svg viewBox="0 0 120 40" fill="none" stroke="currentColor" stroke-width="1" '
          'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
          '<line x1="0" y1="20" x2="42" y2="20" stroke-width="0.6" opacity="0.4"/>'
          '<polyline points="38,15 43,20 38,25" opacity="0.5"/>'
          '<polyline points="33,16 38,20 33,24" opacity="0.3"/>'
          '<g transform="translate(60,21)">'
          '<path d="M0,-15 C1.5,-9 8,-6 8,2 A8,8 0 0 1 -8,2 C-8,-2 -5.5,-4 -4.5,-8 C-2.5,-6.5 -1,-9 0,-15 Z"/>'
          '<path d="M0,-3 C1,-0.5 3,1 3,4 A3,3 0 0 1 -3,4 C-3,1.5 -1,0.5 0,-3 Z" fill="currentColor" stroke="none" opacity="0.75"/>'
          '</g>'
          '<polyline points="82,15 77,20 82,25" opacity="0.3"/>'
          '<polyline points="87,16 82,20 87,24" opacity="0.5"/>'
          '<line x1="78" y1="20" x2="120" y2="20" stroke-width="0.6" opacity="0.4"/>'
          '</svg>')
LEFT = '<svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M9 2L4 7l5 5"/></svg>'
RIGHT = '<svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5 2l5 5-5 5"/></svg>'
CHECK = '<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 6.5l2.5 2.5 4.5-5.5"/></svg>'
DIVIDER = '<div class="divider" data-pagefind-ignore>&#10022; &#10022; &#10022;</div>'

SHEETS = {
    'entity':  ['base', 'entity', 'board', 'register'],
    'listing': ['base', 'entity', 'board', 'register'],
    'journey': ['base', 'board', 'register', 'journey'],
    'jindex':  ['base', 'board', 'register'],
    'road':    ['base', 'entity', 'board', 'standing'],
    'search':  ['base'],
    'hub':     ['base', 'hub'],
    'guest':   ['base', 'board', 'register', 'journey'],
}
SCRIPTS = {
    'entity': ['scripts/ui.js'], 'listing': ['scripts/ui.js'], 'journey': ['scripts/ui.js'],
    'jindex': ['scripts/ui.js'], 'road': ['scripts/ui.js'], 'search': [],
    'hub': ['data/journeys.js'], 'guest': ['scripts/ui.js'],
}


def head(path, title, kind, extra_head='', nav=True):
    # nav=False leaves out the sidebar and the command bar (see build_guests).
    r = rel(path)
    css = ''.join('<link rel="stylesheet" href="%sstyles/%s.css">\n' % (r, s) for s in SHEETS[kind] + ['site'])
    js = ''.join('<script src="%s%s" defer></script>\n' % (r, s)
                 for s in (['data/standing.js', 'scripts/nav.js'] if nav else []) + SCRIPTS[kind])
    full = title if title == SITE else '%s &middot; %s' % (e(title), SITE)
    return ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            '<title>%s</title>\n%s%s%s</head>\n' % (full, css, js, extra_head))


def page(path, title, kind, section, content, eyebrow=None, subtitle=None, tail='', hero=None,
         body_class=None, nav=True):
    # hero: markup that takes the emblem's place at the top of the header.
    # body_class: a hook for site.css rules that belong to one kind of page.
    hdr = ['<div class="page-header">',
           hero or '  <div class="page-emblem" data-pagefind-ignore>%s</div>' % EMBLEM]
    if eyebrow:
        hdr.append('  <div class="page-eyebrow">%s</div>' % e(eyebrow))
    hdr.append('  <h1 class="page-title" data-pagefind-meta="title">%s</h1>' % e(title))
    if subtitle:
        hdr.append('  <div class="page-subtitle">%s</div>' % e(subtitle))
    hdr.append('</div>')
    cls = ' class="%s"' % body_class if body_class else ''
    body = ('<body%s data-pagefind-filter="section:%s">\n<div class="page-content">\n%s\n'
            '<div class="content">\n%s\n</div>\n</div>\n%s</body>\n</html>\n'
            % (cls, section, '\n'.join(hdr), content, tail))
    write(path, head(path, title, kind, nav=nav) + body)


def chip(ref, r, text=None):
    """A chip linking to a record. r = prefix back to the site root."""
    rec = get(ref)
    cls = {'pc': 'chip', 'npc': 'chip chip-npc', 'item': 'chip chip-item', 'place': 'chip chip-place',
           'fac': 'chip chip-place', 'quest': 'chip chip-quest'}[rec['kind_']]
    return '<a class="%s" href="%s%s">%s</a>' % (cls, r, url(ref), e(text or label(ref)))


def glance_chip(text, ref, r, cls):
    if ref:
        return '<a class="%s" href="%s%s">%s</a>' % (cls, r, url(ref), e(text))
    return '<span class="%s">%s</span>' % (cls, e(text))


def nav_bar(prev, centre, nxt, bottom=False):
    """prev / nxt are (href, label) or None; centre is (href, label)."""
    def side(x, left):
        if not x:
            return '<span class="voyage-nav-link disabled"></span>'
        inner = ('%s <span class="nav-label">%s</span>' if left else '<span class="nav-label">%s</span> %s')
        inner = inner % ((LEFT, e(x[1])) if left else (e(x[1]), RIGHT))
        return '<a class="voyage-nav-link" href="%s">%s</a>' % (x[0], inner)
    return ('<div class="%s" data-pagefind-ignore>%s<a class="voyage-nav-center" href="%s">%s</a>%s</div>'
            % ('voyage-nav-bottom' if bottom else 'voyage-nav-bar', side(prev, True),
               centre[0], e(centre[1]), side(nxt, False)))


def chain(rows, i, centre):
    prev = rows[i - 1] if i > 0 else rows[-1]
    nxt = rows[i + 1] if i < len(rows) - 1 else rows[0]
    if len(rows) < 2:
        return nav_bar(None, centre, None)
    return nav_bar((prev['slug'] + '.html', prev.get('short') or prev['name']), centre,
                   (nxt['slug'] + '.html', nxt.get('short') or nxt['name']))


def stat_rows(pairs):
    out = []
    for k, v in pairs:
        if v is None or v == '':
            continue
        long_ = ' stat-val-long' if len(str(v)) > 26 else ''
        out.append('<div class="stat-row"><span class="stat-key">%s</span> '
                   '<span class="stat-val%s">%s</span></div>' % (e(k), long_, e(v)))
    return '<div class="stat-card">%s</div>' % ''.join(out)


def portrait(rec):
    if rec.get('portrait'):
        return ('<div class="portrait-frame"><img src="%s" alt="%s" loading="lazy"></div>'
                % (rec['portrait'], e(rec['name'])))
    return '<div class="portrait-frame"><span class="monogram" data-pagefind-ignore>%s</span></div>' % e(mono(rec['name']))


def mono(name):
    name = re.sub(r'^(The|Lord|Sir|Mayor|Marshal|Governor)\s+', '', name)
    return name[0].upper()


def face(rec):
    if rec.get('portrait'):
        return ('<span class="ent-face"><img src="%s" alt="" loading="lazy" '
                'onerror="this.parentNode.innerHTML=\'&lt;span class=&quot;face-mono&quot;&gt;%s&lt;/span&gt;\'"></span>'
                % (rec['portrait'], e(mono(rec['name']))))
    return '<span class="ent-face"><span class="face-mono" data-pagefind-ignore>%s</span></span>' % e(mono(rec['name']))


def records_block(rec, r):
    recs = rec.get('records') or {}
    if not recs:
        return ''
    nums = sorted(recs, reverse=True)

    def block(n):
        items = ''.join('<li>%s</li>' % e(x) for x in recs[n])
        return ('<div class="record-block"><div class="record-head">'
                '<a class="record-voyage" href="%sunexpected-journeys/journey-%s.html">Journey %s</a></div>'
                '<ul class="record-list">%s</ul></div>' % (r, pad(n), pad(n), items))
    out = [block(nums[0])]
    if len(nums) > 1:
        keys = ' &middot; '.join(pad(n) for n in sorted(nums[1:]))
        out.append('<details class="prior"><summary>Previous Journeys <span class="prior-keys">%s</span></summary>'
                   '<div class="prior-body">%s</div></details>' % (keys, ''.join(block(n) for n in nums[1:])))
    return DIVIDER + '\n' + '\n'.join(out)


XREF_ORDER = [('quest', 'Quests'), ('pc', 'The Embers'), ('npc', 'Characters'), ('item', 'Items'),
              ('place', 'Places'), ('fac', 'War Intel')]


def connections(ref, r, skip=()):
    cols = []
    for kind, title in XREF_ORDER:
        refs = [t for t in LINKS[ref] if t.startswith(kind + ':') and t not in skip]
        if not refs:
            continue
        refs.sort(key=lambda t: label(t))
        cols.append('<div class="xref-col"><div class="xref-col-head">%s</div>%s</div>'
                    % (title, ''.join(chip(t, r) for t in refs)))
    if not cols:
        return ''
    return ('<div class="xref-card"><div class="xref-head"><span class="xref-title">Connections</span></div>'
            '<div class="xref-cols">%s</div></div>' % ''.join(cols))


def last_seen(rec):
    if rec.get('last') is None:
        return rec.get('last_note', 'Unseen')
    return 'Journey ' + pad(rec['last'])


def paras(x):
    if isinstance(x, str):
        x = [x]
    return ''.join('<p>%s</p>' % e(p) for p in x)


def sheet_link(rec):
    """A party member's own character sheet, when one is on file."""
    if not rec.get('sheet'):
        return ''
    return ('<a class="sheet-link" href="%s" target="_blank" rel="noopener" data-pagefind-ignore>'
            'Character sheet <span>D&amp;D Beyond &#8599;</span></a>' % rec['sheet'])


def entity_page(rec, section, centre_label, stats, sub, bar, extra_top='', extra_mid='',
                conn_first=False):
    path = '%s/%s.html' % (DIRS[rec['kind_']], rec['slug'])
    r = rel(path)
    info = ['<div class="entry-name">%s</div>' % e(rec['name'])]
    if sub:
        info.append('<div class="entry-sub">%s</div>' % e(sub))
    info.append('<div class="entry-body">%s</div>' % paras(rec['overview']))
    if rec.get('pursuit'):
        info.append('<div class="pursuit"><span class="pursuit-label">Pursuit</span>'
                    '<span class="pursuit-text">%s</span></div>' % e(rec['pursuit']))
    if rec.get('state'):
        info.append('<div class="pursuit"><span class="pursuit-label">Now</span>'
                    '<span class="pursuit-text">%s</span></div>' % e(rec['state']))
    conn = connections(rec['ref'], r)
    parts = [bar, extra_top,
             '<div class="entry-header">\n  <div class="identity-card">%s%s</div>\n'
             '  <div class="entry-info">%s</div>\n</div>' % (portrait(rec), stat_rows(stats) + sheet_link(rec), ''.join(info)),
             extra_mid]
    if conn_first and conn:
        parts.append(conn)
    parts.append(records_block(rec, r))
    if not conn_first and conn:
        parts.append(DIVIDER + conn)
    page(path, rec['name'], 'entity', section, '\n'.join(p for p in parts if p))


def facet(label_, pills, stacked=False):
    return ('<div class="facet%s"><span class="facet-label">%s</span><div class="facet-pills">%s</div></div>'
            % (' facet-stacked' if stacked else '', e(label_), ''.join(pills)))


def pill(attr, value, text):
    return '<button class="filter-tag" type="button" data-%s="%s">%s</button>' % (attr, e(value), e(text))


# Two-axis register filter, one value per axis, plus a name search. The same
# logic Caelestis uses on its Dossiers page, written once for every register.
FILTER_JS = """<script>
// Runs at DOMContentLoaded so its click handlers are bound after ui.js's
// generic .filter-tag handler and get the last word on which pills are lit.
document.addEventListener('DOMContentLoaded', function () {
  'use strict';
  var AXES = %s;
  var NOUN = %s;
  var rows   = Array.prototype.slice.call(document.querySelectorAll('.register .ent'));
  var pills  = Array.prototype.slice.call(document.querySelectorAll('.filter-tag'));
  var tabs   = Array.prototype.slice.call(document.querySelectorAll('.board-tab[data-class]'));
  var search = document.querySelector('.search-input');
  var count  = document.querySelector('.result-count');
  var none   = document.querySelector('.no-results');
  var clear  = document.querySelector('.clear-btn');
  var state  = { q: '', cls: 'all' };
  AXES.forEach(function (a) { state[a] = null; });

  function axisOf(p) { for (var i = 0; i < AXES.length; i++) { if (p.dataset[AXES[i]] !== undefined) return AXES[i]; } }
  function has(el, axis, val) { return (el.dataset[axis] || '').split(' ').indexOf(val) !== -1; }

  function apply() {
    var n = 0;
    rows.forEach(function (r) {
      var ok = (state.cls === 'all' || has(r, 'class', state.cls)) &&
               (!state.q || (r.dataset.name || '').indexOf(state.q) !== -1);
      AXES.forEach(function (a) { if (ok && state[a] && !has(r, a, state[a])) ok = false; });
      r.hidden = !ok;
      if (ok) n++;
    });
    pills.forEach(function (p) { var a = axisOf(p); p.classList.toggle('is-active', state[a] === p.dataset[a]); });
    tabs.forEach(function (t) { t.classList.toggle('is-active', t.dataset['class'] === state.cls); });
    if (count) count.textContent = n + ' ' + NOUN;
    if (none)  none.hidden = n > 0;
    var any = state.q || state.cls !== 'all' || AXES.some(function (a) { return state[a]; });
    if (clear) clear.hidden = !any;
  }

  pills.forEach(function (p) {
    p.addEventListener('click', function () {
      var a = axisOf(p), v = p.dataset[a];
      state[a] = state[a] === v ? null : v;
      apply();
    });
  });
  tabs.forEach(function (t) {
    t.addEventListener('click', function () { state.cls = t.dataset['class']; apply(); });
  });
  if (search) search.addEventListener('input', function () {
    state.q = search.value.trim().toLowerCase();
    apply();
  });
  if (clear) clear.addEventListener('click', function () {
    state.q = ''; state.cls = 'all';
    AXES.forEach(function (a) { state[a] = null; });
    if (search) search.value = '';
    apply();
  });
  apply();
});
</script>
"""


def filter_js(axes, noun):
    return FILTER_JS % (json.dumps(axes), json.dumps(noun))


def board_body(search_label, facets, count_text, rows, empty='Nothing on record matches.', panels=False):
    return ('<div class="board-body%s">\n'
            '  <div class="search-row" data-pagefind-ignore>'
            '<input class="search-input" type="search" placeholder="Search by name..." aria-label="%s"></div>\n'
            '  <div class="facets" data-pagefind-ignore>%s</div>\n'
            '  <div class="result-line" data-pagefind-ignore><span class="result-count">%s</span>'
            '<button class="clear-btn" type="button" hidden>Clear filters</button></div>\n'
            '  <div class="register" data-pagefind-ignore>\n%s\n  </div>\n'
            '  <p class="no-results" hidden>%s</p>\n</div>'
            % (' panels' if panels else '', e(search_label), ''.join(facets), e(count_text),
               '\n'.join(rows), e(empty)))


# ---------------------------------------------------------------------------
# UNEXPECTED JOURNEYS
# ---------------------------------------------------------------------------

def glance(j, r, with_synopsis=True):
    rows = []
    if with_synopsis:
        rows.append('<div class="glance-synopsis">%s</div>' % e(j['synopsis']))

    def row(lab, chips):
        if chips:
            rows.append('<div class="glance-row"><span class="glance-label">%s</span>'
                        '<div class="glance-chips">%s</div></div>' % (lab, ''.join(chips)))
    row('The Embers', [chip('pc:' + s, r) for s in j['pcs']])
    row('Key NPCs', [glance_chip(t, ref, r, 'chip chip-npc') for t, ref in j['npcs']])
    row('Locations', [glance_chip(t, ref, r, 'chip chip-place') for t, ref in j['places']])
    row('Items', [glance_chip(t, ref, r, 'chip chip-item') for t, ref in j['items']])
    return '\n'.join(rows)


def build_journeys():
    for j in JOURNEYS:
        k = pad(j['num'])
        path = 'unexpected-journeys/journey-%s.html' % k
        r = rel(path)
        brief = (HERE / 'journeys' / (k + '.brief.html')).read_text(encoding='utf-8')
        full = (HERE / 'journeys' / (k + '.full.html')).read_text(encoding='utf-8')
        prev = ('journey-%s.html' % pad(j['num'] - 1), 'Previous Journey') if j['num'] - 1 in JBY else None
        nxt = ('journey-%s.html' % pad(j['num'] + 1), 'Next Journey') if j['num'] + 1 in JBY else None
        centre = ('index.html', 'All Journeys')
        if j.get('video'):
            rec = ('<div class="video-container"><iframe src="https://www.youtube.com/embed/%s" '
                   'title="Session recording" loading="lazy" allowfullscreen></iframe></div>\n'
                   '<div class="video-link">Watch on YouTube: <a href="https://youtu.be/%s" target="_blank" '
                   'rel="noopener">youtu.be/%s</a> &middot; <a href="%s" target="_blank" rel="noopener">'
                   'all recordings</a></div>' % (j['video'], j['video'], j['video'], e(CAMPAIGN['playlist'])))
        elif j.get('video') is False:
            rec = ('<div class="video-container"><div class="video-placeholder">'
                   '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true">'
                   '<circle cx="24" cy="24" r="20"/><polygon points="20,16 36,24 20,32" fill="currentColor" '
                   'stroke="none" opacity="0.4"/></svg><p>This Session Was Not Recorded</p></div></div>\n'
                   '<div class="video-link">The other sessions: <a href="%s" target="_blank" '
                   'rel="noopener">all recordings</a></div>' % e(CAMPAIGN['playlist']))
        else:
            rec = ('<div class="video-container"><div class="video-placeholder">'
                   '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true">'
                   '<circle cx="24" cy="24" r="20"/><polygon points="20,16 36,24 20,32" fill="currentColor" '
                   'stroke="none" opacity="0.4"/></svg><p>Recording Not Linked Yet</p></div></div>\n'
                   '<div class="video-link">Find it in the playlist: <a href="%s" target="_blank" '
                   'rel="noopener">all recordings</a></div>' % e(CAMPAIGN['playlist']))
        content = '''<div class="log-meta">
  <span class="log-badge">UJ {k}</span>
  <span class="log-type-badge">Party Level {level}</span>
  <span class="log-type-badge">{where}</span>
</div>
{bar}
<div class="voyage-glance">
{glance}
</div>
<div class="railed">
<div class="account-tabs tabrail" data-pagefind-ignore>
  <button class="account-tab is-active" type="button" data-panel="brief" aria-selected="true">
    <span class="account-tab-name">Brief Account</span>
    <span class="account-tab-note">What happened, beat by beat</span>
  </button>
  <button class="account-tab" type="button" data-panel="full" aria-selected="false">
    <span class="account-tab-name">Full Account</span>
    <span class="account-tab-note">The whole story, as written</span>
  </button>
  <button class="account-tab" type="button" data-panel="recording" aria-selected="false">
    <span class="account-tab-name">Recording</span>
    <span class="account-tab-note">The session as it was played</span>
  </button>
</div>
<div class="account-panels panels">
  <section class="account-panel is-active" id="brief" data-panel="brief">
    <div class="account-body">
{brief}
    </div>
  </section>
  <section class="account-panel" id="full" data-panel="full">
    <div class="account-body">
<div class="narrative">
{full}
</div>
    </div>
  </section>
  <section class="account-panel" id="recording" data-panel="recording" data-pagefind-ignore>
    <div class="account-body">
{rec}
    </div>
  </section>
</div>
</div>
{bottom}'''.format(k=k, level=j['level'], where=e(j['where']), bar=nav_bar(prev, centre, nxt),
                   glance=glance(j, r), brief=brief.rstrip(), full=full.rstrip(), rec=rec,
                   bottom=nav_bar(prev, centre, nxt, bottom=True))
        page(path, j['title'], 'journey', 'unexpected-journeys', content,
             eyebrow='Unexpected Journey ' + k, subtitle=j['subtitle'])

    # index, newest first
    rows = []
    for j in sorted(JOURNEYS, key=lambda x: -x['num']):
        k = pad(j['num'])
        rows.append('''<div class="log-entry">
  <div class="log-row">
    <a class="log-row-link" href="journey-{k}.html">
      <span class="log-num"><span class="log-num-label">Journey</span><span class="log-num-val">{k}</span></span>
      <span class="log-title">{title}</span>
      <span class="log-open">Open Record {arrow}</span>
    </a>
    <button class="log-toggle" data-pagefind-ignore type="button" aria-expanded="false" aria-controls="ov-{k}">
      <span class="log-toggle-label">Overview</span><svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 4l4 4 4-4"/></svg>
    </button>
  </div>
  <div class="log-overview" data-pagefind-ignore id="ov-{k}" hidden>
{glance}
    <div class="overview-foot"><a class="overview-link" href="journey-{k}.html">Open Full Record {arrow}</a></div>
  </div>
</div>'''.format(k=k, title=e(j['title']), arrow=RIGHT, glance=glance(j, '../')))
    content = ('<div class="intro-note">Open a journey for the full record: the glance, the brief account, '
               'the whole story and the recording. Or expand a row here for the quick overview without '
               'leaving the list.</div>\n<div class="section-label">All Journeys</div>\n'
               '<div class="log-table">\n%s\n</div>' % '\n'.join(rows))
    page('unexpected-journeys/index.html', 'Unexpected Journeys', 'jindex', 'unexpected-journeys', content,
         subtitle='Every session on record, newest first.')


# ---------------------------------------------------------------------------
# THE EMBERS
# ---------------------------------------------------------------------------

def embers_banner(r, href, caption=''):
    """The company's own banner, made by the players. r is the path back to the site root."""
    cap = ('<figcaption>%s</figcaption>' % caption) if caption else ''
    return ('<figure class="embers-banner" data-pagefind-ignore><a href="{href}">'
            '<img src="{r}images/the-embers.jpg" '
            'srcset="{r}images/the-embers-800.jpg 800w, {r}images/the-embers.jpg 1600w" '
            'sizes="(max-width: 960px) 100vw, 920px" width="1600" height="873" '
            'alt="The Embers: a phoenix of flame rising from a bed of coals, above a scroll bearing the company\'s name">'
            '</a>{cap}</figure>').format(r=r, href=href, cap=cap)


def build_embers():
    for i, pc in enumerate(PCS):
        stats = [('Race', pc['race']), ('Class', pc['klass']), ('Affiliation', pc['affiliation']),
                 ('First Journey', 'Journey ' + pad(pc['first'])), ('Last Seen', last_seen(pc)),
                 ('Status', pc['status'])]
        entity_page(pc, 'the-embers', 'The Embers', stats, pc['sub'],
                    chain(PCS, i, ('index.html', 'The Embers')))

    races = sorted({p['race'] for p in PCS})
    classes = sorted({p['klass'] for p in PCS})
    rows = []
    for pc in PCS:
        rows.append('''<div class="ent crew-row" data-race="{race}" data-klass="{klass}" data-name="{lname}">
  <a class="ent-row" href="{slug}.html">
    {face}
    <span class="ent-name">{name}<span class="ent-sub">{race_} &middot; {klass_}</span></span>
    <span class="ent-type">{status}</span>
    <span class="ent-state">{last}</span>
  </a>
  <div class="ent-detail"><p class="stub-desc">{line}</p></div>
</div>'''.format(race=slugify(pc['race']), klass=slugify(pc['klass']), lname=e(pc['name'].lower()),
                 slug=pc['slug'], face=face(pc), name=e(pc['name']), race_=e(pc['race']),
                 klass_=e(pc['klass']), status=e(pc['status']), last=last_seen(pc),
                 line=e(pc['pursuit'])))
    facets = [facet('Race', [pill('race', slugify(x), x) for x in races]),
              facet('Class', [pill('klass', slugify(x), x) for x in classes])]
    content = ('<p class="intro-note">Five who met on a road and one cousin who comes and goes. Each row '
               'carries what that Ember is chasing; the file behind it has every journey they have been part of, '
               'what they carry, and who they are tied to.</p>\n'
               + board_body('Search the Embers', facets, '%d in the company' % len(PCS), rows))
    page('the-embers/index.html', 'The Embers', 'listing', 'the-embers', content,
         subtitle='The company, and what each of them carries',
         tail=filter_js(['race', 'klass'], 'in the company'),
         hero=embers_banner('../', '../images/the-embers.jpg', 'The company\'s banner, made by its players.'))


# ---------------------------------------------------------------------------
# DOSSIERS
# ---------------------------------------------------------------------------

def build_dossiers():
    ordered = sorted(NPCS, key=lambda n: re.sub(r'^(The|Lord|Sir|Mayor|Marshal|Governor)\s+', '', n['name']))
    for i, n in enumerate(ordered):
        stats = [('Role', n['role']), ('To the Embers', n['relation']), ('Affiliation', n['affiliation']),
                 ('Standing', n['standing']), ('Last Seen', last_seen(n)), ('Status', n['status'])]
        entity_page(n, 'dossiers', 'Dossiers', stats, n['role'],
                    chain(ordered, i, ('index.html', 'Dossiers')))

    rows = []
    for n in ordered:
        state = last_seen(n) + (' &middot; named only' if n.get('named_only') else '')
        rows.append('''<div class="ent npc-row" data-met="{met}" data-aff="{aff}" data-name="{lname}">
  <a class="ent-row" href="{slug}.html">
    {face}
    <span class="ent-name">{name}<span class="ent-sub">{role}</span></span>
    <span class="ent-type">{standing}</span>
    <span class="ent-state">{state}</span>
  </a>
  <div class="ent-detail"><p class="stub-desc">{ov}</p></div>
</div>'''.format(met=n['met'], aff=n['aff'],
                 lname=e(' '.join([n['name']] + n.get('aliases', [])).lower()),
                 slug=n['slug'], face=face(n), name=e(n['name']), role=e(n['role']),
                 standing=e(n['standing']), state=state, ov=e(n['overview'])))
    # Named, unfiled: these exist nowhere else, so they stay indexed.
    unfiled = []
    for name, line in UNFILED:
        unfiled.append('''<div class="ent npc-row is-unfiled" data-met="" data-aff="" data-name="{lname}">
  <div class="ent-row is-unlinked">
    <span class="ent-face"><span class="face-mono" data-pagefind-ignore>{m}</span></span>
    <span class="ent-name">{name}<span class="ent-sub">Named, unfiled</span></span>
    <span class="ent-type"></span>
    <span class="ent-state">No file</span>
  </div>
  <div class="ent-detail"><p class="stub-desc">{line}</p></div>
</div>'''.format(lname=e(name.lower()), m=e(mono(name)), name=e(name), line=e(line)))

    mets = [m for m in MET_LABELS if any(n['met'] == m for n in NPCS)]
    affs = [a for a in AFF_LABELS if any(n['aff'] == a for n in NPCS)]
    facets = [facet('Where met', [pill('met', m, MET_LABELS[m]) for m in mets]),
              facet('Affiliation', [pill('aff', a, AFF_LABELS[a]) for a in affs], stacked=True)]
    total = len(ordered) + len(unfiled)
    body = board_body('Search dossiers', facets, '%d on record' % total, rows)
    # unfiled rows sit in the same register but outside the pagefind-ignore
    body = body.replace('\n  </div>\n  <p class="no-results"',
                        '\n  </div>\n  <div class="section-label unfiled-label">Named, Unfiled</div>\n'
                        '  <div class="register register-unfiled">\n%s\n  </div>\n  <p class="no-results"'
                        % '\n'.join(unfiled))
    page('dossiers/index.html', 'Dossiers', 'listing', 'dossiers', body,
         subtitle='Everyone the Embers have met, and everyone they have heard of',
         tail=filter_js(['met', 'aff'], 'on record'))


# ---------------------------------------------------------------------------
# THE ATLAS
# ---------------------------------------------------------------------------

def build_atlas():
    for i, p in enumerate(PLACES):
        region = dict((a, b) for a, b, _ in REGIONS)[p['region']]
        stats = [('Type', p['kind']), ('Region', region), ('Where', p['where']),
                 ('Last Visited', last_seen(p)), ('Status', p['status'])]
        mid = ''
        if p.get('sites'):
            mid += ('<div class="xref-card"><div class="xref-head"><span class="xref-title">Within %s</span></div>'
                    '<ul class="site-list">%s</ul></div>'
                    % (e(p['name']), ''.join('<li><span class="site-name">%s</span>'
                                             '<span class="site-note">%s</span></li>' % (e(a), e(b))
                                             for a, b in p['sites'])))
        if p.get('plate'):
            pl = p['plate']
            mid += ('<figure class="plate"><img src="%s" alt="%s" loading="lazy">'
                    '<figcaption>%s</figcaption></figure>' % (pl['src'], e(pl['alt']), e(pl['caption'])))
        entity_page(p, 'atlas', 'The Atlas', stats, p['kind'],
                    chain(PLACES, i, ('index.html', 'The Atlas')), extra_mid=mid)

    tabs, panels = [], []
    for n, (key, name, note) in enumerate(REGIONS):
        linked = [p for p in PLACES if p['region'] == key]
        loose = [p for p in PLACES_UNLINKED if p['region'] == key]
        rows = []
        for p in linked:
            sites = ''
            if p.get('sites'):
                sites = ('<div class="det-sites"><span class="det-label">Within</span><div class="det-chips">%s</div></div>'
                         % ''.join('<span class="stub-chip" style="cursor:default">%s</span>' % e(a)
                                   for a, _ in p['sites']))
            rows.append('''<div class="ent place-row" data-entry="{name}">
  <a class="ent-row" href="{slug}.html"><span class="ent-glyph body"></span>
    <span class="ent-name">{name}<span class="ent-sub">{kind} &middot; {where}</span></span>
    <span class="ent-state">{status}</span></a>
  <div class="ent-detail"><p class="stub-desc">{ov}</p>{sites}</div>
</div>'''.format(name=e(p['name']), slug=p['slug'], kind=e(p['kind']), where=e(p['where']),
                 status=e(p['status']), ov=e(p['overview']), sites=sites))
        for p in loose:
            rows.append('''<div class="ent place-row is-unknown" data-entry="{name}">
  <div class="ent-row is-unlinked"><span class="ent-glyph body"></span>
    <span class="ent-name">{name}<span class="ent-sub">{kind} &middot; {where}</span></span>
    <span class="ent-state">{status}</span></div>
  <div class="ent-detail"><p class="stub-desc">{ov}</p></div>
</div>'''.format(name=e(p['name']), kind=e(p['kind']), where=e(p['where']), status=e(p['status']),
                 ov=e(p['blurb'])))
        tabs.append('<button class="board-tab%s" type="button" data-panel="%s" aria-selected="%s">%s '
                    '<span class="board-count">%d</span></button>'
                    % (' is-active' if n == 0 else '', key, 'true' if n == 0 else 'false', e(name), len(rows)))
        panels.append('<section class="board-panel%s" id="%s" data-panel="%s">\n'
                      '<p class="board-note">%s</p>\n<div class="register">\n%s\n</div>\n</section>'
                      % (' is-active' if n == 0 else '', key, key, e(note), '\n'.join(rows)))
    content = ('<div class="intro-note">Where the Embers have been, and where they have only been told to go. '
               'Entries drawn faintly are known by name alone.</div>\n'
               '<div class="survey"><img src="%s" alt="%s" loading="lazy"></div>\n'
               '<div class="railed">\n<div class="board-tabs tabrail" data-pagefind-ignore>\n%s\n</div>\n'
               '<div class="board-panels panels" data-pagefind-ignore>\n%s\n</div>\n</div>'
               % (ATLAS_MAP['src'], e(ATLAS_MAP['alt']), '\n'.join(tabs), '\n'.join(panels)))
    page('atlas/index.html', 'The Atlas', 'listing', 'atlas', content,
         subtitle='Every road walked and every place worth marking')


# ---------------------------------------------------------------------------
# THE ARMORY
# ---------------------------------------------------------------------------

def build_armory():
    ordered = sorted(ITEMS, key=lambda x: re.sub(r'^The\s+', '', x['name']))
    for i, it in enumerate(ordered):
        stats = [('Type', it['kind']), ('Held By', it['holder']), ('Origin', it['origin']),
                 ('Last Seen', last_seen(it)), ('Status', it['status'])]
        entity_page(it, 'armory', 'Armory', stats, it['sub'],
                    chain(ordered, i, ('index.html', 'Armory')))

    kinds = sorted({i['kind'] for i in ITEMS})
    holders = []
    for it in ITEMS:
        if it['holder'] not in holders:
            holders.append(it['holder'])
    rows = []
    for it in ordered:
        rows.append('''<div class="ent item-row" data-class="{klass}" data-type="{kind}" data-holder="{hold}" data-name="{lname}">
  <a class="ent-row" href="{slug}.html">
    <span class="ent-face {klass}"><span class="face-mono" data-pagefind-ignore>{m}</span></span>
    <span class="ent-name">{name}<span class="ent-sub">{sub}</span></span>
    <span class="ent-type">{kind_}</span>
    <span class="ent-state">{holder}</span>
  </a>
  <div class="ent-detail"><p class="stub-desc">{ov}</p></div>
</div>'''.format(klass=it['klass'], kind=slugify(it['kind']), hold=slugify(it['holder']),
                 lname=e(it['name'].lower()), slug=it['slug'], m=e(mono(it['name'])), name=e(it['name']),
                 sub=e(it['sub']), kind_=e(it['kind']), holder=e(it['holder']), ov=e(it['overview'])))
    tabs = []
    for key, name in ITEM_TABS:
        n = len(ITEMS) if key == 'all' else sum(1 for i in ITEMS if i['klass'] == key)
        tabs.append('<button class="board-tab%s" type="button" data-class="%s">%s <span class="board-count">%d</span></button>'
                    % (' is-active' if key == 'all' else '', key, e(name), n))
    facets = [facet('Type', [pill('type', slugify(k), k) for k in kinds], stacked=True),
              facet('Held by', [pill('holder', slugify(h), h) for h in holders], stacked=True)]
    content = ('<div class="railed">\n<div class="board-tabs tabrail" data-pagefind-ignore>\n%s\n</div>\n%s\n</div>'
               % ('\n'.join(tabs), board_body('Search the armory', facets, '%d on record' % len(ITEMS),
                                               rows, panels=True)))
    page('armory/index.html', 'Armory', 'listing', 'armory', content,
         subtitle='What the Embers carry, and what it has cost them',
         tail=filter_js(['type', 'holder'], 'on record'))


# ---------------------------------------------------------------------------
# WAR INTEL
# ---------------------------------------------------------------------------

def build_war_intel():
    for i, f in enumerate(FACTIONS):
        stats = [('Type', f['kind']), ('To the Embers', f['relation']), ('Last Seen', last_seen(f)),
                 ('Status', f['status'])]
        entity_page(f, 'war-intel', 'War Intel', stats, f['kind'],
                    chain(FACTIONS, i, ('index.html', 'War Intel')))
    blocks = []
    for key, name, note in FACTION_BANDS:
        cards = []
        for f in [x for x in FACTIONS if x['band'] == key]:
            cards.append('<a class="s-card" href="%s.html"><div class="s-card-head"><div class="s-icon">'
                         '<span class="face-mono" data-pagefind-ignore>%s</span></div><div class="s-title">%s</div></div>'
                         '<div class="s-desc">%s</div></a>'
                         % (f['slug'], e(mono(f['name'])), e(f['name']), e(f['overview'])))
        blocks.append('<div class="section-label">%s <span class="section-note">%s</span></div>\n'
                      '<div class="card-grid" data-pagefind-ignore>\n%s\n</div>' % (e(name), e(note), '\n'.join(cards)))
    page('war-intel/index.html', 'War Intel', 'listing', 'war-intel', '\n'.join(blocks),
         subtitle='The powers shaping the war, as far as the Embers know them')


# ---------------------------------------------------------------------------
# QUEST BOARD
# ---------------------------------------------------------------------------

def progress(q):
    obj = q.get('objectives')
    if not obj:
        return None
    return sum(1 for _, d in obj if d), len(obj)


def build_quests():
    order = [q for q in QUESTS if q['status'] == 'open'] + [q for q in QUESTS if q['status'] == 'closed']
    for i, q in enumerate(order):
        path = 'quests/%s.html' % q['slug']
        r = '../'
        bar = chain(order, i, ('index.html', 'Quest Board'))
        parts = [bar]
        if q.get('giver'):
            g = get(q['giver'])
            if g.get('portrait'):
                gf = '<img src="%s" alt="" loading="lazy">' % g['portrait']
            else:
                gf = '<span class="monogram" data-pagefind-ignore>%s</span>' % e(mono(g['name']))
            parts.append('<div class="giver-strip"><div class="giver-face">%s</div><div class="giver-info">'
                         '<span class="giver-label">%s</span> <a class="giver-name" href="%s%s">%s</a></div></div>'
                         % (gf, 'Set by' if q['slug'] == 'the-orb-of-dragonkind' else 'Assigned by',
                            r, url(q['giver']), e(g['name'])))
        desc = paras(q['overview'])
        if q.get('outcome'):
            desc += '<p class="quest-outcome"><span class="pursuit-label">Outcome</span> %s</p>' % e(q['outcome'])
        if q.get('parent'):
            desc += ('<span class="row-sub">Part of <a href="%s.html" style="color:inherit">%s</a></span>'
                     % (q['parent'], e(get('quest:' + q['parent'])['name'])))
        pr = progress(q)
        if pr:
            objs = ''.join('<li class="obj-item%s"><span class="obj-box">%s</span><span class="obj-text">%s</span></li>'
                           % (' is-done' if d else '', CHECK if d else '', e(t)) for t, d in q['objectives'])
            side = ('<div class="panel"><div class="panel-head"><span class="panel-title">Objectives</span>'
                    '<span class="panel-count">%d of %d</span></div><ul class="obj-list">%s</ul></div>'
                    % (pr[0], pr[1], objs))
            items = sorted([t for t in LINKS[q['ref']] if t.startswith('item:')], key=label)
            if items:
                side += ('<div class="panel"><div class="panel-head"><span class="panel-title">Notable Items</span>'
                         '<span class="panel-count">%d</span></div><ul class="loot-list">%s</ul></div>'
                         % (len(items), ''.join(
                             '<li class="loot-item"><a class="loot-link" href="%s%s"><span class="loot-name">%s</span>'
                             '<span class="loot-note">%s</span></a></li>'
                             % (r, url(t), e(get(t)['name']), e(get(t)['sub'])) for t in items)))
            if q.get('rewards'):
                side += ('<div class="panel"><div class="panel-head"><span class="panel-title">Rewards</span></div>'
                         '<ul class="loot-list">%s</ul></div>'
                         % ''.join('<li class="loot-item"><span class="loot-link"><span class="loot-name">%s</span></span></li>'
                                   % e(x) for x in q['rewards']))
            parts.append('<div class="brief-grid"><div class="panel"><div class="panel-head">'
                         '<span class="panel-title">Briefing</span></div><div class="quest-desc">%s</div></div>'
                         '<div>%s</div></div>' % (desc, side))
        else:
            parts.append('<div class="entry-body" style="max-width:80ch;">%s</div>' % desc)
        conn = connections(q['ref'], r)
        if conn:
            parts.append(conn)
        parts.append(records_block(q, r))
        kindword = 'Quest' if q['kind'] == 'quest' else 'Thread'
        page(path, q['name'], 'entity', 'quests', '\n'.join(p for p in parts if p),
             eyebrow=('Closed ' + kindword) if q['status'] == 'closed' else kindword)

    def row(q, child=False):
        pr = progress(q)
        extra = ''
        if q.get('giver') and not child:
            g = get(q['giver'])
            gf = ('<img src="%s" alt="" loading="lazy">' % g['portrait']) if g.get('portrait') \
                else '<span class="monogram" data-pagefind-ignore>%s</span>' % e(mono(g['name']))
            extra = ('<span class="row-giver"><span class="row-giver-face">%s</span>%s %s</span>'
                     % (gf, 'Set by' if q['slug'] == 'the-orb-of-dragonkind' else 'Assigned by', e(g['name'])))
        if child:
            extra = '<span class="row-sub">Part of %s</span>' % e(get('quest:' + q['parent'])['name'])
        if q['status'] == 'closed' and q.get('outcome'):
            extra = '<span class="row-sub">%s</span>' % e(q['outcome'])
        prog = ('<span class="obj-progress">%d/%d</span>' % pr) if pr else '<span class="obj-progress is-none">&middot;</span>'
        return ('<div class="log-entry q-entry%s" data-kind="%s"><div class="log-row">'
                '<a class="log-row-link" href="%s.html"><span class="log-title">%s '
                '<span class="q-kind kind-%s">%s</span>%s</span>%s<span class="log-open">Open &rsaquo;</span></a>'
                '</div></div>' % (' is-child' if child else '', q['kind'], q['slug'], e(q['name']),
                                  q['kind'], 'Quest' if q['kind'] == 'quest' else 'Thread', extra, prog))

    open_q = [q for q in QUESTS if q['status'] == 'open' and q['kind'] == 'quest']
    qrows = []
    for q in open_q:
        qrows.append(row(q))
        for c in QUESTS:
            if c.get('parent') == q['slug'] and c['status'] == 'open':
                qrows.append(row(c, child=True))
    threads = [q for q in QUESTS if q['status'] == 'open' and q['kind'] == 'thread' and not q.get('parent')]
    closed = sorted([q for q in QUESTS if q['status'] == 'closed'], key=lambda q: -q['last'])
    content = '''<div class="railed">
<div class="board-tabs tabrail" data-pagefind-ignore>
  <button class="board-tab is-active" type="button" data-panel="quests" aria-selected="true">Quests <span class="board-count">{nq}</span></button>
  <button class="board-tab" type="button" data-panel="threads" aria-selected="false">Threads <span class="board-count">{nt}</span></button>
  <button class="board-tab" type="button" data-panel="closed" aria-selected="false">Closed <span class="board-count">{nc}</span></button>
</div>
<div class="board-panels panels">
  <section class="board-panel is-active" id="quests" data-panel="quests">
    <p class="board-note">Work the Embers have taken on, whether handed to them or picked up because it mattered enough to follow.</p>
    <div class="log-table" data-pagefind-ignore>{q}</div>
  </section>
  <section class="board-panel" id="threads" data-panel="threads">
    <p class="board-note">Loose ends and open questions. Nobody has been handed these. Any of them could become a quest.</p>
    <div class="log-table" data-pagefind-ignore>{t}</div>
  </section>
  <section class="board-panel" id="closed" data-panel="closed">
    <p class="board-note">Finished, one way or another.</p>
    <div class="log-table" data-pagefind-ignore>{c}</div>
  </section>
</div>
</div>'''.format(nq=len(open_q), nt=len(threads), nc=len(closed), q=''.join(qrows),
                 t=''.join(row(q) for q in threads), c=''.join(row(q) for q in closed))
    page('quests/index.html', 'Quest Board', 'listing', 'quests', content,
         subtitle='What the Embers are chasing, and what is chasing them')


# ---------------------------------------------------------------------------
# THE ROAD SO FAR
# ---------------------------------------------------------------------------

def build_road():
    s = STANDING
    j = JBY[s['journey']]
    r = '../'
    cards = []
    for slug in s['quests']:
        q = get('quest:' + slug)
        pr = progress(q)
        nxt = next((t for t, d in q.get('objectives', []) if not d), None)
        pct = int(100 * pr[0] / pr[1]) if pr else 0
        cards.append('<a class="q-card" href="%squests/%s.html"><span class="q-top"><span class="q-name">%s</span>'
                     '<span class="q-prog">%s</span></span><span class="q-bar"><span class="q-fill" style="width:%d%%">'
                     '</span></span>%s</a>'
                     % (r, slug, e(q['name']), ('%d/%d' % pr) if pr else '', pct,
                        ('<span class="q-next"><span class="q-next-label">Next</span> %s</span>' % e(nxt)) if nxt else ''))
    crew = ''.join('<a class="crew-card" href="%sthe-embers/%s.html"><span class="crew-name">%s</span>'
                   '<span class="crew-line">%s</span></a>' % (r, p['slug'], e(p['short']), e(p['line']))
                   for p in PCS)
    stops = ''.join('<a class="tl-stop%s" href="%sunexpected-journeys/journey-%s.html"><span class="tl-dot"></span>'
                    '<span class="tl-num">%s</span><span class="tl-title">%s</span></a>'
                    % (' is-now' if x['num'] == s['journey'] else '', r, pad(x['num']), pad(x['num']), e(x['title']))
                    for x in sorted(JOURNEYS, key=lambda x: -x['num']))
    content = '''<div class="bearing">
  <div class="bearing-main">
    <div class="here">
      <span class="here-label">Position</span>
      <span class="here-name">{pos}</span>
      <span class="here-sub">{blurb}</span>
    </div>
    <div class="panel">
      <div class="panel-head"><span class="panel-title">Last Journey</span>
        <a class="panel-more" href="{r}unexpected-journeys/journey-{k}.html">Read the account &rsaquo;</a></div>
      <div class="last-title">Journey {k}: {title}</div>
      <p class="last-text">{last}</p>
      <p class="last-text">{conseq}</p>
      <div class="chip-row"><span class="chip-label">Faces</span><div class="chips">{met}</div></div>
    </div>
    <div class="panel">
      <div class="panel-head"><span class="panel-title">Quest Board</span>
        <a class="panel-more" href="{r}quests/index.html">All quests &rsaquo;</a></div>
      <div class="q-grid">{cards}</div>
    </div>
    <div class="panel">
      <div class="panel-head"><span class="panel-title">The Embers</span>
        <a class="panel-more" href="{r}the-embers/index.html">The company &rsaquo;</a></div>
      <div class="crew-grid">{crew}</div>
    </div>
    <div class="panel">
      <div class="panel-head"><span class="panel-title">Still Unanswered</span>
        <a class="panel-more" href="{r}quests/index.html#threads">All threads &rsaquo;</a></div>
      <div class="chips">{open}</div>
    </div>
  </div>
  <nav class="timeline" data-pagefind-ignore>
    <div class="tl-head">The Road</div>
    <div class="tl-stops">{stops}</div>
  </nav>
</div>'''.format(pos=e(s['position']), blurb=e(s['pos_blurb']), r=r, k=pad(j['num']), title=e(j['title']),
                 last=e(s['last_text']), conseq=e(s['consequence']),
                 met=''.join('<a class="chip" href="%s%s">%s</a>' % (r, url(t), e(label(t))) for t in s['met']),
                 cards=''.join(cards), crew=crew,
                 open=''.join('<a class="chip" href="%squests/%s.html">%s</a>'
                              % (r, x, e(get('quest:' + x)['name'])) for x in s['unanswered']),
                 stops=stops)
    page('road-so-far/index.html', 'The Road So Far', 'road', 'road-so-far', content,
         subtitle='As of Journey %s: %s' % (pad(j['num']), j['title']))


# ---------------------------------------------------------------------------
# SEARCH
# ---------------------------------------------------------------------------

def build_search():
    scopes = [(k, v) for k, v in SECTION_LABELS.items()]
    opts = ''.join('<option value="%s">%s</option>' % (k, e(v)) for k, v in scopes)
    labels = dict([('', 'all records')] + scopes)
    path = 'search/index.html'
    extra = ('<script src="../data/vocabulary.js"></script>\n<script src="../scripts/spelling.js"></script>\n')
    body = '''<body data-pagefind-ignore>
<div class="terminal-wrap">
  <div class="terminal-head">
    <div class="terminal-eyebrow">Shadow of the Dragon Queen &middot; The Record</div>
    <h1 class="terminal-title">Search</h1>
    <p class="terminal-sub">Every journey, face, place and thing on record. If a name is spelled the way it sounded at the table, the search will try to meet you halfway.</p>
  </div>
  <div class="search-console">
    <div class="search-console-label">Query</div>
    <div class="search-row">
      <div class="search-field">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.5-4.5"/></svg>
        <input class="search-input" id="q" type="text" placeholder="Search the record&hellip;" autocomplete="off" autofocus aria-label="Search the record">
      </div>
      <div class="scope-select">
        <select id="scope" aria-label="Section to search">
          <option value="">All Records</option>
          %s
        </select>
      </div>
    </div>
    <div class="scope-hint" id="scopeHint">Searching <b>all records</b>. Choose a section to search only within it.</div>
  </div>
  <div id="resultsMeta" class="results-meta" style="display:none;">
    <div class="results-count"><span id="count">0</span> &middot; <span class="results-term" id="termEcho"></span></div>
    <div class="results-scope" id="scopeEcho">across all records</div>
  </div>
  <div id="results"></div>
  <div id="state" class="search-state">Enter a name, place, or event to begin.</div>
</div>

<script type="module">
// Player-facing search. Uses the Pagefind JS API; the index is generated
// into /pagefind/ by the deploy Action, so it does not exist in the repo.

const SCOPE_LABELS = %s;

const STOPWORDS = new Set(['a','an','the','of','to','in','on','at','by','for','and','or','but','is','was','it','as','with','from','that','this','his','her','their','they','them','he','she']);
function cleanExcerpt(html) {
  return html.replace(/<mark>(.*?)<\\/mark>/g, (m, word) =>
    STOPWORDS.has(word.trim().toLowerCase()) ? word : m);
}

function sectionFromUrl(url) {
  const segs = url.replace(/^\\//, '').split('/');
  let label = 'Records';
  for (const s of segs) { if (SCOPE_LABELS[s]) { label = SCOPE_LABELS[s]; break; } }
  const m = url.match(/journey-(\\d+)/);
  if (m) label += ' \\u00b7 ' + m[1];
  return label;
}

let pagefind = null;
async function loadPagefind() {
  if (pagefind) return pagefind;
  try {
    pagefind = await import('../pagefind/pagefind.js');
    const siteRoot = location.pathname.replace(/search\\/(index\\.html)?$/, '');
    await pagefind.options({ excerptLength: 30, baseUrl: siteRoot });
    await pagefind.init();
  } catch (e) {
    pagefind = null;
    document.getElementById('state').textContent =
      'Search index not yet available. It builds automatically on deploy.';
    console.error('Pagefind load failed:', e);
  }
  return pagefind;
}

const qEl = document.getElementById('q');
const scopeEl = document.getElementById('scope');
const resultsEl = document.getElementById('results');
const stateEl = document.getElementById('state');
const metaEl = document.getElementById('resultsMeta');
const countEl = document.getElementById('count');
const termEcho = document.getElementById('termEcho');
const scopeEcho = document.getElementById('scopeEcho');
const scopeHint = document.getElementById('scopeHint');

function setState(msg) { stateEl.style.display = 'block'; stateEl.textContent = msg; }
function clearState() { stateEl.style.display = 'none'; }
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

const bareWord = w => w.toLowerCase().replace(/[^a-z0-9]/g, '');
async function hasRealHit(search, term) {
  if (!search.results.length) return false;
  const words = term.split(/\\s+/).map(bareWord).filter(w => w.length >= 3 && !STOPWORDS.has(w));
  if (!words.length) return true;
  const sample = await Promise.all(search.results.slice(0, 5).map(r => r.data()));
  // Every word typed has to be found for real. A highlight counts for a word
  // when it starts the same way, or is that word's stem (not just its first
  // few letters, which is all Pagefind's prefix fallback needs to match).
  const marks = [].concat(...sample.map(d => (d.excerpt.match(/<mark>(.*?)<\\/mark>/g) || [])
    .map(m => bareWord(m.replace(/<\\/?mark>/g, ''))))).filter(m => m.length >= 3);
  return words.every(w => marks.some(m => m.startsWith(w.slice(0, 4)) ||
    (w.startsWith(m) && m.length >= w.length - 3)));
}

let debounce;
async function run() {
  const term = qEl.value.trim();
  const scope = scopeEl.value;

  scopeHint.innerHTML = scope
    ? 'Searching <b>' + SCOPE_LABELS[scope] + '</b> only. Switch to <b>All Records</b> to search everything.'
    : 'Searching <b>all records</b>. Choose a section to search only within it.';

  const priorNote = document.getElementById('correction-note');
  if (priorNote) priorNote.remove();

  if (!term) {
    resultsEl.innerHTML = '';
    metaEl.style.display = 'none';
    setState('Enter a name, place, or event to begin.');
    return;
  }

  const pf = await loadPagefind();
  if (!pf) return;

  const opts = scope ? { filters: { section: scope } } : {};
  let search = await pf.search(term, opts);

  // Nothing real as typed? Try a repaired spelling before giving up. Names
  // heard across a table rarely survive contact with a keyboard intact.
  //
  // "Nothing" needs care. When a word is not in the index, Pagefind falls
  // back to ever-shorter prefixes of it, so a misspelling usually comes back
  // with a few junk hits on its first letter or two rather than with none.
  // A hit only counts if what it highlighted shares a real stem with what
  // was typed.
  let searched = term, correctedFrom = null;
  if (window.SotdqSpelling) {
    const fix = window.SotdqSpelling.correct(term);
    if (fix.changed && !(await hasRealHit(search, term))) {
      const retry = await pf.search(fix.term, opts);
      if (retry.results.length) { search = retry; searched = fix.term; correctedFrom = term; }
    }
  }

  const nothing = () => {
    resultsEl.innerHTML = '';
    metaEl.style.display = 'none';
    setState('No records found for "' + term + '"' + (scope ? ' in ' + SCOPE_LABELS[scope] : '') + '.');
  };
  if (!search.results.length) return nothing();

  const rawData = await Promise.all(search.results.slice(0, 30).map(r => r.data()));

  // Drop results whose only match is a stopword.
  const meaningful = searched.toLowerCase().split(/\\s+/).filter(Boolean).filter(w => !STOPWORDS.has(w));
  const data = rawData.filter(d => {
    if (!meaningful.length) return true;
    const marks = (d.excerpt.match(/<mark>(.*?)<\\/mark>/g) || [])
      .map(m => m.replace(/<\\/?mark>/g, '').trim().toLowerCase());
    if (marks.some(w => !STOPWORDS.has(w))) return true;
    const plain = d.excerpt.replace(/<\\/?mark>/g, '').toLowerCase();
    return meaningful.some(w => plain.includes(w));
  });
  if (!data.length) return nothing();

  clearState();
  metaEl.style.display = 'flex';
  countEl.textContent = data.length + (data.length === 1 ? ' record' : ' records');
  termEcho.textContent = '"' + searched + '"';
  if (correctedFrom) {
    const n = document.createElement('div');
    n.id = 'correction-note';
    n.className = 'search-correction';
    n.innerHTML = 'Showing results for <b>' + esc(searched) +
      '</b> \\u2014 nothing is filed under \\u201c' + esc(correctedFrom) + '\\u201d.';
    resultsEl.parentNode.insertBefore(n, resultsEl);
  }
  scopeEcho.textContent = scope ? 'in ' + SCOPE_LABELS[scope] : 'across all records';

  resultsEl.innerHTML = data.map(d => {
    const title = (d.meta && d.meta.title) ? d.meta.title : d.url;
    return `<a class="result" href="${d.url}">
      <div class="result-head">
        <div class="result-title">${title}</div>
        <div class="result-path">${sectionFromUrl(d.url)}</div>
      </div>
      <div class="result-snippet">${cleanExcerpt(d.excerpt)}</div>
    </a>`;
  }).join('');
}

qEl.addEventListener('input', () => { clearTimeout(debounce); debounce = setTimeout(run, 180); });
scopeEl.addEventListener('change', run);

const params = new URLSearchParams(location.search);
if (params.get('scope')) scopeEl.value = params.get('scope');
if (params.get('q')) { qEl.value = params.get('q'); run(); }
</script>
</body>
</html>
''' % (opts, json.dumps(labels))
    write(path, head(path, 'Search', 'search', extra) + body)


# ---------------------------------------------------------------------------
# HUB AND GATE
# ---------------------------------------------------------------------------

ICONS = {
    'journeys': '<svg viewBox="0 0 36 36" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M10 6h18a2 2 0 0 1 2 2v18a2 2 0 0 1-2 2H10"/><path d="M10 28a3 3 0 0 1 0-6V6a3 3 0 0 0 0 6"/><line x1="16" y1="12" x2="24" y2="12"/><line x1="16" y1="17" x2="24" y2="17"/><line x1="16" y1="22" x2="21" y2="22"/></svg>',
    'quests': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3h14v18l-7-4-7 4z"/><path d="M9 8h6M9 12h4"/></svg>',
    'embers': '<svg viewBox="0 0 36 36" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M18 31c-5.5 0-10-4.2-10-9.6 0-3.4 1.7-5.8 3.4-8 1.1-1.5 2-3.4 2.2-5.6 1.7 2.2 2.8 3.9 2.8 6.2 0 1.1-.3 2.2-1.1 3.3 2.2-1.1 3.9-3.3 3.9-6.1 1.7 2.8 3.3 6.1 3.3 10C22.5 26.5 20.4 31 18 31z"/></svg>',
    'dossiers': '<svg viewBox="0 0 36 36" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="11" r="4"/><path d="M10 29c0-4.4 3.6-8 8-8s8 3.6 8 8"/><circle cx="7" cy="13" r="3"/><path d="M2 28c0-3.3 2.2-6 5-6"/><circle cx="29" cy="13" r="3"/><path d="M34 28c0-3.3-2.2-6-5-6"/></svg>',
    'atlas': '<svg viewBox="0 0 36 36" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="18" r="13"/><polygon points="18,6 20,16 18,14 16,16" fill="currentColor" stroke="none" opacity="0.7"/><polygon points="18,30 16,20 18,22 20,20" stroke="none" fill="currentColor" opacity="0.35"/><line x1="18" y1="8" x2="18" y2="28"/><line x1="8" y1="18" x2="28" y2="18"/></svg>',
    'armory': '<svg viewBox="0 0 36 36" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="4" x2="18" y2="27"/><line x1="12" y1="22" x2="24" y2="22"/><path d="M15.5 27h5l-1 5h-3z"/><path d="M16 6l2-2 2 2"/></svg>',
    'intel': '<svg viewBox="0 0 36 36" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M18 4l12 5v12q0 9-12 13Q6 30 6 21V9z"/><path d="M18 11v14M12 17h12"/></svg>',
    'search': '<svg viewBox="0 0 36 36" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="16" cy="16" r="10"/><path d="M23.5 23.5L31 31"/></svg>',
    'road': '<svg viewBox="0 0 36 36" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M13 32L16 4M23 32L20 4"/><path d="M18 8v3M18 15v3M18 22v3M18 29v2" opacity="0.6"/></svg>',
}


def card(href, icon, title, desc, links):
    ls = ''.join('<a class="s-link%s" href="%s"%s>%s</a>'
                 % (' s-link-all' if all_ else '', h, (' id="%s"' % i) if i else '', e(t))
                 for h, t, all_, i in links)
    return ('<div class="s-card"><a class="s-card-overlay" href="%s" aria-label="%s"></a>'
            '<div class="s-card-head"><div class="s-icon">%s</div><div class="s-title">%s</div></div>'
            '<div class="s-desc">%s</div><div class="s-links">%s</div></div>'
            % (href, e(title), ICONS[icon], e(title), e(desc), ls))


def build_hub():
    latest = JBY[LATEST]
    newest_npc = get(STANDING['met'][0])
    company = [
        card('unexpected-journeys/index.html', 'journeys', 'Unexpected Journeys',
             'Every session on record: the brief account, the whole story and the recording, on one page.',
             [('unexpected-journeys/journey-%s.html' % pad(LATEST), 'Journey ' + pad(LATEST), False, 'js-latest'),
              ('unexpected-journeys/index.html', 'All Journeys', True, None)]),
        card('quests/index.html', 'quests', 'Quest Board',
             'What the Embers have taken on, and what is still hanging over them.',
             [('quests/index.html#threads', 'Open Threads', False, None),
              ('quests/index.html', 'Open Board', True, None)]),
        card('the-embers/index.html', 'embers', 'The Embers',
             'The company: who they are, what they are chasing, and what they carry.',
             [('the-embers/index.html', 'Meet the Company', True, None)]),
        card('dossiers/index.html', 'dossiers', 'Dossiers',
             'Allies, nobles, guild contacts and enemies. Every face the party has met, and a few they have only heard named.',
             [(url(newest_npc['ref']), newest_npc['name'], False, None),
              ('dossiers/index.html', 'All Dossiers', True, None)]),
        card('atlas/index.html', 'atlas', 'The Atlas',
             'Every road walked and every place worth marking, from Vogler to Kalaman and on.',
             [('atlas/kalaman.html', 'Kalaman', False, None), ('atlas/index.html', 'Open the Atlas', True, None)]),
        card('armory/index.html', 'armory', 'Armory',
             'Weapons, relics and keepsakes: what the Embers carry, and what it has cost them.',
             [('armory/the-emberwake-greataxe.html', 'The Emberwake', False, None),
              ('armory/index.html', 'Browse the Armory', True, None)]),
    ]
    war = [
        card('road-so-far/index.html', 'road', 'The Road So Far',
             'Where the party stands right now: position, open quests, and the timeline behind them.',
             [('road-so-far/index.html', 'Where We Stand', True, None)]),
        card('war-intel/index.html', 'intel', 'War Intel',
             'The Dragon Queen and her army, the knightly orders, High Sorcery and the guild.',
             [('war-intel/the-red-dragon-army.html', 'The Red Dragon Army', False, None),
              ('war-intel/index.html', 'Read Intel', True, None)]),
        card('search/index.html', 'search', 'Search the Record',
             'Pull the thread on anything you half remember. Misheard names are forgiven.',
             [('search/index.html', 'Open Search', True, None)]),
    ]
    body = '''<body data-pagefind-ignore>
<div class="hub">
  <div class="hub-head">
    {banner}
    <div class="hub-eyebrow">Command Post &middot; The Embers of Vogler</div>
    <h1 class="hub-title">{site}</h1>
    <div class="hub-sub">Everything the company knows, and everything it carries.</div>
  </div>

  <section class="hub-section">
    <div class="hub-section-head">
      <span class="hub-section-title">The Company</span>
      <span class="hub-section-desc">Yours: where you have been, who you have met, what you are chasing.</span>
    </div>
    <div class="card-grid">
{company}
    </div>
  </section>

  <section class="hub-section">
    <div class="hub-section-head">
      <span class="hub-section-title">The War</span>
      <span class="hub-section-desc">The wider world, and where you stand in it.</span>
    </div>
    <div class="card-grid">
{war}
    </div>
  </section>

  <div class="hub-footer">
    <b>{site}</b> &nbsp;&middot;&nbsp; {kicker} &nbsp;&middot;&nbsp; <a href="index.html">Return to the gate</a>
  </div>
</div>
<script>
(function () {{
  // data/journeys.js is the registry; keep the card on its latest entry.
  if (window.SOTDQ_JOURNEYS && SOTDQ_JOURNEYS.length) {{
    var latest = SOTDQ_JOURNEYS[SOTDQ_JOURNEYS.length - 1];
    var el = document.getElementById('js-latest');
    if (el && latest.path) {{ el.setAttribute('href', latest.path); el.textContent = 'Journey ' + latest.num; }}
  }}
}})();
</script>
</body>
</html>
'''.format(banner=embers_banner('', 'the-embers/index.html'), site=SITE, kicker=CAMPAIGN['kicker'], company='\n'.join(company), war='\n'.join(war))
    write('hub.html', head('hub.html', SITE, 'hub') + body)


GATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{site}</title>
<link rel="stylesheet" href="styles/base.css">
<style>
  body {{ overflow: hidden; }}
  .gate {{
    position: fixed; inset: 0;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    cursor: pointer; overflow: hidden;
  }}
  .gate-bg {{
    position: absolute; inset: 0; z-index: 0;
    background: url('{art}') center top / cover no-repeat;
    transition: transform 0.9s ease, filter 0.9s ease;
  }}
  .gate-bg::after {{
    content: ''; position: absolute; inset: 0;
    background:
      linear-gradient(to bottom, rgba(8,5,3,0.55) 0%, rgba(8,5,3,0.15) 24%, rgba(8,5,3,0.30) 52%, rgba(8,5,3,0.80) 80%, rgba(8,5,3,0.97) 100%),
      linear-gradient(to right, rgba(8,5,3,0.6) 0%, transparent 24%, transparent 76%, rgba(8,5,3,0.6) 100%);
  }}
  .gate-content {{
    position: relative; z-index: 2; text-align: center; padding: 0 1.5rem;
    animation: fadeUp 1.2s ease both;
    transition: opacity 0.55s ease, transform 0.55s ease;
  }}
  .gate-title {{
    font-family: 'Cinzel', serif; font-size: clamp(2.1rem, 6.4vw, 4.4rem);
    font-weight: 900; letter-spacing: 0.07em; line-height: 1.08; text-transform: uppercase;
    color: var(--text);
    text-shadow: 0 0 60px rgba(176,40,40,0.55), 0 2px 10px rgba(0,0,0,0.9);
    margin-bottom: 0.9rem;
  }}
  .gate-title span {{ color: var(--gold-light); }}
  .gate-tagline {{
    font-size: clamp(1rem, 2.5vw, 1.3rem); font-style: italic;
    color: var(--text-dim); letter-spacing: 0.04em; margin-bottom: 0.5rem;
    text-shadow: 0 1px 8px rgba(0,0,0,0.9);
  }}
  .gate-campaign {{
    font-family: 'Cinzel', serif; font-size: 0.888rem; letter-spacing: 0.3em;
    text-transform: uppercase; color: var(--text-dim); margin-bottom: 2rem;
  }}
  .gate-rule {{ display: flex; align-items: center; justify-content: center; gap: 0.8rem; color: var(--gold-dim); margin-bottom: 2.8rem; }}
  .gate-rule::before, .gate-rule::after {{ content: ''; width: 60px; height: 1px; background: linear-gradient(to right, transparent, var(--gold-dim)); }}
  .gate-rule::after {{ transform: scaleX(-1); }}
  .gate-enter {{
    display: inline-flex; align-items: center; gap: 0.9rem;
    font-family: 'Cinzel', serif; font-size: 0.845rem; letter-spacing: 0.28em; text-transform: uppercase;
    color: var(--gold); text-decoration: none; border: 1px solid var(--gold-dim);
    padding: 0.85rem 2.4rem; background: rgba(8,5,3,0.55);
    transition: border-color 0.25s, color 0.25s, background 0.25s, box-shadow 0.25s;
  }}
  .gate-enter:hover, .gate:hover .gate-enter {{
    border-color: var(--gold); color: var(--gold-light);
    background: rgba(201,150,63,0.08); box-shadow: 0 0 40px rgba(201,150,63,0.18);
  }}
  .gate-enter svg {{ width: 12px; }}
  .gate-hint {{
    margin-top: 1.4rem; font-family: 'Cinzel', serif; font-size: 0.766rem;
    letter-spacing: 0.22em; text-transform: uppercase; color: var(--text-muted);
    animation: pulse 3s ease-in-out infinite;
  }}
  body.entering .gate-content {{ opacity: 0; transform: translateY(-14px); }}
  body.entering .gate-bg {{ transform: scale(1.06); filter: brightness(0.35); }}
  @keyframes fadeUp {{ from {{ opacity:0; transform:translateY(22px); }} to {{ opacity:1; transform:translateY(0); }} }}
  @keyframes pulse {{ 0%,100% {{ opacity: 0.45; }} 50% {{ opacity: 0.9; }} }}
  @media (prefers-reduced-motion: reduce) {{
    .gate-content, .gate-hint {{ animation: none; }}
    .gate-bg, .gate-content {{ transition: none; }}
  }}
</style>
</head>
<body data-pagefind-ignore>
<div class="gate" id="js-gate">
  <div class="gate-bg"></div>
  <div class="gate-content">
    <h1 class="gate-title">Shadow of the<br><span>Dragon Queen</span></h1>
    <p class="gate-tagline">{tagline}</p>
    <p class="gate-campaign">{kicker}</p>
    <div class="gate-rule">&#10022;</div>
    <a class="gate-enter" href="hub.html" id="js-enter">
      Enter
      <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M2 6h8M7 3l3 3-3 3"/></svg>
    </a>
    <div class="gate-hint">Click anywhere or press any key</div>
  </div>
</div>
<script>
(function () {{
  var DEST = 'hub.html';
  var went = false;
  function enter() {{
    if (went) return;
    went = true;
    document.body.classList.add('entering');
    setTimeout(function () {{ window.location.href = DEST; }}, 380);
  }}
  document.getElementById('js-gate').addEventListener('click', enter);
  document.addEventListener('keydown', function (e) {{
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === 'Shift' || e.key === 'Tab') return;
    enter();
  }});
  var l = document.createElement('link');
  l.rel = 'prefetch'; l.href = DEST;
  document.head.appendChild(l);
}})();
</script>
</body>
</html>
'''


def build_gate():
    write('index.html', GATE.format(site=SITE, art=CAMPAIGN['gate_art'], tagline=e(CAMPAIGN['tagline']),
                                    kicker=e(CAMPAIGN['kicker'])))


# ---------------------------------------------------------------------------
# GUEST PLAYERS: one page, with none of the site's navigation on it. Two
# folding sections (the story, how the game works), then a tab per
# ready-made character, and a button that exports the lot as a PDF.
# Each character is laid out after the standard character sheet: abilities,
# saving throws and skills down the side; armor class, hit points, attacks,
# actions, spells and features beside them.
# Data: campaign_guests.py.
# Styling and the print layout: the "Guest players" block in styles/site.css.
# ---------------------------------------------------------------------------

ABILITIES = [('STR', 'Strength'), ('DEX', 'Dexterity'), ('CON', 'Constitution'),
             ('INT', 'Intelligence'), ('WIS', 'Wisdom'), ('CHA', 'Charisma')]
SKILLS = [('Acrobatics', 'DEX'), ('Animal Handling', 'WIS'), ('Arcana', 'INT'), ('Athletics', 'STR'),
          ('Deception', 'CHA'), ('History', 'INT'), ('Insight', 'WIS'), ('Intimidation', 'CHA'),
          ('Investigation', 'INT'), ('Medicine', 'WIS'), ('Nature', 'INT'), ('Perception', 'WIS'),
          ('Performance', 'CHA'), ('Persuasion', 'CHA'), ('Religion', 'INT'), ('Sleight of Hand', 'DEX'),
          ('Stealth', 'DEX'), ('Survival', 'WIS')]
GUEST_PROFICIENCY = 2   # every guest sheet is level 3


def signed(n):
    """A modifier for display, with a true minus sign."""
    n = int(n)
    return '+%d' % n if n >= 0 else '&minus;%d' % -n


def ticks(n, what, spent=0):
    """n boxes to tick as a limited use is spent. Plain checkboxes, no script."""
    return ''.join('<input class="g-tick" type="checkbox" aria-label="%s, use %d of %d"%s>'
                   % (e(what), i + 1, n, ' checked' if i < spent else '') for i in range(n))


def guest_numbers(s):
    """Everything on a sheet that follows from the ability scores."""
    mods = {k: (s['scores'][k] - 10) // 2 for k, _ in ABILITIES}
    half = GUEST_PROFICIENCY // 2 if s.get('jack') else 0
    for name in tuple(s['skills']) + tuple(s.get('expertise', ())):
        assert name in dict(SKILLS), 'unknown skill on the %s sheet: %s' % (s['slug'], name)
    saves = [(name, mods[k] + (GUEST_PROFICIENCY if k in s['saves'] else 0), k in s['saves'])
             for k, name in ABILITIES]
    skills = []
    for name, k in SKILLS:
        prof = name in s['skills']
        bonus = (GUEST_PROFICIENCY * 2 if name in s.get('expertise', ()) else
                 GUEST_PROFICIENCY if prof else half)
        skills.append((name, k, mods[k] + bonus, prof))
    return dict(mods=mods, saves=saves, skills=skills, init=mods['DEX'] + half)


def guest_rows(rows):
    """Named entries: a limited-use label and its boxes where there is one."""
    out = []
    for name, uses, n, text in rows:
        tag = ''
        if uses or n:
            tag = ' <span class="g-uses">%s%s</span>' % (
                e(uses), (' <span class="g-ticks">%s</span>' % ticks(n, name)) if n else '')
        out.append('<p class="g-row"><b>%s</b>%s %s</p>' % (e(name), tag, e(text)))
    return '<div class="g-rows">\n%s\n</div>' % '\n'.join(out)


def guest_spells(sp):
    rows = []
    for lbl, slots, spent, spells in sp['groups']:
        uses = ('<span class="g-uses">%d Slots <span class="g-ticks">%s</span></span>'
                % (slots, ticks(slots, lbl + ' slot', spent))) if slots else '<span class="g-uses">At will</span>'
        rows.append('<tr class="g-slot"><td colspan="5"><span class="g-group-title">%s</span>%s</td></tr>'
                    % (e(lbl), uses))
        for name, time, rng, save, effect in spells:
            rows.append('<tr><td>%s</td><td>%s</td><td>%s</td>'
                        '<td%s>%s</td><td>%s</td></tr>'
                        % (e(name), e(time), e(rng), '' if save else ' class="g-none"', e(save), e(effect)))
    conc = any(effect.startswith('Concentration') for _, _, _, spells in sp['groups'] for *_, effect in spells)
    return '''<div class="brief-heading">Spells</div>
<div class="g-cast">
  <div class="g-vital"><span class="g-val">{ability}</span><span class="g-key">Spellcasting Ability</span></div>
  <div class="g-vital"><span class="g-val">{dc}</span><span class="g-key">Spell Save DC</span></div>
  <div class="g-vital"><span class="g-val">{attack}</span><span class="g-key">Spell Attack Bonus</span></div>
</div>
<table class="g-table g-spells">
<thead><tr><th>Spell</th><th>Time</th><th>Range</th><th>Save / Atk</th><th>Effect</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
{note}'''.format(ability=e(sp['ability']), dc=e(sp['dc']), attack=e(sp['attack']), rows='\n'.join(rows),
                 note='<p class="g-hint">Concentration: you can hold one such spell at a time. Casting another ends the first.</p>'
                 if conc else '')


def guest_sheet(s, active=False):
    n = guest_numbers(s)
    scores = ''.join(
        '<div class="g-score"><span class="g-key">%s</span><span class="g-val">%s</span>'
        '<span class="g-score-num">%d</span></div>' % (e(name), signed(n['mods'][k]), s['scores'][k])
        for k, name in ABILITIES)

    def li(val, name, prof, sub=''):
        return ('<div class="g-li%s"><span class="g-dot"></span><span class="g-li-val">%s</span>'
                '<span class="g-li-name">%s</span><span class="g-li-tag">%s</span></div>'
                % (' is-prof' if prof else '', signed(val), e(name), sub))
    saves = ''.join(li(v, name, prof) for name, v, prof in n['saves'])
    skills = ''.join(li(v, name, prof, k.title()) for name, k, v, prof in n['skills'])
    attacks = ''.join(
        '<tr><td>%s</td><td data-label="Hit">%s</td><td data-label="Damage / Type">%s</td>'
        '<td data-label="Notes">%s</td></tr>\n' % (e(a), e(b), e(c), e(d)) for a, b, c, d in s['attacks'])
    actions = ['<p class="g-row g-std"><b>Standard Actions</b> Attack, Cast a Spell, Dash, Disengage, Dodge, '
               'Help, Hide.</p>']
    for group, rows in s['actions']:
        actions.append('<div class="g-group-title">%s</div>\n%s' % (e(group), guest_rows(rows)))
    features = ''
    if s['features']:
        features = ('<div class="brief-heading">Features &amp; Traits</div>\n%s'
                    % guest_rows([(a, '', 0, b) for a, b in s['features']]))
    return '''  <section class="account-panel g-sheet{on}" id="{slug}" data-panel="{slug}">
    <div class="account-body">
<div class="g-head">
  <div><div class="g-name">{name}</div><div class="g-pitch">&ldquo;{quote}&rdquo;</div></div>
  <div class="g-badges"><span class="log-badge">Level 3</span><span class="log-type-badge">{role}</span><span class="log-type-badge">{complexity}</span></div>
</div>
<div class="g-id">
  <div class="g-id-cell"><span class="g-id-val"></span><span class="g-key">Character Name</span></div>
  <div class="g-id-cell"><span class="g-id-val">{name} 3</span><span class="g-key">Class &amp; Level</span></div>
  <div class="g-id-cell"><span class="g-id-val"></span><span class="g-key">Species</span></div>
  <div class="g-id-cell"><span class="g-id-val"></span><span class="g-key">Player Name</span></div>
</div>
<p class="g-about">{about}</p>
<div class="g-strip">
  <div class="g-vital"><span class="g-val">{ac}</span><span class="g-key">Armor Class</span><span class="g-note">{ac_note}</span></div>
  <div class="g-vital"><span class="g-val">{init}</span><span class="g-key">Initiative</span></div>
  <div class="g-vital"><span class="g-val">{speed}</span><span class="g-key">Speed</span></div>
  <div class="g-vital g-hp">
    <div class="g-hp-cell"><span class="g-val">{hp}</span><span class="g-key">Max HP</span></div>
    <label class="g-hp-cell"><input type="number" inputmode="numeric" min="0" max="{hp}" placeholder="{hp}"><span class="g-key">Current HP</span></label>
    <label class="g-hp-cell"><input type="number" inputmode="numeric" min="0" placeholder="0"><span class="g-key">Temp HP</span></label>
  </div>
  <div class="g-vital g-hd"><span class="g-val">{hit_dice}</span><span class="g-key">Hit Dice</span></div>
</div>
<div class="g-cols">
<div class="g-side">
  <div class="g-scores">{scores}</div>
  <div class="g-lists">
    <div class="g-list"><div class="g-list-title">Saving Throws</div>{saves}</div>
    <div class="g-list"><div class="g-list-title">Skills</div>{skills}</div>
  </div>
</div>
<div class="g-main">
<div class="brief-heading">Weapon Attacks &amp; Cantrips</div>
<table class="g-table">
<thead><tr><th>Name</th><th>Hit</th><th>Damage / Type</th><th>Notes</th></tr></thead>
<tbody>
{attacks}</tbody>
</table>
<div class="brief-heading">Actions</div>
{actions}
{spells}
{features}
</div>
</div>
    </div>
  </section>'''.format(on=' is-active' if active else '', slug=s['slug'], name=e(s['name']), quote=e(s['quote']),
                       role=e(s['role']), complexity=e(s['complexity']), about=e(s['about']),
                       ac=e(s['ac']), ac_note=e(s['ac_note']), init=signed(n['init']), speed=e(s['speed']),
                       hp=e(s['hp']), hit_dice=e(s['hit_dice']),
                       scores=scores, saves=saves, skills=skills, attacks=attacks,
                       actions='\n'.join(actions),
                       spells=guest_spells(s['spells']) if s.get('spells') else '', features=features)


def build_guests():
    slugs = [g['slug'] for g in GUEST_PAGES]
    assert len(slugs) == len(set(slugs)), 'two guest pages share a slug'
    for g in GUEST_PAGES:
        build_guest_page(g)


def build_guest_page(g):
    story = '\n'.join('<p>%s</p>' % e(p) for p in g['story'])
    basics = '\n'.join('    <li><b>%s</b> %s</li>' % (e(a), e(b)) for a, b in g['basics'])
    # What to do on a turn, one line per character. It sits with the rules
    # so the sheets themselves stay to the numbers.
    turns = '\n'.join('<p class="g-row"><b>%s</b> %s</p>' % (e(s['name']), e(' '.join(s['turn'])))
                      for s in g['sheets'])
    video = ''
    if g.get('video'):
        video = ('<div class="video-block"><div class="video-container"><iframe '
                 'src="https://www.youtube.com/embed/%s" title="How to play" loading="lazy" allowfullscreen>'
                 '</iframe></div>\n<div class="video-link">Watch on YouTube: <a href="https://youtu.be/%s" '
                 'target="_blank" rel="noopener">youtu.be/%s</a></div></div>\n' % ((g['video'],) * 3))
    caret = ('<svg class="account-caret" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.8" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 2l4 4-4 4"/></svg>')
    tabs = []
    for i, s in enumerate(g['sheets']):
        tabs.append('''  <button class="account-tab%s" type="button" data-panel="%s" aria-selected="%s">
    <span class="account-tab-name">%s</span>
    <span class="account-tab-note">%s</span>
  </button>''' % (' is-active' if i == 0 else '', s['slug'], 'true' if i == 0 else 'false',
                  e(s['name']), e(s['role'])))
    content = '''<div class="g-tools">
  <button class="g-export" id="js-export" type="button"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 2v8M4.5 6.5L8 10l3.5-3.5M2.5 13.5h11"/></svg>Export PDF</button>
</div>
<details class="account g-fold" open>
  <summary>{caret}<span class="account-name">Who You Are</span><span class="account-note">Your part in the story</span></summary>
  <div class="account-body">
<div class="narrative">
{story}
</div>
  </div>
</details>
<details class="account g-fold" open>
  <summary>{caret}<span class="account-name">How to Play</span><span class="account-note">The basics</span></summary>
  <div class="account-body">
{video}{ease}<ul class="brief-list">
{basics}
</ul>
<div class="brief-heading">On Your Turn</div>
<p class="g-hint">A dependable turn for each character, for when you are unsure what to do.</p>
<div class="g-rows g-turns">
{turns}
</div>
  </div>
</details>
<div class="section-label">Choose Your Character</div>
<p class="g-choose">{choose}</p>
<div class="account-tabs">
{tabs}
</div>
<div class="account-panels">
{sheets}
</div>'''.format(caret=caret, story=story, video=video, basics=basics, turns=turns, choose=e(g['choose']),
                 ease=('<p class="g-ease">%s</p>\n' % e(g['ease'])) if g.get('ease') else '',
                 tabs='\n'.join(tabs),
                 sheets='\n'.join(guest_sheet(s, i == 0) for i, s in enumerate(g['sheets'])))
    # Export is the browser's own print-to-PDF, laid out by the print rules in
    # site.css. Folded sections are opened for the print and put back after,
    # which also covers a plain Ctrl+P.
    tail = '''<script>
(function () {
  var folds = document.querySelectorAll('details.g-fold'), was = null;
  window.addEventListener('beforeprint', function () {
    if (was) return;
    was = []; folds.forEach(function (d) { was.push(d.open); d.open = true; });
  });
  window.addEventListener('afterprint', function () {
    if (!was) return;
    folds.forEach(function (d, i) { d.open = was[i]; }); was = null;
  });
  var btn = document.getElementById('js-export');
  if (btn) btn.addEventListener('click', function () { window.print(); });
})();
</script>
'''
    # nav=False: a guest gets the page and nothing else. The sidebar and the
    # command bar belong to the party's record, which is not theirs to wade through.
    page('guests/%s.html' % g['slug'], g['title'], 'guest', 'guests', content, eyebrow=g['eyebrow'],
         subtitle=g['subtitle'], body_class='guest-page', tail=tail, nav=False)


# ---------------------------------------------------------------------------
# REDIRECTS for addresses that were shared before the restructure
# ---------------------------------------------------------------------------

STUB = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={to}">
<link rel="canonical" href="{to}">
<title>Moved &middot; Shadow of the Dragon Queen</title>
</head>
<body data-pagefind-ignore style="background:#0a0704;color:#efe4d0;font-family:Georgia,serif;padding:2rem;">
<p>This page has moved. <a href="{to}" style="color:#e6bd72;">Continue</a>.</p>
<script>location.replace({js});</script>
</body>
</html>
'''


def stub(path, to):
    write(path, STUB.format(to=to, js=json.dumps(to)))


def build_stubs():
    for j in JOURNEYS:
        k = pad(j['num'])
        if j['num'] > 9:
            continue          # only 001-009 ever existed at the old addresses
        stub('unexpected-journeys/unexpected-journey-brief-account/unexpected-journey-brief-account-%s.html' % k,
             '../journey-%s.html#brief' % k)
        stub('unexpected-journeys/unexpected-journey-full-account/unexpected-journey-full-account-%s.html' % k,
             '../journey-%s.html#full' % k)
    stub('command-post/index.html', '../hub.html')
    stub('field-manual/index.html', '../hub.html')
    stub('theatre-of-war/index.html', '../atlas/index.html')
    stub('quests/fire-and-frost.html', 'the-leviathan-axe.html')            # renamed after Journey 010
    stub('dossiers/the-pale-elven-woman.html', 'the-pale-woman.html')       # renamed pages keep their old addresses
    stub('armory/leeching-bolts.html', 'leeching-arrows.html')
    stub('armory/armor-of-bone.html', 'armor-of-the-fallen.html')
    stub('atlas/the-reliquary-of-sir-cthondor.html', 'the-radiant-reliquary.html')
    stub('armory/divine-pendant.html', 'amulet-of-paladine.html')
    stub('armory/periapt-from-the-cliffside.html', 'periapt-of-wound-closure.html')
    stub('armory/blue-gemmed-ring.html', 'ring-of-protection.html')


# ---------------------------------------------------------------------------
# DATA FILES the pages read at runtime
# ---------------------------------------------------------------------------

def js(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)


def build_data():
    s = STANDING
    j = JBY[s['journey']]
    quests = []
    for slug in s['quests']:
        q = get('quest:' + slug)
        pr = progress(q)
        quests.append({'name': q['name'], 'progress': ('%d/%d' % pr) if pr else '',
                       'href': 'quests/%s.html' % slug})
    standing = {
        'journey': j['num'], 'title': j['title'], 'position': s['position'], 'posNote': s['pos_note'],
        'outstanding': s['outstanding'],
        'detail': {'consequence': s['consequence'], 'quests': quests,
                   'met': [{'name': label(t), 'href': url(t)} for t in s['met']]},
        'links': {'standing': 'road-so-far/index.html',
                  'journey': 'unexpected-journeys/journey-%s.html' % pad(j['num']),
                  'scheduler': CAMPAIGN['scheduler']},
    }
    write('data/standing.js',
          '/**\n * Shadow of the Dragon Queen - Where the Party Stands\n'
          ' * Powers the command bar that scripts/nav.js puts at the top of every page.\n'
          ' * Written by _build/build.py from STANDING in campaign_world.py.\n */\n'
          'window.SOTDQ_STANDING = %s;\n' % js(standing))

    reg = [{'num': pad(x['num']), 'title': x['title'],
            'path': 'unexpected-journeys/journey-%s.html' % pad(x['num'])} for x in JOURNEYS]
    write('data/journeys.js',
          '/**\n * Shadow of the Dragon Queen - Journey Registry\n'
          ' * One entry per session, oldest first. The hub card follows the last one.\n'
          ' * Written by _build/build.py from JOURNEYS in campaign_world.py.\n */\n'
          'var SOTDQ_JOURNEYS = %s;\n' % js(reg))

    words = set(EXTRA_VOCAB)
    names = [r['name'] for r in REG.values()] + [n for n, _ in UNFILED] + [x['title'] for x in JOURNEYS]
    for r in REG.values():
        names += r.get('aliases', [])
        names += [a for a, _ in r.get('sites', [])]
    stop = {'the', 'of', 'and', 'to', 'for', 'from', 'a', 'in', 'on', 'at', 'with', 'after', 'over', 'beneath'}
    for n in names:
        for w in re.findall(r"[A-Za-z][A-Za-z'\-]+", n):
            w = w.strip("'-")
            if len(w) >= 4 and w.lower() not in stop:
                words.add(w[0].upper() + w[1:])
    write('data/vocabulary.js',
          '/**\n * Shadow of the Dragon Queen - Search Vocabulary\n'
          ' * Proper nouns the search uses to repair a query that returned nothing,\n'
          ' * for names a player only ever heard spoken aloud.\n'
          ' * Written by _build/build.py; add extras to EXTRA_VOCAB in campaign_world.py.\n */\n'
          'var SOTDQ_VOCAB = %s;\n' % js(sorted(words, key=str.lower)))


# ---------------------------------------------------------------------------

def main():
    build_journeys()
    build_embers()
    build_dossiers()
    build_atlas()
    build_armory()
    build_war_intel()
    build_quests()
    build_road()
    build_search()
    build_hub()
    build_gate()
    build_guests()
    build_stubs()
    build_data()
    print('%d files written' % len(written))


if __name__ == '__main__':
    main()
