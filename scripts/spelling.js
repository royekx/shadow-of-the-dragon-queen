/* ═══════════════════════════════════════════════════════════
   spelling.js — query repair for S.E.A.R.C.H.

   Pagefind matches prefixes and stems; it does not match
   misspellings. A player who only ever heard "Sor'kur" spoken
   aloud types "Sorker" and gets nothing back.

   This corrects the query instead of stuffing hidden keywords
   into pages. Loaded before search.js and before the terminal.

     window.SotdqSpelling.correct(term)
       → { term, changed, from }

   Correction is a fallback, not a filter. Both surfaces run the
   query as typed first and only fall back to the repaired term
   when the original returns nothing — so a real word is never
   quietly rewritten out from under someone.

   The vocabulary lives in data/vocabulary.js.
   ═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  function bare(w) {
    return String(w).toLowerCase().replace(/[^a-z0-9]/g, '');
  }

  // Damerau-Levenshtein: counts a transposition as one edit, which is
  // what "Ostkek" for "Ostekk" actually is.
  function distance(a, b) {
    var la = a.length, lb = b.length;
    if (!la) return lb;
    if (!lb) return la;
    if (Math.abs(la - lb) > 2) return 99;

    var d = [], i, j;
    for (i = 0; i <= la; i++) { d[i] = [i]; }
    for (j = 0; j <= lb; j++) { d[0][j] = j; }

    for (i = 1; i <= la; i++) {
      for (j = 1; j <= lb; j++) {
        var cost = a.charAt(i - 1) === b.charAt(j - 1) ? 0 : 1;
        d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost);
        if (i > 1 && j > 1 &&
            a.charAt(i - 1) === b.charAt(j - 2) &&
            a.charAt(i - 2) === b.charAt(j - 1)) {
          d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + cost);
        }
      }
    }
    return d[la][lb];
  }

  function vocabulary() {
    return (typeof window !== 'undefined' && window.SOTDQ_VOCAB) || [];
  }

  // Longer words tolerate more damage before the match stops being credible.
  function tolerance(len) {
    if (len < 4) return 0;
    if (len <= 5) return 1;
    if (len <= 9) return 2;
    return 3;
  }

  function fixWord(word) {
    var key = bare(word);
    if (key.length < 4) return null;

    var vocab = vocabulary(), i, best = null, bestScore = 99;

    for (i = 0; i < vocab.length; i++) {
      var target = bare(vocab[i]);
      if (!target) continue;
      if (target === key) return null;              // already correct
      if (target.indexOf(key) === 0) return null;   // a prefix Pagefind handles
      var score = distance(key, target);
      if (score < bestScore) { bestScore = score; best = vocab[i]; }
    }

    if (best && bestScore <= tolerance(key.length)) return best;
    return null;
  }

  function correct(term) {
    var words = String(term).split(/(\s+)/);
    var changed = false;

    var fixed = words.map(function (w) {
      if (/^\s*$/.test(w)) return w;
      var lead = (w.match(/^[^A-Za-z0-9]*/) || [''])[0];
      var tail = (w.match(/[^A-Za-z0-9]*$/) || [''])[0];
      var core = w.slice(lead.length, w.length - tail.length || undefined);
      var fix = fixWord(core);
      if (!fix) return w;
      changed = true;
      return lead + fix + tail;
    }).join('');

    return { term: changed ? fixed : term, changed: changed, from: term };
  }

  window.SotdqSpelling = { correct: correct, distance: distance };
})();
