#!/usr/bin/env python3
"""SFX1 — remise en page des 6 documents officiels (grilles horaires et descriptions).

Le texte des descriptions est extrait automatiquement des PDF originaux (aucune réécriture),
puis remis en forme ; les grilles sont retranscrites mot pour mot. Rendu PDF par Chrome.
Usage : python3 make_pdfs.py <dossier_originaux> <dossier_sortie>
"""
import sys, re, html, base64
from pathlib import Path
import pdfplumber
from playwright.sync_api import sync_playwright

SRC = Path(sys.argv[1]); OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
ASSETS = Path(__file__).resolve().parent / "assets"
esc = html.escape

def b64(p): return base64.b64encode(Path(p).read_bytes()).decode()
LOGO = b64(ASSETS / "logo-sfxun.jpg")
FONTS = "".join(
    f'@font-face{{font-family:"{fam}";src:url(data:font/woff;base64,{b64(ASSETS / f)}) format("woff");font-weight:{w}}}'
    for fam, f, w in [("Inter", "inter-400.woff", "400"), ("Inter", "inter-600.woff", "500 650"), ("Inter", "inter-700.woff", "700 1000"),
                      ("Inter Display", "interdisplay-600.woff", "500 700"), ("Inter Display", "interdisplay-800.woff", "750 1000")])

CSS = FONTS + """
@page{size:A4;margin:14mm 0 14mm}
@page:first{margin-top:0}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;font-family:Inter,sans-serif;color:#231c20;font-size:10.4pt;line-height:1.55}
:root{--wine:#98052b;--deep:#5c0a22;--blush:#f7edef;--cream:#faf7f5;--line:#eadfe3;--nl:#e8790a;--muted:#6f666b}
.page{width:210mm;padding:0 16mm 0;position:relative}
.band{margin:0 -16mm 9mm;padding:9mm 16mm 8mm;background:linear-gradient(115deg,#4b0519 0%,#98052b 62%,#b3123c 100%);color:#fff;position:relative;overflow:hidden;display:flex;gap:9mm;align-items:center}
.band:after{content:"";position:absolute;right:-28mm;top:-30mm;width:85mm;height:85mm;border-radius:50%;border:9mm solid #ffffff14}
.band:before{content:"";position:absolute;right:30mm;bottom:-38mm;width:60mm;height:60mm;border-radius:50%;background:#ffffff0d}
.logo{background:#fff;border-radius:3.5mm;padding:2.6mm 3.2mm;flex-shrink:0;box-shadow:0 2mm 6mm #0003}
.logo img{height:15mm;display:block}
.band .eyebrow{font-size:7.6pt;letter-spacing:.2em;text-transform:uppercase;color:#ffcfd9;font-weight:700;margin:0 0 1.5mm}
.band h1{font-family:"Inter Display";font-weight:800;font-size:23pt;line-height:1.05;letter-spacing:-.02em;margin:0}
.band .pills{display:flex;gap:2mm;margin-top:3mm;flex-wrap:wrap}
.band .pill{background:#ffffff22;border:1px solid #ffffff55;border-radius:20mm;padding:1mm 3.2mm;font-size:8pt;font-weight:600}
h2.sec{font-family:"Inter Display";font-weight:800;font-size:13.5pt;color:var(--deep);margin:7mm 0 3mm;display:flex;align-items:center;gap:3mm}
h2.sec:before{content:"";width:6mm;height:1.2mm;border-radius:1mm;background:var(--wine)}
/* tableau formation commune */
table.fco{width:100%;border-collapse:separate;border-spacing:0;font-size:10pt;border:1px solid var(--line);border-radius:3mm;overflow:hidden}
table.fco th,table.fco td{padding:2.05mm 3.4mm;border-bottom:1px solid #f1e9ec;text-align:left}
table.fco thead th{background:var(--blush);color:var(--wine);font-size:7.6pt;letter-spacing:.12em;text-transform:uppercase;font-weight:800}
table.fco .n{text-align:center;width:27mm;font-weight:800;font-variant-numeric:tabular-nums}
table.fco tbody tr:nth-child(even) td{background:#fdfafb}
table.fco tr.nl td{background:#fff4e6!important}
table.fco tr.nl td:first-child:after{content:"NL";margin-left:2.2mm;font-size:6.5pt;font-weight:900;color:#fff;background:var(--nl);border-radius:1mm;padding:.3mm 1.2mm;vertical-align:1px}
table.fco tr.sub td{background:var(--cream)!important;font-weight:700;color:var(--deep)}
table.fco tfoot td{background:#2a1a21;color:#fff;font-weight:800;border:0}
.small{font-size:8.4pt;color:var(--muted)}
.legend{display:flex;gap:5mm;align-items:center;margin:2.2mm 0 0;font-size:8.2pt;color:var(--muted)}
.legend b{display:inline-block;font-size:6.5pt;font-weight:900;color:#fff;background:var(--nl);border-radius:1mm;padding:.3mm 1.2mm;margin-right:1.5mm}
/* lignes de choix */
.choices{border:1px solid var(--line);border-radius:3mm;overflow:hidden}
.choices .head{gap:3mm;background:var(--blush);color:var(--wine);font-size:7.6pt;letter-spacing:.12em;text-transform:uppercase;font-weight:800;padding:2.2mm 3.4mm;display:flex;justify-content:space-between}
.line{display:grid;grid-template-columns:1fr 24mm;border-top:1px solid #f1e9ec}
.line .opts{display:flex;flex-wrap:wrap;gap:2mm;padding:2.6mm 3.4mm;align-items:center}
.opt{display:inline-flex;align-items:center;gap:2mm;border:1px solid #e3d2d8;border-radius:2mm;padding:1.6mm 2.6mm;font-size:9.4pt;font-weight:600;background:#fff}
.opt:before{content:"";width:3.4mm;height:3.4mm;border:1.4px solid var(--wine);border-radius:.8mm;flex-shrink:0}
.opt.act{font-style:italic;border-style:dashed}
.opt.empty{visibility:hidden}
.ou{font-size:8pt;color:var(--muted)}
.line .hrs{border-left:1px solid #f1e9ec;display:flex;flex-direction:column;justify-content:center;align-items:stretch;background:#fcf8f9}
.line .hrs span{display:block;text-align:center;font-weight:800;font-size:9pt;padding:.75mm 0;border-bottom:1px dashed #eadde2;font-variant-numeric:tabular-nums}
.line .hrs span:last-child{border-bottom:0}
.line .hrs.one{justify-content:center;font-weight:900;color:var(--wine);text-align:center;font-size:11pt}
.choices .total{display:grid;grid-template-columns:1fr 24mm;background:#2a1a21;color:#fff;font-weight:800;font-size:9pt}
.choices .total div{padding:2.2mm 3.4mm}.choices .total div:last-child{text-align:center;border-left:1px solid #ffffff22}
.rules{list-style:none;padding:0;margin:4mm 0 0;display:grid;gap:1.6mm}
.rules li{position:relative;padding-left:7mm;font-size:9.4pt}
.rules li:before{content:"✓";position:absolute;left:0;top:.2mm;width:4.6mm;height:4.6mm;border-radius:50%;background:var(--wine);color:#fff;font-size:7pt;font-weight:900;display:grid;place-items:center}
.rules li.strong{font-weight:700}
.note{font-size:8.6pt;font-style:italic;color:var(--muted);margin:2mm 0 0}
.twocol{display:grid;grid-template-columns:1fr 1fr;gap:6mm}
/* descriptions */
.intro-strip{display:flex;gap:2.5mm;flex-wrap:wrap;margin:-2mm 0 6mm}
.intro-strip span{font-size:8pt;font-weight:700;color:var(--wine);background:var(--blush);border-radius:20mm;padding:1.1mm 3mm}
.course{margin:0 0 6mm;break-inside:auto}
.course-head{display:grid;grid-template-columns:12mm 1fr auto;gap:3.5mm;align-items:center;background:linear-gradient(90deg,var(--blush),#fff);border-left:1.6mm solid var(--wine);border-radius:0 3mm 3mm 0;padding:2.6mm 4mm 2.6mm 3mm;margin-bottom:3mm;break-after:avoid}
.course-head .ico{width:12mm;height:12mm;border-radius:3mm;background:#fff;display:grid;place-items:center;font-size:17pt;box-shadow:0 .6mm 2mm #98052b22}
.course-head .num{font-size:7.5pt;font-weight:800;color:var(--wine);letter-spacing:.14em;text-transform:uppercase}
.course-head h2{font-family:"Inter Display";font-weight:800;font-size:13.5pt;line-height:1.15;margin:.4mm 0 0;color:#2a1a21}
.course-head .h{background:var(--wine);color:#fff;font-weight:800;font-size:8.6pt;border-radius:20mm;padding:1.2mm 3.4mm;white-space:nowrap;max-width:62mm;white-space:normal;text-align:center}
.course p{margin:0 0 2.4mm;text-align:justify;hyphens:auto}
.course h3{font-family:"Inter Display";font-size:11pt;font-weight:700;color:var(--wine);margin:3.6mm 0 1.6mm;break-after:avoid}
.course h4{font-size:10.2pt;font-weight:700;color:var(--deep);margin:3mm 0 1.2mm;break-after:avoid;display:flex;align-items:center;gap:2mm}
.course h4:before{content:"";width:2mm;height:2mm;border-radius:50%;background:var(--wine);flex-shrink:0}
.course ul{margin:0 0 2.6mm;padding:0;list-style:none;display:grid;gap:.8mm;background:var(--cream);border-radius:2.5mm;padding:2.6mm 4mm}
.course li{position:relative;padding-left:5mm}
.course li:before{content:"";position:absolute;left:.6mm;top:2.15mm;width:1.8mm;height:1.8mm;border-radius:50%;border:1.3px solid var(--wine)}
.course strong{font-weight:700;color:#2a1a21}
.grid .band{padding:7mm 16mm 6.5mm;margin-bottom:5mm}
.grid h2.sec{margin:4.5mm 0 2.2mm;font-size:12.5pt}
.grid table.fco{font-size:9.4pt}.grid table.fco th,.grid table.fco td{padding:1.45mm 3.2mm}
.grid .line .opts{padding:1.8mm 3mm;gap:1.6mm}.grid .opt{padding:1.1mm 2.2mm;font-size:8.9pt}
.grid .line .hrs span{padding:.45mm 0;font-size:8.6pt}
.grid .rules{margin-top:3mm;gap:1.1mm}.grid .rules li{font-size:9pt}
.grid .legend{margin-top:1.6mm}
.split{display:grid;grid-template-columns:1.45fr 1fr;gap:6mm;align-items:start}
.split table.fco .n{width:16mm}.split table.fco th,.split table.fco td{padding:1.45mm 2.4mm}.split .choices .line{grid-template-columns:1fr 14mm}.split .choices .total{grid-template-columns:1fr 14mm}
.keep{break-before:avoid}.course-head{break-after:avoid;page-break-after:avoid}.course h3,.course h4{page-break-after:avoid}
.valid{margin-top:6mm;border:1px dashed #d99a2b;background:#fff8ea;color:#6d4400;border-radius:3mm;padding:2.6mm 3.6mm;font-size:8.2pt}
"""

FOOTER = ('<div style="width:100%;font-family:Arial;font-size:7px;color:#7a6f74;padding:0 16mm;display:flex;justify-content:space-between">'
          '<span>Collège Saint-François-Xavier I · Rue de Rome 18, 4800 Verviers · 087/39.39.39 · info@sfx1.org</span>'
          '<span>Mise en page SFX1 – contenu identique au document officiel · <span class="pageNumber"></span>/<span class="totalPages"></span></span></div>')

def band(eyebrow, title, pills):
    return (f'<div class="band"><div class="logo"><img src="data:image/jpeg;base64,{LOGO}" alt="SFXun"></div><div>'
            f'<p class="eyebrow">{eyebrow}</p><h1>{title}</h1><div class="pills">{"".join(f"<span class=pill>{p}</span>" for p in pills)}</div></div></div>')

def doc(body):
    return f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'

# ------------------------------------------------------------------ GRILLES (texte des originaux)
def fco_table(head, rows, total, nl_rows):
    th = "".join(f'<th class="{"n" if i else ""}">{h}</th>' for i, h in enumerate(head))
    tb = ""
    for r in rows:
        cls = "nl" if r[0] in nl_rows else ("sub" if r[0].startswith("Activités complémentaires") else "")
        tb += f'<tr class="{cls}">' + "".join(f'<td class="{"n" if i else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>"
    tf = "<tr>" + "".join(f'<td class="{"n" if i else ""}">{c}</td>' for i, c in enumerate(total)) + "</tr>" if total else ""
    return f'<table class="fco"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody><tfoot>{tf}</tfoot></table>'

def choices(title, lines, total_label, total_val, hrs_title="Heures"):
    out = f'<div class="choices"><div class="head"><span>{title}</span><span>{hrs_title}</span></div>'
    for opts, hrs in lines:
        o = '<span class="ou">ou</span>'.join(f'<span class="opt{" act" if x.startswith("~") else ""}">{x.lstrip("~")}</span>' for x in opts)
        if isinstance(hrs, list):
            h = '<div class="hrs">' + "".join(f"<span>{v}</span>" for v in hrs) + "</div>"
        else:
            h = f'<div class="hrs one">{hrs}</div>'
        out += f'<div class="line"><div class="opts">{o}</div>{h}</div>'
    if total_val:
        out += f'<div class="total"><div>{total_label}</div><div>{total_val}</div></div>'
    return out + "</div>"

def grille_d1():
    rows = [["Religion", "2", "2"], ["Français", "6", "5"], ["Mathématiques", "4", "5"],
            ["Langue moderne I <span class=small>(néerlandais, anglais ou allemand)</span>", "4", "4"],
            ["Étude du milieu*", "4", "4"], ["Sciences*", "3", "3"], ["Éducation physique", "3", "3"],
            ["Éducation par la technologie", "1", "1"], ["Éducation artistique (dessin)", "1", "1"],
            ["Activités complémentaires (voir ci-dessous)", "4", "4"]]
    t = fco_table(["Formation commune obligatoire", "1re année", "2e année"], rows, ["", "32", "32"], {"Étude du milieu*", "Sciences*"})
    c1 = choices("Activités complémentaires en première année",
                 [(["Latin"], "2"), (["Méthode de travail"], "1"), (["Informatique", "Atelier de conversation*"], "1")], "", "4")
    c2 = choices("Activités complémentaires en deuxième année",
                 [(["Latin", "Sciences", "Socio-économie", "Activités musicales", "AC anglais", "Informatique"], "2"),
                  (["Latin", "Sciences", "Socio-économie", "Arts de la parole", "Activités sportives", "Initiation à la culture antique (grec)"], "2")],
                 "Attention : une seule fois la même activité !", "4")
    body = band("Enseignement secondaire · Premier degré", "Grille horaire du premier degré", ["1re année", "2e année", "Périodes par semaine"]) + \
        '<div class="split"><div><h2 class="sec">Formation commune obligatoire</h2>' + t + \
        '<div class="legend"><span><b>NL</b>* Cours en néerlandais pour l’immersion</span></div></div>' + \
        '<div><h2 class="sec">Activités complémentaires</h2>' + c1 + \
        '<p class="note">*Pour les élèves en immersion uniquement et obligatoirement</p></div></div><div style="height:5mm"></div>' + c2 + \
        '<ul class="rules"><li>Un seul choix sur la même ligne.</li><li>Le choix de 2<sup>ème</sup> année n’engage en rien le choix de 3<sup>ème</sup> année.</li></ul>'
    return f'<div class="page grid">{body}</div>'

def grille_d2():
    rows = [["Religion", "2", "2"], ["Français", "5", "5"], ["Mathématiques", "5", "5"],
            ["Langue moderne I <span class=small>(néerlandais, anglais ou allemand)</span>", "4", "4"],
            ["Histoire", "2*", "2*"], ["Géographie", "2*", "2*"], ["Éducation physique", "2", "2"], ["Sciences", "3*", "3"]]
    t = fco_table(["Formation commune obligatoire", "3ème année", "4ème année"], rows, ["Total de la formation commune obligatoire", "25", "25"], {"Histoire", "Géographie", "Sciences"})
    c = choices("Options et activités complémentaires au deuxième degré",
                [(["Latin 4h", "Sciences économiques 4h", "Arts d’expression 4h", "Sciences 5h"], ["26", "27"]),
                 (["~*Informatique 2h"], ["28", "29"]),
                 (["Langue moderne II Néerlandais 4h", "Langue moderne II Anglais 4h", "Langue moderne II Allemand 4h"], ["30", "31", "32", "33"]),
                 (["~*Grec 2h", "~*Labo sciences immersion 1h"], ["34", "35"])],
                "", "De 4h à 8h", "Période(s) par semaine")
    body = band("Enseignement secondaire · Deuxième degré", "Grille horaire du deuxième degré", ["3ème année", "4ème année", "Période(s) par semaine"]) + \
        '<h2 class="sec">Formation commune obligatoire</h2>' + t + \
        '<div class="legend"><span><b>NL</b>* Cours en néerlandais pour l’immersion</span></div>' + \
        '<h2 class="sec">Options et activités complémentaires</h2>' + c + \
        '<ul class="rules"><li>Un seul choix sur la même ligne. Minimum légal : 28 heures. Maximum légal : 34 heures.</li>' \
        '<li class="strong">Au moins une option de base : latin, sciences-éco., arts d’ex., sciences 5, langue moderne II.</li>' \
        '<li class="strong">Les élèves d’immersion ne peuvent pas choisir sciences 5h.</li>' \
        '<li class="strong">Indiquez votre choix en traçant une diagonale dans les cases des options ou activités choisies.</li></ul>' \
        '<p class="note">* Cocher la case si vous choisissez cette activité complémentaire en plus de votre ou vos options de base.</p>'
    return f'<div class="page grid">{body}</div>'

def grille_d3():
    rows = [["Religion", "2"], ["Français", "4"], ["Mathématiques", "4"],
            ["Langue moderne I <span class=small>(néerlandais, anglais ou allemand)</span>", "4"],
            ["Histoire*", "2"], ["Géographie*", "2"], ["Éducation physique", "2"], ["Sciences", "3"]]
    t = fco_table(["Formation commune obligatoire", "5 et 6ème années<br><span style='text-transform:none;letter-spacing:0;font-weight:500'>Période(s) par semaine</span>"],
                  rows, ["Total de la formation commune obligatoire", "23"], {"Histoire*", "Géographie*"})
    c = choices("Options et activités complémentaires au troisième degré",
                [(["Latin 4h", "Sciences-économiques 4h", "Arts d’expression 4h", "Sciences 7h"], ["1", "1", "1", "1"]),
                 (["Langue moderne II Néerlandais 4h", "Langue moderne II Anglais 4h", "Langue moderne II Allemand 4h"], ["1", "1", "1", "1"]),
                 (["Mathématiques 6h"], ["1", "1"]),
                 (["~Grec 2h", "~Math. suppl. 2h", "~Espagnol 2h"], ["1", "1"])],
                "", "6 à 12h", "Période(s)")
    body = band("Enseignement secondaire · Troisième degré", "Grille horaire du troisième degré", ["5ème année", "6ème année", "Période(s) par semaine"]) + \
        '<h2 class="sec">Formation commune obligatoire</h2>' + t + \
        '<div class="legend"><span><b>NL</b>* Cours en néerlandais pour l’immersion</span></div>' + \
        '<h2 class="sec">Options et activités complémentaires</h2>' + c + \
        '<ul class="rules"><li>Un seul choix sur la même ligne. Minimum légal : 28 heures.</li>' \
        '<li>Maximum légal 32 heures. Possibilité de 34, 35 voire 36 périodes moyennant conditions (voir ci-après).</li></ul>'
    return f'<div class="page grid">{body}</div>'

# ------------------------------------------------------------------ DESCRIPTIONS (texte extrait)
BUL = "●·.-•"
ICONS = [("LATIN ou GREC", "🏛️"), ("LANGUES ANCIENNES", "🏛️"), ("LATIN", "🏛️"), ("ANTIQUE", "🏺"), ("SOCIO", "🤝"), ("ECONOM", "📊"),
         ("MATH", "📐"), ("SCIENTIFIQUES", "🧪"), ("SCIENCES", "🔬"), ("ARTISTIQUES", "🎭"), ("EXPRESSION", "🎭"), ("ESPAGNOL", "💬"),
         ("LANGUE", "💬"), ("SPORTIVES", "🚴"), ("ACCOMPAGNEMENT", "🧭"), ("INFORMATIQUE", "💻")]

def icon(t):
    u = t.upper().replace("É", "E")
    for k, v in ICONS:
        if k.upper().replace("É", "E") in u: return v
    return "📘"

def runs(chars):
    """Texte d'une ligne avec les passages en gras conservés."""
    out, cur, bold = [], "", None
    for c in chars:
        b = "F2" in c["fontname"] or "Bold" in c["fontname"]
        if bold is None: bold = b
        if b != bold and c["text"].strip():
            out.append((bold, cur)); cur, bold = "", b
        cur += c["text"]
    out.append((bold, cur))
    return out

def extract(pdf_path):
    items = []  # (kind, payload)
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages:
            for l in p.extract_text_lines(keep_blank_chars=True):
                ch = [c for c in l["chars"]]
                size = round(ch[0]["size"]); txt = l["text"].strip()
                if not txt: continue
                boldness = sum(("F2" in c["fontname"] or "Bold" in c["fontname"]) for c in ch if c["text"].strip()) / max(1, len([c for c in ch if c["text"].strip()]))
                items.append(dict(text=txt, x0=l["x0"], x1=l["x1"], top=l["top"], size=size, bold=boldness, chars=ch, page=p.page_number))
    return items

def html_runs(line):
    s = ""
    for b, t in runs(line["chars"]):
        t = esc(t)
        s += f"<strong>{t}</strong>" if b and t.strip() else t
    return s.strip()

def build_description(items):
    title = items[0]["text"]; items = items[1:]
    courses, cur, block, prev = [], None, None, None
    def flush():
        nonlocal block
        if block and cur is not None: cur["body"].append(block)
        block = None
    for it in items:
        t = it["text"]
        if it["size"] >= 15:
            flush()
            if prev and prev["size"] >= 15 and cur and not cur["body"]:
                cur["head"] += " " + t; prev = it; continue
            cur = {"head": t, "body": []}; courses.append(cur); prev = it; continue
        if it["size"] == 14:
            flush(); cur["body"].append(("h3", html_runs(it))); prev = it; continue
        is_bul = t[0] in BUL and (len(t) > 1 and (t[1] == " " or t[0] in "●·•"))
        if it["bold"] >= 0.85 and it["x1"] < 480:
            flush(); cur["body"].append(("h4", html_runs(it))); prev = it; continue
        if is_bul and not (it["bold"] >= 0.85):
            item = re.sub(r"^(<strong>)?\s*[●·.\-•]\s*", r"\1", html_runs(it))
            if block and block[0] == "ul":
                block[1].append(item)
            else:
                flush(); block = ["ul", [item]]
            prev = it; continue
        if block and block[0] == "ul" and (it["x0"] > 85 or (prev is not None and prev["x1"] > 480 and (prev["page"] != it["page"] or it["top"] - prev["top"] < 22))):
            block[1][-1] += " " + html_runs(it); prev = it; continue
        # paragraphe
        new_para = True
        if block and block[0] == "p" and prev is not None:
            same_page = prev["page"] == it["page"]
            gap = it["top"] - prev["top"] if same_page else 14.6
            new_para = gap > 22 or prev["x1"] < 470
        if new_para:
            flush(); block = ["p", html_runs(it)]
        else:
            block[1] += " " + html_runs(it)
        prev = it
    flush()
    return title, courses

def render_block(b):
    if b[0] == "p": return f"<p>{b[1]}</p>"
    if b[0] == "ul": return "<ul>" + "".join(f"<li>{x}</li>" for x in b[1]) + "</ul>"
    if b[0] == "h3": return f"<h3>{b[1]}</h3>"
    if b[0] == "h4": return f"<h4>{b[1]}</h4>"

HEAD_RE = re.compile(r"^(\d+)\.\s*(.+?)(?:\s*[-–]\s*(\d.*|\d+h.*))?$")

def description(code, nom, annees, pdf_path):
    title, courses = build_description(extract(pdf_path))
    secs, chips = "", []
    for c in courses:
        m = re.match(r"^(\d+)\.\s*(.*)$", c["head"])
        num, rest = m.group(1), m.group(2)
        mh = re.match(r"^(.*?)\s*[-–]\s*((?:\d+\s*h|\d+heures?).*)$", rest) or re.match(r"^(.*?)\s+(\d+h.*)$", rest)
        name, hrs = (mh.group(1), mh.group(2)) if mh else (rest, "")
        cn = re.sub(r"\s*[-–]\s*$", "", name).strip(); chips.append(esc(cn[:1].upper() + cn[1:].lower()))
        secs += (f'<section class="course"><div class="course-head" style="break-inside:avoid"><span class="ico">{icon(name)}</span><div><span class="num">{num}.</span>'
                 f'<h2>{esc(name)}</h2></div>{f"<span class=h>{esc(hrs)}</span>" if hrs else ""}</div>'
                 + (f'<div class="keep">{render_block(c["body"][0])}</div>' if c["body"] else "")
                 + "".join(render_block(b) for b in c["body"][1:]) + "</section>")
    body = band(f"Enseignement secondaire · {nom}", esc(title), [annees]) + \
        '<div class="intro-strip">' + "".join(f"<span>{x}</span>" for x in chips) + "</div>" + secs
    return f'<div class="page">{body}</div>', title, courses

def grille_tc():
    import json
    import glob
    T = json.load(open(SRC.parent / "data/contenus/tronc_commun.json"))["tronc_commun"]
    IMM = {(x["cours"], a) for x in T.get("immersion", []) for a in x["annees"]}
    th = '<tr><th>Discipline</th><th class="n">S1</th><th class="n">S2</th><th class="n">S3</th></tr>'
    tb = ""
    for grp in T["groupes"]:
        g, rows = grp["domaine"], grp["cours"]
        tb += f'<tr class="grp"><td colspan="4">{g}</td></tr>'
        for r in rows:
            r = [r["cours"], r["s1"], r["s2"], r["s3"]]
            cells = "".join(f'<td class="n"><span class="{"imm" if (r[0], c) in IMM and v != "–" else ""}">{v}</span></td>' for c, v in zip(["S1", "S2", "S3"], r[1:]))
            nm = f'<span class="immn">{r[0]}</span>' if any((r[0], c) in IMM for c in ["S1", "S2", "S3"]) else r[0]
            tb += f'<tr><td>{nm}</td>{cells}</tr>'
    tf = '<tr><td>Total</td><td class="n">32</td><td class="n">32</td><td class="n">32</td></tr>'
    css = '<style>.grid table.fco td,.grid table.fco th{padding:1.3mm 2.6mm!important;font-size:9.2pt}.grid .band{margin-bottom:4mm}table.fco{table-layout:fixed;width:100%}table.fco td:first-child,table.fco th:first-child{width:auto}table.fco .n{width:24mm!important}table.fco .obs{font-size:8pt;color:#6b5f64;width:58mm}table.fco tr.grp td{background:#f7e8ec;color:#98052b;font-weight:800;text-transform:uppercase;font-size:8pt;letter-spacing:.04em}table.fco tfoot .obs{color:#fff}.imm{display:inline-block;min-width:7mm;padding:.4mm 1.5mm;border-radius:2mm;background:#ffe94d}.immn{background:linear-gradient(transparent 15%,#ffe94d 15%,#ffe94d 85%,transparent 85%);padding:0 1mm}.leg{margin-top:3mm;font-size:9pt}</style>'
    body = css + band("Enseignement secondaire · Tronc commun", "Grille horaire du tronc commun", ["S1 · dès 2026-2027", "S2 · dès 2027-2028", "S3 · dès 2028-2029", "Périodes de 50 min par semaine"]) + \
        '<h2 class="sec">Disciplines et périodes hebdomadaires</h2>' + f'<table class="fco"><thead>{th}</thead><tbody>{tb}</tbody><tfoot>{tf}</tfoot></table>' + '<p class="leg"><span class="immn">Surligné en jaune</span> : cours en immersion, cours de néerlandais (langue moderne I) compris.</p>'
    return f'<div class="page grid">{body}</div>'

def render(pw, html_str, out):
    b = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = b.new_page(); pg.set_content(html_str, wait_until="load"); pg.wait_for_timeout(300)
    pg.pdf(path=str(out), format="A4", print_background=True, display_header_footer=True,
           header_template="<span></span>", footer_template=FOOTER, prefer_css_page_size=True)
    b.close()

if __name__ == "__main__":
    meta = {"D1": ("Premier degré", "1re et 2e années"), "D2": ("Deuxième degré", "3e et 4e années"), "D3": ("Troisième degré", "5e et 6e années")}
    import sys
    with sync_playwright() as pw:
        render(pw, doc(grille_tc()), OUT / "TC-Grille-horaire-tronc-commun-SFX1.pdf")
        if "tc" in sys.argv: raise SystemExit
        for code, fn in [("D1", grille_d1), ("D2", grille_d2), ("D3", grille_d3)]:
            render(pw, doc(fn()), OUT / f"{code}-Grille-horaire-SFX1.pdf")
            nom, an = meta[code]
            h, _, _ = description(code, nom, an, SRC / f"{code}-Description.pdf")
            Path(OUT / f"{code}-Description.html").write_text(doc(h))
            render(pw, doc(h), OUT / f"{code}-Description-SFX1.pdf")
    print("ok")
