#!/usr/bin/env python3
"""
port_from_caelestis.py - bring the Caelestis stylesheets and shared scripts
across, re-skinned for Shadow of the Dragon Queen.

    python3 _build/port_from_caelestis.py /path/to/caelestis

Reads  : <caelestis>/styles/{caelestis,entity,board,register,bearing}.css
         <caelestis>/scripts/{ui,spelling}.js
Writes : styles/{base,entity,board,register,standing}.css
         styles/{journey,hub}.css   (lifted from page <style> blocks)
         scripts/{ui,spelling}.js

Class names are left exactly as Caelestis has them (voyage-nav-bar, cae-lightbox
and so on). That is deliberate: it keeps this a straight copy plus a recolour,
so a fix made on Caelestis can be brought over by running this again rather
than by hand. Only three things change:

  1. the :root token block           - crimson and bronze instead of steel
  2. the backdrop                    - embers drawn in CSS instead of a nebula
  3. a handful of hard-coded colours - listed in SWEEP below

scripts/nav.js is NOT ported. It is written for this site (its own sections,
its own command bar) and is edited by hand.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FILES = {
    'styles/caelestis.css': 'styles/base.css',
    'styles/entity.css':    'styles/entity.css',
    'styles/board.css':     'styles/board.css',
    'styles/register.css':  'styles/register.css',
    'styles/bearing.css':   'styles/standing.css',
    'scripts/ui.js':        'scripts/ui.js',
    'scripts/spelling.js':  'scripts/spelling.js',
}

HEADER = """/* =======================================================
   SHADOW OF THE DRAGON QUEEN - Shared Design System
   Ported from the Caelestis site by _build/port_from_caelestis.py.
   Do not hand-edit the ported sheets; put site-specific rules in
   styles/site.css, which every page loads last.
   ======================================================= */
"""

TOKENS = """:root {
  /* -- Backgrounds: scorched iron -- */
  --bg:          #0a0704;
  --bg-deep:     #060403;
  --bg-panel:    rgba(26, 18, 12, 0.92);
  --bg-card:     rgba(31, 22, 15, 0.90);
  --bg-raised:   rgba(48, 34, 23, 0.80);

  /* -- Rules: parchment, held faint -- */
  --rule:        rgba(214, 186, 146, 0.15);
  --rule-soft:   rgba(214, 186, 146, 0.08);

  /* -- Bronze: the warm accent. Names stay --gold-* so every ported
        rule follows without edits. -- */
  --gold:        #c9963f;
  --gold-light:  #e6bd72;
  --gold-dim:    #94692a;
  --gold-faint:  rgba(201, 150, 63, 0.10);
  --gold-rule:   rgba(201, 150, 63, 0.30);

  /* -- Crimson: wayfinding, links, hover. Names stay --ice-*. -- */
  --ice:         #d0574a;
  --ice-light:   #ec8d7c;
  --ice-dim:     #8f2a22;
  --ice-faint:   rgba(176, 40, 40, 0.12);

  /* -- Steel: held in reserve for a third state. Names stay --violet-*. -- */
  --violet:      #9aa7b4;
  --violet-dim:  #66727e;

  /* -- Text: four tiers on warm parchment -- */
  --text:        #efe4d0;
  --text-soft:   #dccdb4;
  --text-dim:    #c7b79d;
  --text-muted:  #a39379;
  --text-faint:  #7d6e5a;

  /* Veil over the backdrop. The one dial for how much ember shows through. */
  --veil-centre: rgba(10, 7, 4, 0.20);
  --veil-edge:   rgba(6, 4, 3, 0.58);

  /* -- Rank colours (unused here, kept so ported rules resolve) -- */
  --cadet:       #b04a4a;
  --sailor:      #9aa7b4;
  --officer:     #c9963f;
  --bridge:      #c9963f;

  /* -- Misc -- */
  --radius:      0;
}"""

# The Caelestis backdrop is a photograph. This one is drawn: a low red glow as
# if the horizon were burning, bronze haze high on the right, and a scatter of
# sparks. No image to host, nothing to fail to load.
BACKDROP = """body::before {
  content: ''; position: fixed; inset: 0; z-index: -2;
  background:
    radial-gradient(120% 70% at 18% 108%, rgba(150, 34, 22, 0.55) 0%, rgba(96, 22, 14, 0.28) 38%, transparent 68%),
    radial-gradient(90% 60% at 88% 104%, rgba(168, 84, 24, 0.30) 0%, transparent 62%),
    radial-gradient(70% 50% at 82% -8%, rgba(120, 82, 34, 0.22) 0%, transparent 70%),
    radial-gradient(60% 45% at 8% -6%, rgba(70, 22, 18, 0.30) 0%, transparent 72%),
    linear-gradient(to bottom, #0b0806 0%, #0a0705 55%, #120a07 100%);
}
body::after {
  content: ''; position: fixed; inset: 0; z-index: -1; pointer-events: none;
  /* Sparks first so they sit above the veil. */
  background-image:
    radial-gradient(1.5px 1.5px at 8%  72%, #ffb36699 0%, transparent 100%),
    radial-gradient(1px   1px   at 22% 58%, #ff9a4d66 0%, transparent 100%),
    radial-gradient(2px   2px   at 31% 86%, #ffc680aa 0%, transparent 100%),
    radial-gradient(1px   1px   at 44% 64%, #ff8a3d55 0%, transparent 100%),
    radial-gradient(1.5px 1.5px at 57% 91%, #ffb36688 0%, transparent 100%),
    radial-gradient(1px   1px   at 66% 49%, #ffd9a044 0%, transparent 100%),
    radial-gradient(2px   2px   at 74% 78%, #ff9a4d99 0%, transparent 100%),
    radial-gradient(1px   1px   at 83% 61%, #ffb36655 0%, transparent 100%),
    radial-gradient(1.5px 1.5px at 91% 88%, #ffc68088 0%, transparent 100%),
    radial-gradient(1px   1px   at 14% 41%, #ffd9a033 0%, transparent 100%),
    radial-gradient(1px   1px   at 38% 33%, #ffb36633 0%, transparent 100%),
    radial-gradient(1px   1px   at 61% 24%, #ffd9a02e 0%, transparent 100%),
    radial-gradient(1px   1px   at 88% 31%, #ff9a4d33 0%, transparent 100%),
    radial-gradient(1px   1px   at 4%  18%, #ffd9a022 0%, transparent 100%),
    radial-gradient(1px   1px   at 51% 12%, #ffb36622 0%, transparent 100%),
    radial-gradient(ellipse at 50% 45%, var(--veil-centre) 50%, var(--veil-edge) 100%);
  background-repeat: no-repeat;
}"""

# Hard-coded colours that sit outside the token block. Regexes, so spacing
# inside rgba() does not matter.
def rgba(r, g, b):
    return re.compile(r'rgba\(\s*%d\s*,\s*%d\s*,\s*%d\s*,' % (r, g, b))

SWEEP = [
    (rgba(201, 153, 58), 'rgba(201, 150, 63,'),   # the old Caelestis gold
    (rgba(192, 134, 82), 'rgba(201, 150, 63,'),   # the newer ember
    (rgba(6, 4, 14),     'rgba(8, 5, 3,'),        # violet-black fills
    (rgba(8, 6, 16),     'rgba(8, 5, 3,'),
    (rgba(7, 10, 18),    'rgba(9, 6, 4,'),        # the content scrim
    (rgba(3, 5, 10),     'rgba(4, 2, 1,'),
    (rgba(6, 9, 15),     'rgba(8, 5, 3,'),
    (rgba(18, 21, 31),   'rgba(22, 15, 10,'),
    (rgba(74, 127, 176), 'rgba(176, 60, 50,'),    # npc chips: steel blue -> crimson
    (rgba(30, 74, 122),  'rgba(176, 60, 50,'),
    (rgba(90, 45, 130),  'rgba(140, 150, 162,'),  # place chips: violet -> steel
    (rgba(138, 99, 184), 'rgba(140, 150, 162,'),
    (rgba(150, 131, 196),'rgba(140, 150, 162,'),
    (rgba(111, 158, 201),'rgba(176, 60, 50,'),
    (rgba(130, 168, 210),'rgba(214, 186, 146,'),
    (re.compile(r'#7aaad0', re.I), '#ec8d7c'),
    (re.compile(r'#08060f', re.I), '#080503'),
    (re.compile(r'#0a0814', re.I), '#0a0705'),
    (re.compile(r'#0a0a14', re.I), '#0a0705'),
    (re.compile(r'#33405c', re.I), '#3a2a1c'),
    (re.compile(r'#9683c4', re.I), '#9aa7b4'),
    (re.compile(r'#b6a6dc', re.I), '#c3ccd5'),
    (re.compile(r'#6f5f9c', re.I), '#66727e'),
    (re.compile(r'#453a63', re.I), '#3a424a'),
]

# Rules Caelestis keeps in a page's own <style> block. They are lifted into
# real stylesheets here so a page type cannot lose them.
PAGE_STYLES = {
    'voyages/voyage-004.html': 'styles/journey.css',
    'hub.html':                'styles/hub.css',
}

JS_RENAMES = [
    ('CAELESTIS_VOCAB', 'SOTDQ_VOCAB'),
    ('CaelestisSpelling', 'SotdqSpelling'),
]


def reskin_base(css):
    # header
    css = re.sub(r'\A/\*.*?\*/\n', HEADER, css, count=1, flags=re.S)
    # token block
    css, n = re.subn(r':root\s*\{.*?\n\}', lambda m: TOKENS, css, count=1, flags=re.S)
    assert n == 1, 'token block not found'
    # backdrop: everything from body::before through the end of body::after
    # (and the comment above it, which describes the photograph)
    css, n = re.subn(r'(?:/\* Fixed starfield.*?\*/\s*)?body::before\s*\{.*?\}\s*(?:/\*.*?\*/\s*)?body::after\s*\{.*?\n\}',
                     lambda m: BACKDROP, css, count=1, flags=re.S)
    assert n == 1, 'backdrop block not found'
    assert 'url(' not in css.split('@import', 1)[-1].split(';', 1)[-1], 'an image reference survived'
    return css


def sweep(css):
    for pat, rep in SWEEP:
        css = pat.sub(rep, css)
    return css


def braces(s):
    return s.count('{'), s.count('}')


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1]).resolve()
    for a, b in FILES.items():
        text = (src / a).read_text(encoding='utf-8')
        before = braces(text)
        if b.endswith('.css'):
            if b == 'styles/base.css':
                text = reskin_base(text)
            text = sweep(text)
            o, c = braces(text)
            assert o == c, '%s: brace mismatch %d/%d' % (b, o, c)
        else:
            for old, new in JS_RENAMES:
                text = text.replace(old, new)
            assert braces(text) == before, '%s: brace count changed' % b
        out = ROOT / b
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8')
        print('%-24s -> %-22s %6d bytes' % (a, b, len(text.encode('utf-8'))))

    for a, b in PAGE_STYLES.items():
        html = (src / a).read_text(encoding='utf-8')
        blocks = re.findall(r'<style>(.*?)</style>', html, flags=re.S)
        assert blocks, '%s: no <style> block' % a
        css = '/* Lifted from the <style> block of Caelestis %s by\n   _build/port_from_caelestis.py. Do not hand-edit. */\n' % a
        css += sweep('\n'.join(blocks))
        o, c = braces(css)
        assert o == c, '%s: brace mismatch %d/%d' % (b, o, c)
        (ROOT / b).write_text(css, encoding='utf-8')
        print('%-24s -> %-22s %6d bytes' % (a, b, len(css.encode('utf-8'))))


if __name__ == '__main__':
    main()
