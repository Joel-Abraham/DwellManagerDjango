"""
==============================================================
 DwellManager — Complete Project Documentation Builder
 - Auto-generates UML diagrams (Activity, Sequence, Use Case)
 - Compiles full corrected DOCX matching CardeTrade template
==============================================================
Run:  python build_dwellmanager_docx.py
Output: DwellManager_Project_Documentation.docx
"""

import os
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon
from matplotlib.lines import Line2D

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# =====================================================================
# PART 1 — DIAGRAM GENERATION (matplotlib)
# =====================================================================
DIAGRAM_DIR = "diagrams"
os.makedirs(DIAGRAM_DIR, exist_ok=True)

matplotlib.rcParams["font.family"] = "serif"
matplotlib.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif"]


def _box(ax, x, y, w, h, text, fc="#f5f5f5", ec="black", fs=9, bold=False):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                         linewidth=1.0, edgecolor=ec, facecolor=fc)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, fontweight="bold" if bold else "normal", wrap=True)
    return (x + w / 2, y, x + w / 2, y + h)


def _diamond(ax, x, y, w, h, text, fc="#fff8dc", fs=9):
    pts = [(x, y + h / 2), (x + w / 2, y), (x + w, y + h / 2), (x + w / 2, y + h)]
    poly = Polygon(pts, closed=True, facecolor=fc, edgecolor="black", linewidth=1.0)
    ax.add_patch(poly)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def _arrow(ax, p1, p2, label="", style="->", color="black", fs=8):
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle=style, color=color, linewidth=1.0))
    if label:
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        ax.text(mx + 0.05, my, label, fontsize=fs, color=color, ha="left", va="center")


# ---------------------------------------------------------------
# 1. Activity Diagram (swimlane)
# ---------------------------------------------------------------
def draw_activity_diagram(path):
    fig, ax = plt.subplots(figsize=(11, 14))
    ax.set_xlim(0, 120); ax.set_ylim(0, 150); ax.axis("off")

    # Swimlanes
    lanes = ["Admin", "Guard", "Resident", "System (DB)"]
    lane_w = 30
    for i, lane in enumerate(lanes):
        x = i * lane_w
        ax.add_patch(Rectangle((x, 0), lane_w, 145, fill=False, edgecolor="black", linewidth=1.0))
        ax.text(x + lane_w / 2, 146.5, lane, ha="center", va="bottom",
                fontsize=11, fontweight="bold")

    # Initial node (System)
    ax.add_patch(Circle((105, 140), 1.5, facecolor="black", edgecolor="black"))
    _box(ax, 97, 132, 16, 5, "Start / Login", fc="#e8f4ff")
    _diamond(ax, 100, 124, 10, 6, "Role?")
    _arrow(ax, (105, 132), (105, 130))

    # Admin flow
    _arrow(ax, (100, 127), (15, 127), "Admin", color="#1f4e79")
    _box(ax, 3, 118, 24, 6, "Admin Dashboard", fc="#dbe9f6")
    _diamond(ax, 5, 108, 20, 7, "Action?")
    _arrow(ax, (15, 118), (15, 115))

    actions = [
        ("Manage Flats", 100),
        ("Manage Residents", 92),
        ("Assign Maintenance", 84),
        ("View Billing", 76),
    ]
    for label, y in actions:
        _box(ax, 3, y, 24, 5, label, fc="#eaf3fb", fs=8)
        _arrow(ax, (5, 111), (3.5, y + 2.5), style="->", color="#1f4e79")

    # Assign Maintenance sub-flow
    _box(ax, 3, 65, 24, 6, "Fetch MR with select_for_update()", fc="#fff2cc", fs=7.5)
    _arrow(ax, (15, 84), (15, 71))
    _diamond(ax, 3, 55, 24, 7, "fee_amount > 0 ?")
    _arrow(ax, (15, 65), (15, 62))
    _box(ax, 3, 45, 24, 6, "CREATE Payment\n(Additional Charge)", fc="#d5e8d4", fs=8)
    _arrow(ax, (15, 55), (15, 51), "Yes", color="green")
    _box(ax, 32, 45, 24, 6, "No Payment Created", fc="#f8cecc", fs=8)
    _arrow(ax, (27, 58.5), (32, 48), "No", color="red")

    # Guard flow
    _arrow(ax, (100, 127), (45, 127), "Guard", color="#7b3f00")
    _box(ax, 33, 118, 24, 6, "Guard Dashboard", fc="#fbe6d0")
    _diamond(ax, 35, 108, 20, 7, "Action?")
    _arrow(ax, (45, 118), (45, 115))

    g_actions = [("Check In Visitor", 100), ("View Inside Visitors", 92),
                 ("Check Out Visitor", 84), ("Search Log", 76)]
    for label, y in g_actions:
        _box(ax, 33, y, 24, 5, label, fc="#fdf2e5", fs=8)
        _arrow(ax, (35, 111), (33.5, y + 2.5), color="#7b3f00")

    _box(ax, 33, 65, 24, 6, "Save Visitor\n(status=Inside)", fc="#d5e8d4", fs=8)
    _arrow(ax, (45, 76), (45, 71))
    _box(ax, 33, 55, 24, 6, "Update Visitor\n(status=Checked-Out)", fc="#d5e8d4", fs=8)
    _arrow(ax, (45, 84), (45, 61))

    # Resident flow
    _arrow(ax, (100, 127), (75, 127), "Resident", color="#385723")
    _box(ax, 63, 118, 24, 6, "Resident Dashboard", fc="#e2efda")
    _diamond(ax, 65, 108, 20, 7, "Action?")
    _arrow(ax, (75, 118), (75, 115))

    r_actions = [("View Bills", 100), ("Pay Bill", 92),
                 ("Raise Maintenance", 84), ("Track Status", 76)]
    for label, y in r_actions:
        _box(ax, 63, y, 24, 5, label, fc="#f0f7ea", fs=8)
        _arrow(ax, (65, 111), (63.5, y + 2.5), color="#385723")

    _box(ax, 63, 65, 24, 6, "Pay with select_for_update()\nstatus=Paid, receipt_ref", fc="#fff2cc", fs=7.5)
    _arrow(ax, (75, 92), (75, 71))
    _box(ax, 63, 55, 24, 6, "Generate Receipt", fc="#d5e8d4", fs=8)
    _arrow(ax, (75, 65), (75, 61))

    _box(ax, 63, 45, 24, 6, "Save MaintenanceRequest\n(status=Pending)", fc="#d5e8d4", fs=8)
    _arrow(ax, (75, 84), (75, 51))

    # Final nodes
    ax.add_patch(Circle((15, 40), 1.5, facecolor="white", edgecolor="black", linewidth=1.5))
    ax.add_patch(Circle((15, 40), 0.7, facecolor="black", edgecolor="black"))
    ax.add_patch(Circle((75, 40), 1.5, facecolor="white", edgecolor="black", linewidth=1.5))
    ax.add_patch(Circle((75, 40), 0.7, facecolor="black", edgecolor="black"))

    _arrow(ax, (15, 45), (15, 41.5))
    _arrow(ax, (75, 45), (75, 41.5))

    plt.title("DwellManager — Activity Diagram (Swimlane)", fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()


# ---------------------------------------------------------------
# 2. Sequence Diagram
# ---------------------------------------------------------------
def draw_sequence_diagram(path):
    fig, ax = plt.subplots(figsize=(12, 11))
    ax.set_xlim(0, 130); ax.set_ylim(0, 130); ax.axis("off")

    # Lifelines
    lifelines = [
        ("Admin", 15, "#1f4e79"),
        ("assign_view\n(Django View)", 45, "#3d85c6"),
        ("SQLite\n(ORM)", 75, "#666666"),
        ("Payment\nModel", 105, "#385723"),
        ("Resident\nBilling View", 125, "#7b3f00"),
    ]
    for name, x, col in lifelines:
        _box(ax, x - 9, 120, 18, 6, name, fc=col, ec=col, fs=8, bold=False)
        for t in ax.texts[-1:]:
            t.set_color("white")
        ax.plot([x, x], [120, 5], linestyle="--", color=col, linewidth=0.8)

    def msg(y, x1, x2, label, color="black", style="->"):
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle=style, color=color, linewidth=1.2))
        mid = (x1 + x2) / 2
        ax.text(mid, y + 0.7, label, fontsize=8, ha="center", color=color,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))

    y = 112
    msg(y, 15, 45, "POST(assigned_to, scheduled_date, fee_amount)"); y -= 5
    ax.text(45, y, "validate form", fontsize=7.5, ha="center", style="italic", color="#3d85c6"); y -= 4

    # Atomic block
    ax.add_patch(Rectangle((40, y - 38), 70, 44, fill=False,
                           edgecolor="#c00", linewidth=1.2, linestyle="-"))
    ax.text(41, y + 2, "  transaction.atomic()", fontsize=8.5, color="#c00", fontweight="bold")

    msg(y, 45, 75, "select_for_update() MaintenanceRequest", color="#666666"); y -= 5
    msg(y, 75, 45, "locked instance (status=Pending)", color="#666666", style="-|>"); y -= 5
    ax.text(45, y, "assert status == 'Pending'", fontsize=7.5, ha="center", style="italic", color="#3d85c6"); y -= 4
    msg(y, 45, 75, "mr.status = 'Assigned'; save()", color="#666666"); y -= 5

    # alt
    ax.add_patch(Rectangle((40, y - 14), 70, 18, fill=False,
                           edgecolor="#080", linewidth=1.0, linestyle=":"))
    ax.text(41, y + 1, "alt  fee_amount > 0", fontsize=8, color="#080", fontweight="bold")
    msg(y, 45, 105, "Payment.objects.create(charge_type='Additional Charge')", color="#385723"); y -= 5
    msg(y, 105, 45, "payment created", color="#385723", style="-|>"); y -= 5
    ax.text(41, y, "else  no charge", fontsize=8, color="#080"); y -= 3

    msg(y, 45, 15, "redirect (200)", color="#1f4e79", style="-|>"); y -= 8

    # Resident view side
    msg(y, 125, 75, "query unpaid payments (own flat)", color="#7b3f00"); y -= 5
    msg(y, 75, 125, "[base charge, additional charge]", color="#7b3f00", style="-|>"); y -= 8

    ax.text(65, 3,
            "Fig: Atomic Maintenance Assignment → Additional Charge (Resident Billing View)",
            fontsize=9, ha="center", style="italic")

    plt.title("DwellManager — Sequence Diagram (Atomic Billing)", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()


# ---------------------------------------------------------------
# 3. Use Case Diagram
# ---------------------------------------------------------------
def draw_usecase_diagram(path):
    fig, ax = plt.subplots(figsize=(13, 11))
    ax.set_xlim(0, 140); ax.set_ylim(0, 120); ax.axis("off")

    # System boundary
    ax.add_patch(Rectangle((30, 5), 80, 108, fill=False, edgecolor="black", linewidth=1.3))
    ax.text(70, 114, "DwellManager System Boundary", ha="center",
            fontsize=11, fontweight="bold")

    # Actors
    def actor(x, y, name, color):
        ax.add_patch(Circle((x, y + 6), 2.2, fill=False, edgecolor=color, linewidth=1.3))
        ax.plot([x, x], [y + 3.8, y - 0.5], color=color, linewidth=1.3)
        ax.plot([x - 2.5, x + 2.5], [y + 1.8, y + 1.8], color=color, linewidth=1.3)
        ax.plot([x, x - 2], [y - 0.5, y - 3.5], color=color, linewidth=1.3)
        ax.plot([x, x + 2], [y - 0.5, y - 3.5], color=color, linewidth=1.3)
        ax.text(x, y - 6, name, ha="center", fontsize=10, fontweight="bold", color=color)

    def usecase(x, y, w, h, label, fc="#dbe9f6", fs=8):
        ell = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=2",
                             linewidth=1.0, edgecolor="#1f4e79", facecolor=fc)
        ax.add_patch(ell)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=fs, wrap=True)

    def assoc(p1, p2, style="-", color="black", ls="-"):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], linestyle=ls,
                color=color, linewidth=0.9, marker="" if style == "-" else "")

    actor(10, 90, "Admin", "#1f4e79")
    actor(10, 40, "Guard", "#7b3f00")
    actor(130, 70, "Resident", "#385723")

    # Admin use cases
    uc_admin = [
        (40, 100, "Register / Login"),
        (40, 90, "Manage Flats (CRUD)"),
        (40, 80, "Manage Residents"),
        (40, 70, "View Maintenance Requests"),
        (40, 60, "Assign Maintenance"),
        (40, 50, "View Billing Overview"),
        (40, 40, "View Analytics"),
    ]
    for x, y, lbl in uc_admin:
        usecase(x, y, 30, 7, lbl, fc="#e3effb")
        assoc((12, 90), (40, y + 3.5))

    # Guard use cases
    uc_guard = [
        (58, 100, "Check In Visitor"),
        (58, 90, "View Inside Visitors"),
        (58, 80, "Check Out Visitor"),
        (58, 70, "Search Visitor History"),
    ]
    for x, y, lbl in uc_guard:
        usecase(x, y, 30, 7, lbl, fc="#fbe6d0")
        assoc((12, 40), (x, y + 3.5))

    # Resident use cases
    uc_res = [
        (98, 100, "View Bills"),
        (98, 90, "Pay Bill"),
        (98, 80, "Download Receipt"),
        (98, 70, "Raise Maintenance Request"),
        (98, 60, "View Request Status"),
    ]
    for x, y, lbl in uc_res:
        usecase(x, y, 30, 7, lbl, fc="#e2efda")
        assoc((128, 70), (128, y + 3.5))

    # Include relationships
    def include(p1, p2, label="<<include>>"):
        ax.annotate("", xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle="->", color="#c00",
                                    linestyle="--", linewidth=0.9))
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        ax.text(mx, my, label, fontsize=7, color="#c00", ha="center",
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none"))

    # Add extra use cases as include targets
    usecase(48, 30, 24, 7, "Set Fee", fc="#fff2cc")
    usecase(76, 30, 24, 7, "Create Additional\nCharge", fc="#fff2cc")
    usecase(48, 20, 24, 7, "Capture Vehicle\nDetails", fc="#fff2cc")
    usecase(76, 20, 24, 7, "Generate Receipt", fc="#fff2cc")

    include((70, 60), (60, 37))       # Assign MR -> Set Fee
    include((70, 60), (88, 37))       # Assign MR -> Create Additional Charge
    include((73, 100), (60, 27))      # Check In -> Capture Vehicle
    include((113, 90), (88, 27))      # Pay Bill -> Generate Receipt

    ax.text(70, 2, "Legend:   ─── Association    ---> <<include>>",
            ha="center", fontsize=9, style="italic")

    plt.title("DwellManager — Use Case Diagram", fontsize=14, fontweight="bold", pad=10)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()


print("▶ Generating diagrams...")
draw_activity_diagram(os.path.join(DIAGRAM_DIR, "activity.png"))
draw_sequence_diagram(os.path.join(DIAGRAM_DIR, "sequence.png"))
draw_usecase_diagram(os.path.join(DIAGRAM_DIR, "usecase.png"))
print("✓ Diagrams generated in ./diagrams/")


# =====================================================================
# PART 2 — DOCX GENERATION
# =====================================================================

def set_times(style, size=12, bold=False):
    style.font.name = "Times New Roman"
    style.font.size = Pt(size)
    style.font.bold = bold
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts"); rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), "Times New Roman")


def fmt(p, ls=1.5, after=6, align=None):
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    p.paragraph_format.line_spacing = ls
    p.paragraph_format.space_after = Pt(after)
    if align is not None:
        p.alignment = align


def body(doc, text, bold=False, italic=False, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
         after=6, ls=1.5):
    p = doc.add_paragraph()
    fmt(p, ls=ls, after=after, align=align)
    r = p.add_run(text)
    r.font.name = "Times New Roman"; r.font.size = Pt(size)
    r.bold = bold; r.italic = italic
    return p


def h(doc, text, level=1):
    sizes = {1: 16, 2: 14, 3: 12}
    p = doc.add_paragraph()
    fmt(p, ls=1.5, after=10, align=WD_ALIGN_PARAGRAPH.LEFT)
    r = p.add_run(text)
    r.font.name = "Times New Roman"; r.font.size = Pt(sizes[level]); r.bold = True
    return p


def bullet(doc, text, size=12):
    p = doc.add_paragraph(style="List Bullet")
    fmt(p, ls=1.5, after=4, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    r = p.add_run(text); r.font.name = "Times New Roman"; r.font.size = Pt(size)
    return p


def numbered(doc, text, size=12):
    p = doc.add_paragraph(style="List Number")
    fmt(p, ls=1.5, after=4, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    r = p.add_run(text); r.font.name = "Times New Roman"; r.font.size = Pt(size)
    return p


def table(doc, headers, rows):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    for i, hdr in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        p = c.paragraphs[0]; fmt(p, ls=1.0, after=2, align=WD_ALIGN_PARAGRAPH.LEFT)
        r = p.add_run(hdr); r.font.name = "Times New Roman"; r.font.size = Pt(11); r.bold = True
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            fmt(p, ls=1.0, after=2, align=WD_ALIGN_PARAGRAPH.LEFT)
            r = p.add_run(str(v)); r.font.name = "Times New Roman"; r.font.size = Pt(11)
    doc.add_paragraph()


def page_break(doc):
    doc.add_page_break()


def image(doc, path, width_in=6.3):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Inches(width_in))


def chapter_divider(doc, number, title):
    for _ in range(6):
        doc.add_paragraph()
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(number); r.font.name = "Times New Roman"; r.font.size = Pt(48); r.bold = True
    p2 = doc.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run(title.upper()); r2.font.name = "Times New Roman"; r2.font.size = Pt(22); r2.bold = True

    sectPr = doc.sections[-1]._sectPr
    pgB = OxmlElement("w:pgBorders")
    pgB.set(qn("w:offsetFrom"), "page")
    for edge in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "12")
        e.set(qn("w:space"), "24"); e.set(qn("w:color"), "000000")
        pgB.append(e)
    sectPr.append(pgB)
    page_break(doc)


def configure(section):
    section.page_width = Inches(8.5); section.page_height = Inches(11)
    section.left_margin = Inches(1.25); section.right_margin = Inches(1.25)
    section.top_margin = Inches(1.0); section.bottom_margin = Inches(1.0)

    header = section.header
    hp = header.paragraphs[0]; hp.text = ""
    r = hp.add_run("DWELLMANAGER — PROPERTY MANAGEMENT SYSTEM\t\t")
    r.font.name = "Times New Roman"; r.font.size = Pt(10)
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = "PAGE"
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "end")
    r2 = hp.add_run(); r2.font.name = "Times New Roman"; r2.font.size = Pt(10)
    r2._r.append(f1); r2._r.append(it); r2._r.append(f2)

    footer = section.footer
    fp = footer.paragraphs[0]; fp.text = ""; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run("Department of Computer Science  |  Nirmala College Muvattupuzha (Autonomous)")
    r.font.name = "Times New Roman"; r.font.size = Pt(9)


# =====================================================================
# BUILD THE DOCUMENT
# =====================================================================
doc = Document()
set_times(doc.styles["Normal"], 12)
set_times(doc.styles["List Bullet"], 12)
set_times(doc.styles["List Number"], 12)
configure(doc.sections[0])

# ---------- TITLE PAGE ----------
for _ in range(4): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("PROJECT REPORT ON"); r.font.name = "Times New Roman"; r.font.size = Pt(14); r.bold = True
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("DWELLMANAGER — PROPERTY MANAGEMENT SYSTEM")
r.font.name = "Times New Roman"; r.font.size = Pt(20); r.bold = True
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Submitted by:\n[Student Name]\n[Registration Number / Roll No]")
r.font.name = "Times New Roman"; r.font.size = Pt(12)
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Under the Guidance of:\n[Guide's Name]\n[Guide's Designation]")
r.font.name = "Times New Roman"; r.font.size = Pt(12)
for _ in range(3): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Department of Computer Science\nNirmala College Muvattupuzha (Autonomous)\n[Year / Semester]")
r.font.name = "Times New Roman"; r.font.size = Pt(12); r.bold = True
page_break(doc)

# ---------- ACKNOWLEDGEMENT ----------
h(doc, "ACKNOWLEDGEMENT", 1)
body(doc, "I would like to express my sincere gratitude and indebtedness to all those who generously "
          "supported me throughout the development and successful documentation of this project.")
body(doc, "I express my profound gratitude to my esteemed project guide, [Guide's Name], "
          "[Guide's Designation], for providing invaluable intellectual mentorship, continuous "
          "technical encouragement, and constructive critique at every stage of system analysis "
          "and software realization.")
body(doc, "I also extend my sincere appreciation to the faculty members and staff of the Department "
          "of Computer Science, Nirmala College Muvattupuzha (Autonomous), for providing the necessary "
          "infrastructural resources, computational lab facilities, and academic environment required "
          "to execute this work.")
body(doc, "Lastly, I am grateful to my family, peers, and well-wishers for their unwavering moral "
          "encouragement and practical insights throughout this endeavor.")
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = p.add_run("[Student Name]\n[Registration Number / Roll No]")
r.font.name = "Times New Roman"; r.font.size = Pt(12)
page_break(doc)

# ---------- ABSTRACT ----------
h(doc, "ABSTRACT", 1)
body(doc,
    "DwellManager is a full-stack, role-based web application engineered using Python and the Django "
    "Web Framework to modernize and streamline apartment complex administration. Traditional apartment "
    "management suffers from systemic inefficiencies, including informal communication channels, "
    "manual paper-based visitor registers, delayed maintenance fulfillment, and untracked billing of "
    "base maintenance and repair charges.")
body(doc,
    "The DwellManager platform addresses these persistent domain bottlenecks by establishing a "
    "transparent, secure, and role-based digital system structured around three specialized "
    "designations: Admins, Guards, and Residents.")
body(doc,
    "The system enables Admins to manage flats, register residents, assign maintenance requests, and "
    "oversee billing; Guards to perform visitor check-in/checkout with vehicle details and search "
    "visit history; and Residents to view and pay unified bills (base maintenance + additional "
    "charges), raise maintenance requests, and download receipts. A single Payment model with a "
    "charge_type discriminator handles both recurring and one-off charges, and Django transactions "
    "ensure that assigning a maintenance request automatically creates a linked Payment charge "
    "atomically.")
body(doc,
    "Built upon a normalized relational schema interfacing with SQLite, DwellManager delivers "
    "ACID-compliant transactions, robust defense against web vulnerabilities (CSRF, SQL Injection, "
    "XSS), and server-side data isolation, thereby providing a modern, accountable, and dispute-free "
    "operational environment for contemporary residential apartment complexes.")
page_break(doc)

# ---------- TABLE OF CONTENTS ----------
h(doc, "TABLE OF CONTENTS", 1)
toc = [
    "1. INTRODUCTION", "    1.1 Introduction", "    1.2 Problem Statement",
    "    1.3 Scope and Relevance of Project", "    1.4 Objectives",
    "2. SYSTEM ANALYSIS", "    2.1 Introduction", "    2.2 Existing System",
    "    2.3 Proposed System", "    2.4 Feasibility Study",
    "    2.5 Software Engineering Paradigm Applied",
    "3. SYSTEM DESIGN", "    3.1 Introduction", "    3.2 Database Design",
    "    3.3 Object Oriented Design — UML Diagrams",
    "    3.4 Module Description", "    3.5 Input Design", "    3.6 Output Design",
    "4. SYSTEM ENVIRONMENT", "    4.1 Introduction", "    4.2 Software Requirement Specification",
    "    4.3 Hardware Requirement Specification", "    4.4 Tools, Platforms",
    "5. SYSTEM IMPLEMENTATION", "6. SYSTEM TESTING", "7. SYSTEM MAINTENANCE",
    "8. FUTURE ENHANCEMENT AND SCOPE FOR FURTHER DEVELOPMENT",
    "9. CONCLUSION", "10. BIBLIOGRAPHY", "11. ANNEXURES",
]
for item in toc:
    body(doc, item, align=WD_ALIGN_PARAGRAPH.LEFT, after=2)
page_break(doc)

# ---------- CHAPTER 1 ----------
chapter_divider(doc, "1", "Introduction")

h(doc, "1.1 Introduction", 2)
body(doc,
    "Residential apartment complex management traditionally relies on paper registers, verbal "
    "maintenance requests, and manual visitor logs. These practices create operational bottlenecks: "
    "delayed maintenance fulfillment, untracked visitor movement, billing discrepancies, and zero "
    "accountability across staff shifts.")
body(doc,
    "DwellManager is a full-stack web application engineered to modernize apartment complex "
    "administration. The platform eliminates administrative fragmentation by establishing a "
    "transparent, role-based management system structured around three distinct user designations:")
bullet(doc, "Admins: Manage flats and resident records, assign maintenance requests, oversee billing, "
            "and monitor complex-wide analytics.")
bullet(doc, "Guards: Perform visitor check-in/checkout with vehicle details, search visit history, "
            "and maintain gate security logs.")
bullet(doc, "Residents: View and pay bills, raise maintenance requests, download receipts, and "
            "track request status.")

h(doc, "Technical Architecture Overview", 3)
body(doc, "DwellManager is built using a modern multi-tier web architecture:")
bullet(doc, "Back-End: Powered by Python and the Django Web Framework using the Model-View-Template "
            "(MVT) pattern. Django manages core application logic, database Object-Relational Mapping "
            "(ORM), custom role-based access controls, and data protection against common web "
            "vulnerabilities (CSRF, SQL Injection, XSS).")
bullet(doc, "Persistent Storage: SQLite relational database (development and production in the "
            "current configuration).")
bullet(doc, "Front-End: Built using HTML5, CSS3, and a custom dark glassmorphism design system "
            "(static/style.css). No Bootstrap or external CSS frameworks are used. The interface is "
            "server-side rendered with Django templates.")

h(doc, "1.2 Problem Statement", 2)
body(doc, "Conventional apartment management suffers from systemic inefficiencies:")
numbered(doc, "Untracked Visitor Movement: Paper visitor logs are easily lost, illegible, or "
              "incomplete. No real-time visibility into who is inside the complex.")
numbered(doc, "Delayed Maintenance Fulfillment: Verbal or informal complaints result in lost "
              "requests, delayed contractor dispatch, and zero accountability.")
numbered(doc, "Billing Errors and Delays: Manual tracking of base maintenance charges and additional "
              "repair fees leads to miscalculations and payment disputes.")
numbered(doc, "Lack of Audit Trails: No centralized record of financial transactions, maintenance "
              "history, or visitor logs for administrative review.")

h(doc, "1.3 Scope and Relevance of Project", 2)
body(doc, "Scope: DwellManager encompasses the complete end-to-end digital lifecycle of apartment "
          "complex management, incorporating three user tiers:")
bullet(doc, "Role-Based Web Dashboards: Dedicated portals for Admin, Guard, and Resident.")
bullet(doc, "Flat and Resident Management: Admins create, edit, and deactivate flats; register "
            "residents and link them to flats.")
bullet(doc, "Visitor Logging: Guards check in visitors with name, contact, target flat, purpose, "
            "and vehicle details; check out visitors; searchable history.")
bullet(doc, "Maintenance Workflow: Residents raise requests with category and description; Admins "
            "assign contractors, set fees, and update status.")
bullet(doc, "Unified Billing: Automatic creation of base maintenance charges and additional charges "
            "from maintenance fees; payment processing with receipt generation.")

h(doc, "1.4 Objectives", 2)
body(doc, "The primary objective of DwellManager is to design and deploy a secure, transparent "
          "web-based apartment management platform that eliminates administrative fragmentation "
          "through automated workflows and unified billing. Specific objectives include:")
numbered(doc, "Implement role-based authentication for Admin, Guard, and Resident.")
numbered(doc, "Digitalize flat and resident management.")
numbered(doc, "Provide a complete visitor check-in/checkout system with vehicle tracking.")
numbered(doc, "Streamline maintenance request lifecycle from submission to completion.")
numbered(doc, "Unify billing (base maintenance + additional charges) with atomic payment processing.")
numbered(doc, "Ensure server-side data isolation and IDOR protection.")

# ---------- CHAPTER 2 ----------
page_break(doc)
chapter_divider(doc, "2", "System Analysis")

h(doc, "2.1 Introduction", 2)
body(doc, "System analysis evaluates the existing apartment management domain, identifies operational "
          "bottlenecks, and defines structured solutions. For DwellManager, system analysis entails "
          "critically examining traditional manual apartment management workflows and formulating a "
          "modern, web-based software architecture.")

h(doc, "2.2 Existing System", 2)
body(doc, "Traditional apartment management relies on paper visitor registers, verbal maintenance "
          "complaints, and manual billing ledgers.")
body(doc, "Limitations of the Existing System:")
bullet(doc, "Unverifiable Visitor Logs: Paper registers are easily lost or falsified.")
bullet(doc, "Maintenance Delays: No formal ticketing queue.")
bullet(doc, "Billing Disputes: Manual calculations of base maintenance and repair fees.")
bullet(doc, "No Audit Trail: Difficult to trace financial or operational history.")

h(doc, "2.3 Proposed System", 2)
body(doc, "DwellManager replaces manual workflows with an automated, role-based web platform:")
bullet(doc, "Three Role Dashboards: Admin, Guard, Resident.")
bullet(doc, "Visitor Logging Module: Complete check-in/checkout with vehicle details.")
bullet(doc, "Maintenance Ticketing: Resident submission → Admin assignment → Status tracking.")
bullet(doc, "Unified Payment Model: Single Payment table handles both 'Base Maintenance' and "
            "'Additional Charge' via a charge_type discriminator.")
bullet(doc, "Atomic Transactions: Maintenance assignment and payment processing use "
            "transaction.atomic() with select_for_update() to prevent race conditions.")

h(doc, "2.4 Feasibility Study", 2)
h(doc, "2.4.1 Technical Feasibility", 3)
bullet(doc, "Back-End: Python + Django with built-in security (CSRF, SQL injection defense, "
            "password hashing).")
bullet(doc, "Front-End: HTML5, CSS3, custom glassmorphism CSS (no Bootstrap dependency).")
bullet(doc, "Database: SQLite — zero-configuration, ACID-compliant, suitable for the current "
            "deployment scale.")
body(doc, "Conclusion: Proven open-source stack; technically feasible.")

h(doc, "2.4.2 Economic Feasibility", 3)
bullet(doc, "Zero Licensing Costs: Entire stack is open-source.")
bullet(doc, "Low Infrastructure Overhead: SQLite requires no separate database server.")
body(doc, "Conclusion: High operational value at minimal cost.")

h(doc, "2.4.3 Operational Feasibility", 3)
bullet(doc, "Intuitive Role-Specific Dashboards: Each user sees only relevant tools.")
bullet(doc, "Server-Side Data Isolation: Residents can only access their own flat’s data.")
body(doc, "Conclusion: Aligns with actual apartment management workflows.")

h(doc, "2.5 Software Engineering Paradigm Applied", 2)
body(doc,
    "The project follows the Waterfall Model: sequential phases of requirement gathering, system "
    "design, implementation, integration/testing, deployment, and maintenance. Each phase is "
    "completed before the next begins, with no overlapping phases.")

# ---------- CHAPTER 3 ----------
page_break(doc)
chapter_divider(doc, "3", "System Design")

h(doc, "3.1 Introduction", 2)
body(doc,
    "System design defines the architecture, components, and data model. DwellManager uses a secure "
    "MVT architecture across three user tiers: Admin, Guard, and Resident. Core design priorities "
    "include relational database normalization, role-segregated forms, atomic billing workflows, "
    "and a verified maintenance tracking pipeline.")

h(doc, "3.2 Database Design", 2)
body(doc, "The schema consists of five normalized tables:")

h(doc, "1. Flat", 3)
table(doc, ["Field", "Type", "Constraint", "Description"], [
    ["id", "BigAutoField", "Primary Key", "Unique flat identifier"],
    ["flat_number", "CharField(20)", "Unique with block", "Door/bay number"],
    ["block", "CharField(50)", "Unique with flat_number", "Block designation"],
    ["floor", "PositiveIntegerField", "—", "Floor number"],
    ["flat_type", "CharField(20)", "Choices: 1BHK…Studio", "Unit classification"],
    ["owner_name", "CharField(100)", "—", "Owner’s full name"],
    ["base_maintenance_amount", "DecimalField(10,2)", "Min=0.00", "Monthly base charge"],
    ["is_active", "BooleanField", "Default=True", "Soft-delete flag"],
    ["manually_marked_occupied", "BooleanField", "Default=False", "Override for non-portal residents"],
])

h(doc, "2. Resident (AUTH_USER_MODEL)", 3)
table(doc, ["Field", "Type", "Constraint", "Description"], [
    ["id", "BigAutoField", "Primary Key", "Unique user identifier"],
    ["flat", "ForeignKey → Flat", "null=True, blank=True", "Linked flat (null for Admin/Guard)"],
    ["username", "CharField(50)", "Unique, indexed", "Login handle"],
    ["full_name", "CharField(100)", "—", "Display name"],
    ["contact_number", "CharField(15)", "null, blank", "Phone number"],
    ["email", "EmailField", "null, blank", "Email address"],
    ["role", "CharField(20)", "Choices: Resident, Guard, Admin", "RBAC determinant"],
    ["status", "CharField(20)", "Choices: Active, Inactive, Moved-out", "Resident lifecycle"],
    ["move_in_date", "DateField", "null, blank", "Date of move-in"],
    ["is_active", "BooleanField", "Default=True", "Login enable/disable"],
    ["is_staff", "BooleanField", "Default=False", "Django admin access"],
])

h(doc, "3. MaintenanceRequest", 3)
table(doc, ["Field", "Type", "Constraint", "Description"], [
    ["id", "BigAutoField", "Primary Key", "Request identifier"],
    ["flat", "ForeignKey → Flat", "RESTRICT", "Impacted flat"],
    ["category", "CharField(30)", "Choices (13)", "plumbing, electrical, hvac, …"],
    ["description", "TextField(500)", "—", "Problem narrative"],
    ["status", "CharField(20)", "Choices: Pending…Completed", "Workflow state"],
    ["assigned_to", "CharField(100)", "null, blank", "Contractor/vendor name"],
    ["scheduled_date", "DateField", "null, blank", "Planned visit date"],
    ["fee_amount", "DecimalField(10,2)", "null, blank, Min=0.00", "Charge for repair"],
    ["created_at", "DateTimeField", "auto_now_add", "Submission timestamp"],
])

h(doc, "4. Payment (Unified Billing)", 3)
table(doc, ["Field", "Type", "Constraint", "Description"], [
    ["id", "BigAutoField", "Primary Key", "Payment identifier"],
    ["flat", "ForeignKey → Flat", "RESTRICT", "Billed flat"],
    ["charge_type", "CharField(30)", "Choices: Base/Additional", "Discriminator"],
    ["source_request", "ForeignKey → MaintenanceRequest", "SET_NULL", "Linked maintenance request"],
    ["billing_month", "CharField(20)", "—", "Billing cycle (e.g., Sept 2026)"],
    ["amount", "DecimalField(10,2)", "Min=0.00", "Charge amount"],
    ["description", "CharField(200)", "null, blank", "Charge description"],
    ["status", "CharField(20)", "Choices: Unpaid, Paid", "Payment status"],
    ["payment_method", "CharField(20)", "Choices: UPI, Net Banking, Cash", "Remittance channel"],
    ["paid_at", "DateTimeField", "null, blank", "Payment timestamp"],
    ["receipt_ref", "CharField(50)", "null, blank", "Receipt reference"],
    ["created_at", "DateTimeField", "auto_now_add", "Creation timestamp"],
])

h(doc, "5. Visitor", 3)
table(doc, ["Field", "Type", "Constraint", "Description"], [
    ["id", "BigAutoField", "Primary Key", "Visitor log identifier"],
    ["full_name", "CharField(60)", "—", "Visitor name"],
    ["contact_number", "CharField(15)", "—", "Visitor phone"],
    ["target_flat", "ForeignKey → Flat", "RESTRICT", "Flat being visited"],
    ["purpose", "CharField(30)", "Choices (4)", "Delivery, Guest, Service, Other"],
    ["vehicle_number", "CharField(20)", "null, blank", "Vehicle registration"],
    ["vehicle_type", "CharField(10)", "Choices: Car, Bike, None", "Vehicle classification"],
    ["check_in_time", "DateTimeField", "auto_now_add", "Entry timestamp"],
    ["exit_time", "DateTimeField", "null, blank", "Exit timestamp"],
    ["status", "CharField(20)", "Choices: Inside/Checked-Out", "Current state"],
])

h(doc, "3.3 Object Oriented Design — UML Diagrams", 2)

h(doc, "3.3.1 Activity Diagram", 3)
body(doc,
    "The activity diagram below models the complete swimlane workflow across all three roles — "
    "Admin, Guard, and Resident — with decision diamonds showing action branching, the atomic "
    "database transaction for maintenance assignment (with fee > 0 branching to create the "
    "Additional Charge Payment), and the atomic payment processing flow.")
image(doc, os.path.join(DIAGRAM_DIR, "activity.png"), width_in=6.3)
body(doc, "Figure 3.1 — DwellManager Activity Diagram (Swimlane)", italic=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, size=10)

h(doc, "3.3.2 Sequence Diagram", 3)
body(doc,
    "The sequence diagram below illustrates the atomic Maintenance-to-Charge pipeline. When an "
    "Admin assigns a maintenance request, the view wraps the operation in transaction.atomic() and "
    "uses select_for_update() to lock the MaintenanceRequest row, preventing race conditions. If "
    "fee_amount > 0, a linked Payment record (charge_type = Additional Charge) is created in the "
    "same transaction, and the Resident Billing View immediately sees the new charge.")
image(doc, os.path.join(DIAGRAM_DIR, "sequence.png"), width_in=6.3)
body(doc, "Figure 3.2 — DwellManager Sequence Diagram (Atomic Billing)",
     italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=10)

h(doc, "3.3.3 Use Case Diagram", 3)
body(doc,
    "The use case diagram below shows all three actors — Admin, Guard, and Resident — with their "
    "associated use cases enclosed within the DwellManager system boundary. Include relationships "
    "(<<include>>) connect base use cases to their mandatory sub-behaviors, such as Assign "
    "Maintenance including Set Fee and Create Additional Charge.")
image(doc, os.path.join(DIAGRAM_DIR, "usecase.png"), width_in=6.3)
body(doc, "Figure 3.3 — DwellManager Use Case Diagram",
     italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=10)

h(doc, "3.4 Module Description", 2)
h(doc, "1. Admin Module", 3)
bullet(doc, "Flat Management: Create, edit, deactivate flats. Set base_maintenance_amount.")
bullet(doc, "Resident Management: Register residents, link to flats, manage roles and statuses.")
bullet(doc, "Maintenance Assignment: View pending requests, assign contractor, set fee, update status.")
bullet(doc, "Billing Overview: View all unpaid/paid charges, total outstanding.")
bullet(doc, "Dashboard Analytics: Total flats, active residents, pending requests, visitors inside, "
            "total unpaid.")

h(doc, "2. Guard Module", 3)
bullet(doc, "Visitor Check-In: Record name, contact, target flat, purpose, vehicle details.")
bullet(doc, "Visitor Check-Out: Timestamp exit, set status to Checked-Out.")
bullet(doc, "Visitor Log: Searchable history by name, contact, flat number, or date.")

h(doc, "3. Resident Module", 3)
bullet(doc, "Billing Dashboard: View base maintenance and additional charges.")
bullet(doc, "Payment Processing: Pay via UPI, Net Banking, or Cash; receive receipt reference.")
bullet(doc, "Maintenance Requests: Submit request with category and description.")
bullet(doc, "Request Tracking: View status (Pending → Assigned → In Progress → Completed).")

h(doc, "3.5 Input Design", 2)
body(doc, "Input is handled through Django ModelForms with:")
bullet(doc, "Client-side HTML5 validation (required, pattern, min, max, type).")
bullet(doc, "Server-side validation via Django forms (clean() methods).")
bullet(doc, "CSRF tokens on all state-changing forms.")
bullet(doc, "Server-side role guards via decorators (@admin_required, @guard_required, "
            "@resident_required).")

h(doc, "3.6 Output Design", 2)
body(doc, "Output is rendered using Django templates with custom CSS:")
bullet(doc, "Role-Aware Sidebar: Dynamic navigation based on request.user.role.")
bullet(doc, "Dashboard Cards: Key metrics for each role.")
bullet(doc, "Data Tables: Sortable, paginated lists for flats, residents, maintenance, visitors, payments.")
bullet(doc, "Receipts: Formatted payment receipts with reference numbers.")

# ---------- CHAPTER 4 ----------
page_break(doc)
chapter_divider(doc, "4", "System Environment")

h(doc, "4.1 Introduction", 2)
body(doc, "The system environment encompasses the browser client, Django WSGI server, and SQLite "
          "database.")

h(doc, "4.2 Software Requirement Specification", 2)
table(doc, ["Component", "Specification"], [
    ["Operating System", "Windows 10/11, Linux (Ubuntu 22.04 LTS)"],
    ["Development Platform", "Python 3.10+ / Django"],
    ["Front-End", "HTML5, CSS3, custom JavaScript"],
    ["Database", "SQLite (current configuration)"],
    ["Web Server", "Django Development Server"],
    ["Browser", "Chrome, Firefox, Edge, Safari"],
])

h(doc, "4.3 Hardware Requirement Specification", 2)
body(doc, "Server/Developer Side: Intel Core i5 or equivalent, 8 GB RAM (16 GB recommended), "
          "256 GB SSD.")
body(doc, "Client Side: Any internet-enabled device with a modern browser, 2 GB RAM minimum.")

h(doc, "4.4 Tools and Platforms", 2)
h(doc, "4.4.1 Django", 3)
bullet(doc, "MVT Architecture: Decoupled models, views, and templates.")
bullet(doc, "ORM: Python-based database operations with automatic SQL parameterization.")
bullet(doc, "Built-in Security: CSRF protection, XSS prevention, SQL injection defense.")
bullet(doc, "Transaction Support: transaction.atomic() for atomic database operations.")

h(doc, "4.4.2 SQLite", 3)
bullet(doc, "Zero Configuration: No separate server process.")
bullet(doc, "ACID Compliance: Reliable transaction execution.")
bullet(doc, "Django Compatibility: Native backend support.")
bullet(doc, "Suitable Scale: Adequate for single-complex deployments.")

# ---------- CHAPTER 5 ----------
page_break(doc)
chapter_divider(doc, "5", "System Implementation")

h(doc, "5.1 Introduction", 2)
body(doc, "Implementation translates design into executable Django code.")

h(doc, "5.2 Coding", 2)
body(doc, "The codebase follows PEP 8 and modular Django app structure (api/ app containing models, "
          "forms, views, permissions, serializers, tests).")

h(doc, "5.2.1 Coding Standards", 3)
bullet(doc, "PEP 8 Compliance: Python style guide adherence.")
bullet(doc, "Descriptive Naming: Domain-explicit names (e.g., admin_maintenance_assign).")
bullet(doc, "Docstrings: All views documented.")

h(doc, "5.3 Code Validation and Optimization", 2)
bullet(doc, "N+1 Prevention: select_related() used for foreign key relationships.")
bullet(doc, "Atomic Transactions: transaction.atomic() + select_for_update() for financial operations.")
bullet(doc, "IDOR Protection: Resident views derive flat from request.user.flat, never from user input.")

h(doc, "5.3.1 Debugging", 3)
body(doc, "Debugging via Django’s debug toolbar, pdb, and structured logging.")

# ---------- CHAPTER 6 ----------
page_break(doc)
chapter_divider(doc, "6", "System Testing")

h(doc, "6.1 Introduction", 2)
body(doc, "Testing validates that the system meets functional specifications.")

h(doc, "6.2 Types of Testing", 2)
h(doc, "6.2.1 Unit Testing", 3)
bullet(doc, "Flat CRUD operations.")
bullet(doc, "Resident management.")
bullet(doc, "Maintenance request lifecycle.")
bullet(doc, "Atomic billing (assignment + charge creation).")
bullet(doc, "Payment processing with double-payment protection.")
bullet(doc, "Visitor check-in/checkout.")
bullet(doc, "IDOR/security tests (cross-flat access denied).")
bullet(doc, "Authentication and role-based redirects.")

h(doc, "6.2.2 System Testing", 3)
body(doc, "End-to-end workflows: resident registration → maintenance request → admin assignment → "
          "charge creation → resident payment → receipt.")

h(doc, "6.2.3 Integration Testing", 3)
bullet(doc, "Signal triggers: Maintenance assignment creates Payment record.")
bullet(doc, "Database transactions: Payment updates atomic.")
bullet(doc, "Template contexts: Views pass complete, sanitized context.")

h(doc, "6.2.4 Test Cases Verification Table", 3)
table(doc, ["Test ID", "Module", "Scenario", "Expected Result", "Status"], [
    ["TC_AUTH_01", "Authentication", "Admin login redirect", "Redirect to /dashboard/admin/", "Pass"],
    ["TC_AUTH_02", "Authentication", "Resident access to admin route", "403 Forbidden", "Pass"],
    ["TC_FLAT_01", "Flat Mgmt", "Create new flat", "Flat saved; visible in list", "Pass"],
    ["TC_MAINT_01", "Maintenance", "Resident raises request", "Ticket saved; status Pending", "Pass"],
    ["TC_MAINT_02", "Maintenance", "Admin assigns with fee", "Request Assigned; Payment created", "Pass"],
    ["TC_PAY_01", "Payment", "Resident pays charge", "Status Paid; receipt generated", "Pass"],
    ["TC_VIS_01", "Visitor", "Guard checks in visitor", "Visitor Inside; visible in dashboard", "Pass"],
    ["TC_VIS_02", "Visitor", "Guard checks out visitor", "Status Checked-Out; exit time set", "Pass"],
    ["TC_SEC_01", "Security", "Cross-flat payment access", "403/404 denied", "Pass"],
])

# ---------- CHAPTER 7 ----------
page_break(doc)
chapter_divider(doc, "7", "System Maintenance")

h(doc, "7.1 Introduction", 2)
body(doc, "System maintenance ensures ongoing reliability, security, and performance.")

h(doc, "7.2 Maintenance Types", 2)
bullet(doc, "Corrective: Fixing bugs discovered in production.")
bullet(doc, "Adaptive: Updating dependencies (Django, Python versions).")
bullet(doc, "Perfective: Enhancing UI, optimizing queries, adding features.")
bullet(doc, "Preventive: Security audits, database vacuuming, code refactoring.")

# ---------- CHAPTER 8 ----------
page_break(doc)
chapter_divider(doc, "8", "Future Enhancement")

h(doc, "8.1 Introduction", 2)
body(doc, "DwellManager provides a solid foundation for apartment complex management. Future "
          "iterations can expand capabilities.")

h(doc, "8.2 Merits of the System", 2)
bullet(doc, "Three-Role Clarity: Admin, Guard, Resident each see only relevant tools.")
bullet(doc, "Complete Visitor Logging: Real-time inside/outside visibility with vehicle tracking.")
bullet(doc, "Unified Billing: Single Payment model handles base and additional charges.")
bullet(doc, "Atomic Financial Operations: No race conditions in payment processing.")
bullet(doc, "Server-Side Security: IDOR protection, role guards, CSRF tokens.")
bullet(doc, "Custom Glassmorphism UI: Modern, responsive dark theme.")

h(doc, "8.3 Limitations", 2)
bullet(doc, "Web-Only Architecture: No native mobile apps.")
bullet(doc, "SQLite Database: May need migration to PostgreSQL for large-scale deployments.")
bullet(doc, "No IoT Integration: Smart locks or utility meters not supported.")
bullet(doc, "Domestic Currency Only: No multi-currency support.")
bullet(doc, "Internet Dependency: Requires active connectivity.")

h(doc, "8.4 Future Enhancements", 2)
bullet(doc, "Native Mobile Apps: Android/iOS with push notifications for visitors and bills.")
bullet(doc, "PostgreSQL Migration: For multi-complex scalability.")
bullet(doc, "IoT Integration: Smart locks, digital utility meters.")
bullet(doc, "AI Predictive Maintenance: Forecast equipment failures.")
bullet(doc, "Multi-Language Support: Malayalam, Tamil, Hindi.")
bullet(doc, "Payment Gateway Integration: Online payment processing.")

# ---------- CHAPTER 9 ----------
page_break(doc)
chapter_divider(doc, "9", "Conclusion")

h(doc, "9.1 Conclusion", 2)
body(doc,
    "DwellManager successfully resolves the systemic inefficiencies of traditional apartment "
    "management by providing an automated, transparent, role-based digital platform. Built with "
    "Python, Django, and custom glassmorphism CSS, the system connects Admins, Guards, and "
    "Residents in a unified operational environment.")
body(doc,
    "A central achievement is the atomic maintenance-to-charge pipeline: when an Admin assigns a "
    "maintenance request with a fee, a linked Additional Charge Payment record is created in the "
    "same database transaction — eliminating race conditions and manual billing errors.")
body(doc,
    "The Visitor Logging module provides real-time gate security with vehicle tracking, while the "
    "unified Payment model simplifies billing for both base maintenance and repair charges. "
    "Server-side data isolation and role-based decorators ensure residents can only access their "
    "own flat’s data.")
body(doc,
    "While acknowledging current boundaries — SQLite database, web-only architecture, and domestic "
    "currency scope — the system establishes a robust, extensible foundation. Future enhancements "
    "such as native mobile apps, PostgreSQL migration, and IoT integration can readily expand its "
    "capabilities.")
body(doc,
    "In conclusion, DwellManager effectively fulfills all core objectives, demonstrating how "
    "full-stack Django solutions can modernize apartment complex administration.")

# ---------- CHAPTER 10 ----------
page_break(doc)
chapter_divider(doc, "10", "Bibliography")

h(doc, "10.1 Books", 2)
bullet(doc, "Pressman, R. S., & Maxim, B. R. (2019). Software Engineering: A Practitioner's "
            "Approach (9th ed.). McGraw-Hill Education.")
bullet(doc, "Lutz, M. (2013). Learning Python (5th ed.). O'Reilly Media.")
bullet(doc, "Holovaty, A., & Kaplan-Moss, J. (2009). The Definitive Guide to Django: Web "
            "Development Done Right. Apress.")
bullet(doc, "Fowler, M. (2003). UML Distilled: A Brief Guide to the Standard Object Modeling "
            "Language (3rd ed.). Addison-Wesley Professional.")

h(doc, "10.2 Web Resources", 2)
bullet(doc, "Django Software Foundation. (2026). Django Documentation. "
            "https://docs.djangoproject.com/")
bullet(doc, "Python Software Foundation. (2026). Python 3 Documentation. "
            "https://docs.python.org/3/")
bullet(doc, "Mozilla Developer Network (MDN). (2026). Web Docs: HTML, CSS, JavaScript. "
            "https://developer.mozilla.org/")

# ---------- CHAPTER 11 ----------
page_break(doc)
chapter_divider(doc, "11", "Annexures")

h(doc, "11.1 Screenshots", 2)
body(doc, "[Insert DwellManager system screenshots here — Login page, Admin Dashboard, Guard "
          "Dashboard, Resident Dashboard, Visitor Log, Maintenance Assignment, Payment Receipt.]")

# ---------- SAVE ----------
output = "DwellManager_Project_Documentation.docx"
doc.save(output)
print(f"\n✅ Documentation generated: {output}")
print(f"✅ Diagrams saved in: {os.path.abspath(DIAGRAM_DIR)}/")
print("\nNext steps:")
print("  1. Open the DOCX in Microsoft Word.")
print("  2. Replace bracketed placeholders (name, guide, year).")
print("  3. Insert real screenshots in Chapter 11.")
print("  4. Update the Table of Contents page numbers if needed.")