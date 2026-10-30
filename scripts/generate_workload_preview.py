"""Draw a public portfolio illustration using independently invented data only.

This builder never reads or imports the private GLW workbook. It illustrates
the planner's weekly-assignment and capacity-review workflow, not live results.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPACITY = 5.0
PEOPLE = ["Alex Chen", "Morgan Reed", "Taylor Brooks", "Jordan Ellis"]
ASSIGNMENTS = [
    ("Alex Chen", "Project Aspen", "Review grading plan", "Do this week", 3.0, "Normal"),
    ("Alex Chen", "Project Harbor", "Prepare drainage revisions", "Do this week", 3.0, "High"),
    ("Alex Chen", "Project Meadow", "Await client comments", "Waiting", 0.0, "Normal"),
    ("Morgan Reed", "Project Juniper", "Complete site layout", "Do this week", 4.0, "Normal"),
    ("Morgan Reed", "Project Harbor", "Await agency review", "Waiting", 0.0, "Normal"),
    ("Taylor Brooks", "Project Aspen", "Update utility layout", "Do this week", 2.0, "Normal"),
    ("Taylor Brooks", "Project Cedar", "Prepare plan comments", "Backlog", None, "High"),
    ("Jordan Ellis", "Project Cedar", "Review survey base", "Do this week", 1.0, "Normal"),
    ("Jordan Ellis", "Project Juniper", "Estimate plan revisions", "Do this week", None, "Normal"),
]

summaries = []
for person in PEOPLE:
    active = [row for row in ASSIGNMENTS if row[0] == person and row[3] == "Do this week"]
    planned = sum(row[4] for row in active if row[4] is not None)
    missing = sum(row[4] is None for row in active)
    available = CAPACITY - planned
    status = "Needs estimate" if missing else "Overloaded" if available < 0 else "Has room" if available >= 2 else "Balanced"
    summaries.append((person, planned, available, missing, status))

overloaded = sum(row[4] == "Overloaded" for row in summaries)
missing = sum(row[3] for row in summaries)
backlog = sum(row[3] == "Backlog" and row[5] == "High" for row in ASSIGNMENTS)
assert (overloaded, missing, backlog) == (1, 1, 1)
assert [(row[1], row[2]) for row in summaries] == [(6, -1), (4, 1), (2, 3), (1, 4)]

svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1320" viewBox="0 0 1200 1320" role="img" aria-labelledby="title desc">',
       '<title id="title">Weekly workload-planning prototype with fictional data</title>',
       '<desc id="desc">A recreated workbook excerpt showing a management capacity review and selected weekly assignments. Alex is overloaded, Taylor has room, and Jordan needs an estimate. All people, projects and numbers are invented for this illustration.</desc>',
       '<style>text{font-family:Arial,sans-serif;fill:#1c2a24}.muted{fill:#58645b}.label{font-size:20px;font-weight:700;letter-spacing:1.1px}.body{font-size:25px}.small{font-size:21px}.heading{font-size:31px;font-weight:700}.num{font-variant-numeric:tabular-nums}</style>']

def rect(x, y, w, h, fill, radius=0, stroke=None):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+'/>')

def text(x, y, value, css="body", fill=None, anchor=None, weight=None):
    attrs = (f' fill="{fill}" style="fill:{fill}"' if fill else '') + (f' text-anchor="{anchor}"' if anchor else '') + (f' font-weight="{weight}"' if weight else '')
    svg.append(f'<text x="{x}" y="{y}" class="{css}"{attrs}>{escape(str(value))}</text>')

def line(y, start=48, end=1152):
    svg.append(f'<path d="M{start} {y}H{end}" stroke="#d6d8ca"/>')

rect(0, 0, 1200, 1320, "#e7ecdf")
rect(24, 24, 1152, 1272, "#fffdf7", 10, "#d6d8ca")
rect(24, 24, 1152, 58, "#193f35", 10)
rect(24, 54, 1152, 28, "#193f35")
text(48, 61, "WORKLOAD-PLANNING PROTOTYPE", "label", "#fffdf7")
text(1152, 61, "FICTIONAL DATA", "label", "#efb388", "end")
text(48, 140, "Weekly workload planner", "heading")
text(48, 180, "BQE reference data + team-entered weekly plans", "body muted")
line(206)

text(48, 254, "Management View", "heading")
text(1152, 254, "Capacity: 5 days / person", "small muted", anchor="end")
for x, value, label, bg, fg in [
    (48, overloaded, "Overloaded people", "#f8e8df", "#9d4125"),
    (422, missing, "Missing estimates", "#fbf1d6", "#805f12"),
    (796, backlog, "High-priority backlog", "#edf0e5", "#193f35"),
]:
    rect(x, 281, 356, 108, bg, 4)
    text(x + 20, 327, value, "heading num", fg)
    text(x + 20, 365, label, "small", fg)

rect(48, 415, 1104, 51, "#e7ecdf")
for x, label, anchor in [(66, "Employee", None), (531, "Planned", "end"), (714, "Available", "end"), (761, "Review", None)]:
    text(x, 449, label, "small", anchor=anchor, weight=700)
for i, (person, planned, available, _, status) in enumerate(summaries):
    y = 466 + i * 70
    if i % 2:
        rect(48, y, 1104, 70, "#f6f7f0")
    text(66, y + 44, person)
    text(531, y + 44, f"{planned:.1f} d", "body num", anchor="end")
    text(714, y + 44, f"{available:.1f} d", "body num", "#9d4125" if available < 0 else None, "end")
    bg, fg = {"Overloaded": ("#f8e8df", "#9d4125"), "Needs estimate": ("#fbf1d6", "#805f12"), "Has room": ("#e2ecdf", "#28543d"), "Balanced": ("#edf0e5", "#193f35")}[status]
    rect(761, y + 16, 252, 40, bg, 3)
    text(779, y + 44, status, "small", fg)
    line(y + 70)

text(48, 800, "Weekly Plan", "heading")
text(1152, 800, "Selected assignments", "small muted", anchor="end")
rect(48, 824, 1104, 49, "#193f35")
for x, label in [(66, "Employee"), (333, "Project / next action"), (811, "Status")]:
    text(x, 857, label, "small", "#fffdf7", weight=700)
text(1134, 857, "Days", "small", "#fffdf7", "end", 700)
for i, ix in enumerate([0, 1, 4, 6, 8]):
    person, project, action, status, days, priority = ASSIGNMENTS[ix]
    y = 873 + i * 65
    if i % 2:
        rect(48, y, 1104, 65, "#f6f7f0")
    text(66, y + 40, person, "small")
    text(333, y + 26, project, "small", weight=700)
    text(333, y + 52, action, "small muted")
    text(811, y + 40, status, "small", "#805f12" if status == "Waiting" else "#58645b")
    rect(1042, y + 10, 110, 45, "#fbf1d6")
    text(1134, y + 40, f"{days:.1f}" if days is not None else "—", "small num", anchor="end")
    line(y + 65)

rect(48, 1223, 1104, 45, "#edf0e5")
rect(48, 1223, 221, 45, "#193f35")
text(65, 1253, "Management View", "small", "#fffdf7")
text(294, 1253, "Weekly Plan", "small muted")
text(479, 1253, "BQE Reference", "small muted")
svg.append('</svg>')
(ROOT / 'assets/bqe-workload-planner.svg').write_text('\n'.join(svg) + '\n', encoding='utf-8')
print('Created workload-planner illustration from fictional assignments only.')
