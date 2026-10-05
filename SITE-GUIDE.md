# Shadow of the Dragon Queen: Site Guide

The player-facing companion site. Structure, stylesheets and interaction are
ported from the Caelestis site and re-skinned in crimson and bronze.

## One-time setup

Search is built by a GitHub Action, so Pages has to publish from the Action:

**Repo > Settings > Pages > Build and deployment > Source > "GitHub Actions"**

Until that is switched, everything works except the search page, which says
its index is not available yet.

## Layout

| Path | What it is | Caelestis equivalent |
|---|---|---|
| `index.html` | Gate | `index.html` |
| `hub.html` | Command Post | `hub.html` |
| `unexpected-journeys/` | One page per session: glance, brief, full, recording | `voyages/` |
| `road-so-far/` | Where the party stands, with the timeline | `bearings/` |
| `quests/` | Quest Board: quests, threads, closed | `quests/` |
| `the-embers/` | The party | `crew-manifest/` |
| `dossiers/` | NPCs | `dossiers/` |
| `atlas/` | Places | `navigation-records/` |
| `armory/` | Items | `inventory/` |
| `war-intel/` | Factions and powers | `factions/` |
| `search/` | Search, with misspelling repair | `search/` |
| `guests/` | One page for guest players: the story, how to play, and a tab per ready-made character. Sent as a direct link. It has no sidebar or command bar of its own, and is left out of the sidebar and the search index | none |
| `images/` | The Embers' banner, made by the players. Shown on the hub and The Embers page | none |

Old addresses redirect: the brief and full account pages, `command-post/`,
`field-manual/` and `theatre-of-war/`.

## Where things are edited

| To change | Edit | Then |
|---|---|---|
| A person, place, item, quest or faction | `_build/campaign_people.py` or `_build/campaign_world.py` | run the build |
| A journey's account | `_build/journeys/NNN.brief.html`, `NNN.full.html` | run the build |
| The command bar strip | `STANDING` in `_build/campaign_world.py` | run the build |
| The guest page: story, basics, character sheets, video | `_build/campaign_guests.py` | run the build |
| Sidebar sections, scheduler link | `scripts/nav.js` | nothing |
| Site-specific styling | `styles/site.css` | nothing |

```
python3 _build/build.py
```

The pages are static and committed. Nothing runs the build on deploy; the
Action only builds the search index and publishes. A page can be hand-edited,
but the next build overwrites it, so put the change in the data instead.

## Adding a session

1. Write `_build/journeys/012.brief.html` and `012.full.html`.
2. Add the `JOURNEYS` entry in `campaign_world.py`.
3. Add a `12:` line under `records` for everyone and everything it touched,
   and bump their `last`.
4. Update `QUESTS` (objectives, new threads, anything closed) and `STANDING`.
5. Run the build, look at it locally, commit.

## Stylesheets

| File | Source | Edit by hand? |
|---|---|---|
| `styles/base.css` | Caelestis `caelestis.css`, recoloured | No |
| `styles/entity.css`, `board.css`, `register.css` | Caelestis, recoloured | No |
| `styles/standing.css` | Caelestis `bearing.css` | No |
| `styles/journey.css`, `hub.css` | Lifted from Caelestis page `<style>` blocks | No |
| `styles/site.css` | This site only. Loaded last everywhere | Yes |

To bring over a later Caelestis change:

```
python3 _build/port_from_caelestis.py /path/to/caelestis
```

Class names are kept exactly as Caelestis has them (`voyage-nav-bar`,
`cae-lightbox`), which is what keeps that a copy and a recolour. The palette
lives in the `TOKENS` block of the port script.

## Spoiler rules the data follows

- Player-known framing only. Source is the tracker's player tabs and the
  Unexpected Journey accounts. The Prep Queue and the "Next Planned Beat"
  column are never used.
- Unidentified figures stay unidentified (the charred swordswoman, the pale
  woman).
- A name with nothing behind it goes under Named, Unfiled on the Dossiers
  page and gets no page of its own.
- Anything named at the table is player-facing, and items carry the name
  they were given at the table.

## DM side

`_dm/` holds DM-only notes. It lives in the repo and is left out of the
published site: the deploy removes it, and the leading underscore keeps a
branch-based Pages build from serving it. The repo is public, so the folder
is still readable on GitHub. Nothing in `_dm/` is used by the build.

This guide is left out of the published site as well, because it says where
the DM notes are.

## Checking a change locally

```
python3 -m http.server 8000        # from the folder ABOVE the repo
# open http://localhost:8000/shadow-of-the-dragon-queen/

# search, same command the Action runs:
npx -y pagefind --site . \
  --glob "{unexpected-journeys/journey-*.html,unexpected-journeys/index.html,road-so-far/*.html,quests/*.html,the-embers/*.html,dossiers/*.html,atlas/*.html,armory/*.html,war-intel/*.html}" \
  --exclude-selectors "[data-pagefind-ignore], nav, footer"
```

`pagefind/` is git-ignored. The Action rebuilds it on every push.

## The guest page

`guests/index.html` is for people sitting in for a session. It is the one
page built with `nav=False`, so it loads no sidebar and no command bar. Each
tab has its own address (`guests/#fighter`, `guests/#bard`), so one character
can be sent on its own.

Export PDF opens the browser's print dialog; choose Save as PDF there. The
result is the story and How to Play on the first sheet, then every character
on a sheet of its own, in ink on white. The rules for that are the print
block at the end of `styles/site.css`.

Each character follows the standard character sheet. Ability modifiers,
saving throws, the full skill list, initiative and passive Perception are
worked out by the build from the scores and proficiencies in the data;
attack and spell numbers are entered by hand.

To reuse it for another session, rewrite `title`, `subtitle` and `story` in
`_build/campaign_guests.py`. Set `video` there to a YouTube id to put a
how-to-play video at the top of the How to Play section.
