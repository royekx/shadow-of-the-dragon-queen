from html.parser import HTMLParser
css = open('style.css').read()
extra = """
/* Session 012 run-sheet additions */
p.lead { font-size: 10pt; line-height: 1.5; margin-bottom: 3pt; }
.slot-v.opt { color: #444; font-size: 8.5pt; }
p.small { font-size: 8pt; line-height: 1.45; color: #333; margin: 3pt 0 0; }
p.small9 { font-size: 8.5pt; line-height: 1.5; }
.twoup { display: grid; grid-template-columns: 1fr 1fr; gap: 12pt; align-items: start; }
.cb { display: inline-block; width: 8pt; height: 8pt; border: 0.9pt solid #58180D; border-radius: 1pt; flex-shrink: 0; vertical-align: -1pt; background: #fff; }
.cb.lg { width: 14pt; height: 14pt; border-width: 1.1pt; vertical-align: middle; }
.bt { display: flex; gap: 6pt; align-items: flex-start; font-size: 9pt; line-height: 1.42; margin-bottom: 2.8pt; page-break-inside: avoid; break-inside: avoid; }
.bt .cb { margin-top: 2.2pt; }
.bt.opt { color: #444; font-size: 8.5pt; }
.bt.opt .cb { border-radius: 50%; border-color: #999; }
.bt.dot .cb { width: 4pt; height: 4pt; border-radius: 50%; background: #58180D; margin-top: 4.2pt; }
.slot { display: grid; grid-template-columns: 52pt 1fr; gap: 6pt; margin: 3pt 0; }
.slot-l { font-family: 'Arial Narrow', Arial, sans-serif; font-size: 7pt; font-weight: bold; letter-spacing: 1.5px; text-transform: uppercase; color: #58180D; padding-top: 2pt; }
.slot-v { font-size: 9pt; line-height: 1.42; }
.scene-card { page-break-inside: auto; break-inside: auto; }
.scene-header { page-break-after: avoid; break-after: avoid; }
.dm-note, .read-aloud, .ref-table tr, .misc-item, .slot { page-break-inside: avoid; break-inside: avoid; }
.section-label { page-break-after: avoid; break-after: avoid; }
/* gifts master table */
.gifts { font-size: 8.9pt; table-layout: fixed; }
.gifts th { font-size: 8pt; letter-spacing: 2px; padding: 4pt 6pt; }
.gifts td { padding: 4pt 6pt; line-height: 1.4; }
.gifts th:first-child, .gifts td.rl { width: 13%; }
td.rl { font-family: 'Arial Narrow', Arial, sans-serif; font-size: 7pt; font-weight: bold; letter-spacing: 1.2px; text-transform: uppercase; color: #58180D; white-space: nowrap; padding-top: 5pt; }
.ref-table th.g-black { color: #1a1a1a; border-bottom: 2.5pt solid #1a1a1a; }
.ref-table th.g-red { color: #A32D2D; border-bottom: 2.5pt solid #A32D2D; }
.ref-table th.g-white { color: #666; border-bottom: 2.5pt solid #b5b5b5; }
/* clock */
.clock td { font-size: 9.2pt; padding: 3pt 5pt; }
.clock td.t { width: 34pt; font-family: 'Arial Narrow', Arial, sans-serif; font-weight: bold; color: #58180D; }
.clock td.m { width: 26pt; text-align: right; color: #666; }
/* scene 3 pulls */
.pulls { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6pt; margin-top: 6pt; }
.pull { border: 0.5pt solid #bbb; border-radius: 3pt; padding: 0 6pt 5pt; page-break-inside: avoid; break-inside: avoid; }
.pull p { font-size: 8.5pt; line-height: 1.4; margin-bottom: 3.5pt; }
.pull-h { font-family: 'Arial Narrow', Arial, sans-serif; font-size: 8.5pt; font-weight: bold; letter-spacing: 2px; text-transform: uppercase; margin: 0 -6pt 5pt; padding: 4pt 6pt 3pt; display: flex; justify-content: space-between; align-items: center; }
.pull-h.g-black { color: #1a1a1a; border-bottom: 2.5pt solid #1a1a1a; }
.pull-h.g-red { color: #A32D2D; border-bottom: 2.5pt solid #A32D2D; }
.pull-h.g-white { color: #666; border-bottom: 2.5pt solid #b5b5b5; }
.cbs { font-size: 6.5pt; letter-spacing: 1px; color: #666; }
.mini-sb { border: 0.75pt solid #58180D; border-radius: 2pt; padding: 3pt 5pt; font-size: 8.5pt; line-height: 1.4; margin: 4pt 0; }
.ifs td { font-size: 8.5pt; padding: 2.2pt 5pt; }
.ifs td:first-child { width: 32%; font-weight: bold; }
/* finale */
.win { border: 1.5pt solid #58180D; border-radius: 3pt; padding: 4pt 9pt; margin: 5pt 0; page-break-inside: avoid; break-inside: avoid; }
.win-l { font-family: 'Arial Narrow', Arial, sans-serif; font-size: 7pt; font-weight: bold; letter-spacing: 2.5px; text-transform: uppercase; color: #58180D; }
.win-v { font-size: 11.5pt; line-height: 1.4; margin: 1pt 0 2pt; }
.win-s { font-size: 8pt; color: #444; font-style: italic; }
.grid td, .grid th { text-align: center; vertical-align: middle; }
.grid td:first-child, .grid th:first-child { text-align: left; }
.grid.big td { padding: 3pt 5pt; font-size: 9pt; }
.tracker { margin: 6pt 0; }
.zones { display: flex; align-items: stretch; gap: 4pt; margin: 6pt 0; page-break-inside: avoid; break-inside: avoid; }
.zone { flex: 1; border: 0.75pt solid #999; border-radius: 3pt; padding: 4pt 6pt; }
.zone-n { font-family: 'Arial Narrow', Arial, sans-serif; font-size: 8pt; font-weight: bold; letter-spacing: 2px; text-transform: uppercase; color: #58180D; }
.zone-d { font-size: 8pt; line-height: 1.35; color: #333; }
.zarr { align-self: center; color: #58180D; font-size: 12pt; }
.rule { font-size: 8.8pt; line-height: 1.42; margin-bottom: 4pt; page-break-inside: avoid; break-inside: avoid; }
.rule.sub { margin-left: 10pt; }
.finale .rule { font-size: 8.5pt; line-height: 1.36; margin-bottom: 2pt; }
.finale .read-aloud p { font-size: 8.8pt; line-height: 1.5; }
.rule-h { font-family: 'Arial Narrow', Arial, sans-serif; font-size: 7.5pt; font-weight: bold; letter-spacing: 1.2px; text-transform: uppercase; color: #58180D; }
.taken { margin-top: 6pt; font-size: 9pt; display: flex; align-items: flex-end; gap: 8pt; }
.blank { display: inline-block; border-bottom: 0.75pt solid #888; width: 1.25in; height: 12pt; }
.blank.sm { width: 0.55in; height: 9pt; }
.finale .dm-note { margin: 0; }
/* spotlight and cast */
.spot td { font-size: 8.8pt; padding: 3.5pt 5pt; }
.spot td.rl { width: 15%; font-size: 7.5pt; }
.spot td.c { width: 30pt; text-align: center; vertical-align: middle; white-space: nowrap; }
.cast td { font-size: 8.3pt; padding: 3pt 5pt; }
.clues .bt { font-size: 8.5pt; margin-bottom: 2.5pt; }
.misc-item { font-size: 8.6pt; padding: 1.5pt 0 1.5pt 10pt; }
.switches td:first-child { font-size: 9pt; }
.switches th:first-child { color: #58180D; }
.flaretrack { margin-top: 5pt; }
.flaretrack td, .flaretrack th { padding: 2pt 3pt; font-size: 8pt; }
.flaretrack tr:first-child td { font-family: 'Arial Narrow', Arial, sans-serif; font-weight: bold; color: #58180D; border-bottom: none; }
.flaretrack th { border-bottom: none; white-space: nowrap; }
.sendoff { border: 0.75pt solid #58180D; border-radius: 3pt; padding: 0 7pt 5pt; page-break-inside: avoid; break-inside: avoid; }
.sendoff-h { font-family: 'Arial Narrow', Arial, sans-serif; font-size: 8pt; font-weight: bold; letter-spacing: 1.5px; text-transform: uppercase; color: #58180D; border-bottom: 1.5pt solid #58180D; margin: 0 -7pt 5pt; padding: 4pt 7pt 3pt; display: flex; justify-content: space-between; align-items: center; }
.sendoff p { font-size: 8.6pt; line-height: 1.4; margin-bottom: 3.5pt; }
.sendoff p.after { color: #444; }
.fray { margin: 0 0 2pt; }
.cast.guests td { padding: 2pt 5pt; }
.horde { border-top: 0.75pt solid #58180D; padding-top: 4pt; margin-top: 2pt; page-break-inside: avoid; break-inside: avoid; }
.fray td { font-size: 8.3pt; line-height: 1.32; padding: 1.6pt 4pt; }
.fray td.n { width: 12pt; font-family: 'Arial Narrow', Arial, sans-serif; font-weight: bold; color: #58180D; text-align: center; }
"""
body = open('body.html').read().rstrip()
log = open('livelog.html').read().replace('Expected Journey 011', 'Expected Journey 012').strip()
doc = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Expected Journey 012 &mdash; The Three Gifts</title>
<style>
%s%s</style>
</head>
<body>
%s

<!-- == LIVE LOG == -->
%s

</div>
</body>
</html>
""" % (css, extra, body, log)

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack=[]; self.bad=[]
        self.void={'meta','br','hr','img','input','link'}
    def handle_starttag(self,t,a):
        if t not in self.void: self.stack.append(t)
    def handle_endtag(self,t):
        if self.stack and self.stack[-1]==t: self.stack.pop()
        else: self.bad.append(t)
p=P(); p.feed(doc)
nonascii=[c for c in doc if ord(c)>127]
print('unclosed', p.stack, 'bad closes', p.bad, 'non-ascii', len(nonascii), 'bytes', len(doc))
assert not p.stack and not p.bad and not nonascii
open('Expected_Journey_012.html','w',encoding='ascii').write(doc)
