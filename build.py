#!/usr/bin/env python3
"""SFX1 V5 — générateur de site statique multipage.

Usage : python3 build.py [dossier_de_sortie]
Produit un site HTML/CSS/JS autonome : chaque page est un vrai fichier .html,
testable par double-clic sur index.html, publiable tel quel sur Netlify ou OVHcloud.
Les contenus éditables sont dans data/*.json.
"""
import json, os, shutil, sys, html
from pathlib import Path

SRC = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else SRC.parent / "SFX1_V5_TEST"
VERSION = "V5"
SITE_URL = "https://www.sfx1.org"  # remplacé par options_site.adresse_site
OLD = "https://sites.google.com/sfx1.org/sfx-1-verviers/"
SHOW_VID = False  # remplacé après chargement des contenus
YT_CHANNEL = "https://www.youtube.com/@collegesaint-francois-xavi4810"

IMG = json.loads((SRC / "img-meta.json").read_text())
G = json.loads((SRC / "data/grilles.json").read_text())
# Contenus : un fichier JSON par rubrique (modifiable via l'espace d'administration)
C = {}
for _f in sorted((SRC / "data/contenus").glob("*.json")):
    C.update(json.loads(_f.read_text(encoding="utf-8")))
SCHEMA = json.loads((SRC / "data/schema.json").read_text())
def _tolist(items, fields):
    return [[it.get(k, "") for k in fields] if isinstance(it, dict) else it for it in items]
for _path, _fields in SCHEMA.items():
    if _path == "tronc_commun.groupes.cours": continue
    *_p, _last = _path.split(".")
    _o = C
    for _k in _p: _o = _o[_k]
    if _path == "tronc_commun.groupes":
        _o[_last] = [[g.get("domaine", ""), _tolist(g.get("cours", []), SCHEMA["tronc_commun.groupes.cours"])] if isinstance(g, dict) else g for g in _o[_last]]
    else:
        _o[_last] = _tolist(_o[_last], _fields)
SHOW_VID = bool(C.get("options_site", {}).get("afficher_videos"))
SITE_URL = C.get("options_site", {}).get("adresse_site", SITE_URL).rstrip("/")
PUBLIE = bool(C.get("options_site", {}).get("publication"))
PORTAIL = C.get("options_site", {}).get("portail_url", "espace.html")
from urllib.parse import urlparse as _up
_ag = C.get("agenda_app", {}).get("url", "")
AGENDA_ORIGIN = (" " + _up(_ag).scheme + "://" + _up(_ag).netloc) if _ag.startswith("http") else ""
# Documents déposés via l'administration : le fichier prime sur le lien
for _d in C["documents"]:
    if _d.get("fichier"):
        _d["u"] = _d["fichier"].lstrip("/"); _d["type"] = "pdf" if _d["u"].lower().endswith(".pdf") else _d.get("type", "pdf")
FOND = C["fondamental_url"]
PO = C["portes_ouvertes"]
TIMED = f'data-show-from="{PO["affichage_debut"]}" data-show-until="{PO["affichage_fin"]}"'
esc = html.escape

# ------------------------------------------------------------------ helpers
def upload_variants(path):
    """Photo déposée via l'administration (ex. /img/uploads/photo.jpg) : génère les tailles WebP/JPEG."""
    from PIL import Image, ImageOps
    src = SRC / path.lstrip("/")
    key = "u-" + src.stem.lower().replace(" ", "-")
    if key in IMG: return key
    if not src.exists(): return "cour-automne"
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    sizes = []
    for s in (1600, 800):
        if im.width < s and sizes: continue
        w = min(s, im.width); r = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        (OUT / "img").mkdir(parents=True, exist_ok=True)
        r.save(OUT / "img" / f"{key}-{w}.jpg", quality=82, optimize=True, progressive=True)
        r.save(OUT / "img" / f"{key}-{w}.webp", quality=80)
        sizes.append(w)
    IMG[key] = {"w": im.width if im.width <= 1600 else 1600, "h": round(im.height * min(1600, im.width) / im.width), "sizes": sorted(set(sizes))}
    return key

def pic(name, alt="", cls="", sizes="100vw", eager=False, attrs=""):
    if name not in IMG and ("/" in name or "." in name): name = upload_variants(name)
    m = IMG.get(name) or IMG["cour-automne"]; ss = sorted(m["sizes"])
    w, h = m["w"], m["h"]
    fb = ss[-1] if ss[-1] <= 1600 else ss[0]
    webp = ", ".join(f"img/{name}-{s}.webp {s}w" for s in ss)
    jpg = ", ".join(f"img/{name}-{s}.jpg {s}w" for s in ss)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<picture class="{cls}" {attrs}><source type="image/webp" srcset="{webp}" sizes="{sizes}">'
            f'<source type="image/jpeg" srcset="{jpg}" sizes="{sizes}">'
            f'<img src="img/{name}-{fb}.jpg" alt="{esc(alt)}" width="{w}" height="{h}" {load}></picture>')

def btn(text, href, cls="", ext=False):
    t = ' target="_blank" rel="noopener noreferrer"' if ext else ""
    return f'<a class="btn {cls}" href="{href}"{t}>{text} <span aria-hidden="true">↗</span></a>'

def ext(text, url):
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{text} <span aria-hidden="true">↗</span><span class="sr-only"> (nouvel onglet)</span></a>'

def tbv(label="À valider"):
    # Site publié : plus aucune mention « à valider » affichée
    if PUBLIE: return ""
    return f'<span class="tbv">{label}</span>'

EDIT = {"Actualités": "actualites", "À la une": "actualites", "Les plus récentes": "actualites", "Agenda": "agenda_app", "Réforme en cours": "options_site",
        "Les événements": "agenda", "Dans les médias": "presse", "En vidéo": "videos", "Vidéos de la chaîne": "videos",
        "Retrouvez les autres vidéos": "videos", "Bibliothèque": "documents", "Pourquoi choisir SFX1 ?": "pourquoi",
        "Idées reçues": "idees_recues", "Organisation du parcours": "immersion_v2", "Les langues à SFX1": "immersion_v2",
        "Les atouts de l’immersion": "immersion_v2", "Sélectionner une grille": "tronc_commun", "Notre histoire": "histoire_courte",
        "Moments clés": "moments", "Ils sont passés par SFX1": "anciens_celebres", "Notre équipe": "equipe",
        "Infos pratiques": "fondamental", "Une journée chez les petits": "fondamental", "Une journée en primaire": "fondamental",
        "Nos projets": "fondamental", "Nos coordonnées": "formulaire", "Notre pédagogie": "pedagogie", "S’inscrire": "portes_ouvertes", "Se renseigner": "portes_ouvertes",
        "L’excellence à SFX1": "dispositifs"}

def section(eyebrow, content, cls="", sid=""):
    i = f' id="{sid}"' if sid else ""
    if eyebrow in EDIT: i += f' data-edit="{EDIT[eyebrow]}"'
    return f'<section class="section {cls}"{i}><div class="wrap"><p class="eyebrow">{eyebrow}</p>{content}</div></section>'

def page_hero(eyebrow, h1, lead, crumbs=None):
    cr = ""
    if crumbs:
        cr = '<nav class="crumbs" aria-label="Fil d’Ariane"><a href="index.html">Accueil</a>' + "".join(
            f'<span aria-hidden="true">/</span>{"<a href=" + chr(34) + h + chr(34) + ">" + t + "</a>" if h else t}' for t, h in crumbs) + "</nav>"
    return f'<section class="page-hero"><div class="wrap">{cr}<p class="eyebrow">{eyebrow}</p><h1>{h1}</h1><p class="lead">{lead}</p></div></section>'

def card(photo, tag, heading, desc, href):
    return (f'<a class="feature scroll-reveal" href="{href}">{pic(photo, "", sizes="(max-width:650px) 100vw, 420px")}'
            f'<div class="inner"><span class="pill">{tag}</span><h3>{heading}</h3><p>{desc}</p><span class="more">Découvrir ↗</span></div></a>')

def news_card(n):
    ex = tbv("Exemple") if n.get("exemple") else ""
    dt = f'<time class="news-date">{esc(n["date"])}</time>' if n.get("date") else ""
    lk = (f'<a class="news-link" href="{n["url"]}" target="_blank" rel="noopener noreferrer">Voir sur Facebook ↗<span class="sr-only"> (nouvel onglet)</span></a>' if n.get("url") else "")
    return (f'<article class="news-card scroll-reveal" data-cat="{esc(n["tag"])}"><div class="news-pic">{pic(n["image"], "", sizes="(max-width:650px) 100vw, 420px")}{"<span class=illus>Photo d’illustration</span>" if n.get("url") else ""}</div>'
            f'<div class="inner"><div class="meta"><span class="pill">{esc(n["tag"])}</span>{dt}{ex}</div><h3>{esc(n["titre"])}</h3><p>{esc(n["resume"])}</p>{lk}</div></article>')

def myths(title=True):
    cards = "".join(
        f'<div class="myth scroll-reveal"><button type="button" class="myth-in" aria-expanded="false" aria-controls="myth-{i}">'
        f'<span class="myth-front"><span class="myth-ico" aria-hidden="true">{m["ico"]}</span><span class="myth-tag">Idée reçue ?</span><b>{esc(m["q"])}</b><span class="myth-hint">Découvrir la réalité ↻</span></span>'
        f'<span class="myth-back" id="myth-{i}"><span class="myth-tag ok">La réalité</span><span>{esc(m["r"])}</span></span></button></div>'
        for i, m in enumerate(C["idees_recues"]))
    head = '<div class="section-header"><div><h2>Idées reçues ?<br><span class="gradient-text">Démêlons le vrai du faux.</span></h2><p class="lead">Les questions que l’on nous pose le plus souvent. Cliquez sur une carte pour la retourner.</p></div></div>' if title else ""
    return head + f'<div class="myths">{cards}</div>'

def pedagogie_html():
    P = C["pedagogie"]
    c4 = "".join(f'<article class="c4 scroll-reveal"><span class="c4-ico" aria-hidden="true">{esc(c["icone"])}</span><h3>{esc(c["lettre"])}</h3><p>{esc(c["texte"])}</p><p class="c4-sfx"><b>À SFX1</b>{esc(c["a_sfx1"])}</p></article>' for c in P["quatre_c"])
    n = len(P["cycle"])
    steps = "".join(f'<li class="cy-step" style="--i:{i};--n:{n}"><span class="cy-dot">{i + 1}</span><b>{esc(s["etape"])}</b><span>{esc(s["texte"])}</span></li>' for i, s in enumerate(P["cycle"]))
    theme = P.get("theme_annee", "")
    mots = "".join(
        f'<div class="myth mot scroll-reveal{" is-theme" if theme and m["mot"].lower() == theme.lower() else ""}"><button type="button" class="myth-in" aria-expanded="false" aria-controls="mot-{i}">'
        f'<span class="myth-front"><span class="myth-ico" aria-hidden="true">{m["icone"]}</span>{"<span class=myth-tag>Thème de l’année</span>" if theme and m["mot"].lower() == theme.lower() else ""}<b>{esc(m["mot"])}</b><span class="myth-hint">Retourner ↻</span></span>'
        f'<span class="myth-back" id="mot-{i}"><span class="myth-tag ok">{esc(m["mot"])}</span><span>{esc(m["texte"])}</span></span></button></div>' for i, m in enumerate(P["mots"]))
    return (f'<div class="section-header"><div><h2>Une pédagogie jésuite,<br><span class="gradient-text">vivante au quotidien.</span></h2><p class="lead">Former des femmes et des hommes pour et avec les autres : compétents, conscients, attentifs aux autres et engagés.</p></div></div>'
            f'<h3 class="ped-h">Les 4C, notre boussole</h3><div class="c4-grid">{c4}</div>'
            f'<div class="ped-split"><div><h3 class="ped-h">Apprendre, à la manière d’Ignace</h3><p class="lead-sm">Chaque apprentissage suit un même mouvement, de la découverte à la relecture.</p><ol class="cycle" aria-label="Le cycle d’apprentissage ignatien">{steps}</ol></div>'
            f'<figure class="ped-photo scroll-reveal">{pic("sfx-ecran", "Élèves attentifs pendant un cours", sizes="(max-width:800px) 90vw, 420px")}</figure></div>'
            f'<h3 class="ped-h">Six thèmes, un par année</h3><p class="lead-sm">Chaque année, toute l’école vit un thème de la pédagogie ignatienne. Cliquez sur une carte pour la retourner.</p><div class="myths mots">{mots}</div>'
            f'<div class="ped-quote scroll-reveal"><div class="ped-quote-photo">{pic("sfx-accompagnement", "Un enseignant accompagne un élève dans son travail", sizes="(max-width:800px) 100vw, 520px")}</div>'
            f'<div><p class="eyebrow">Non multa, sed multum</p><h3>L’excellence n’est pas une compétition.</h3><p>« Peu de choses, mais en profondeur » : à SFX1, l’exigence est une forme d’attention. Elle dit à chaque élève que nous croyons en lui. Chacun est encouragé à donner le meilleur de lui-même, à son rythme, avec un accompagnement adapté : aider celui qui peine, proposer plus de défis à celui qui avance vite.</p>'
            f'{btn("Nos dispositifs d’accompagnement", "secondaire.html", "outline")}</div></div>'
            f'<p class="media-note">{esc(P["source"])}</p>')

def partners_html(style="A"):
    P = C.get("partenaires", [])
    def mark(p):
        if p.get("logo"):
            k = p["logo"]; k = upload_variants(k) if ("/" in k or "." in k) and k not in IMG else k
            return f'<img src="img/{k}-{sorted(IMG[k]["sizes"])[0]}.jpg" alt="" loading="lazy">'
        return f'<span class="pt-mono" aria-hidden="true">{esc(p["sigle"])}</span>'
    if style == "A":
        cards = "".join(f'<a class="pt-card" href="{p["url"]}" target="_blank" rel="noopener noreferrer">{mark(p)}<span class="pt-txt"><b>{esc(p["nom"])}</b><small>{esc(p["texte"])}</small></span><i aria-hidden="true">↗</i><span class="sr-only"> (nouvel onglet)</span></a>' for p in P)
        return f'<section class="pt-band" aria-label="Notre réseau"><div class="wrap"><p class="eyebrow">Notre réseau</p><h2 class="pt-h">Un collège jésuite, relié au monde.</h2><div class="pt-grid">{cards}</div></div></section>'
    pills = "".join(f'<a class="pt-pill" href="{p["url"]}" target="_blank" rel="noopener noreferrer" title="{esc(p["texte"])}">{mark(p)}<span>{esc(p["nom"])}</span><span class="sr-only"> (nouvel onglet)</span></a>' for p in P)
    return f'<div class="pt-strip" aria-label="Notre réseau"><span class="pt-lab">Membre du réseau des écoles jésuites</span><div class="pt-pills">{pills}</div></div>'

def fb_banner():
    ig = C.get("instagram", "")
    if ig:
        return (f'<div class="fb-band"><span class="fb-logo" aria-hidden="true">f</span><div><h3>Suivez la vie du Collège sur Facebook et Instagram</h3><p>Projets, sorties, réussites et informations pratiques, au fil de l’année.</p></div>'
                f'<div class="buttons" style="margin:0"><a class="btn" href="{C["facebook"]}" target="_blank" rel="noopener noreferrer">Facebook <span aria-hidden="true">↗</span></a><a class="btn outline" href="{ig}" target="_blank" rel="noopener noreferrer">Instagram <span aria-hidden="true">↗</span></a></div></div>')
    return f'<div class="fb-band"><span class="fb-logo" aria-hidden="true">f</span><div><h3>Suivez la vie du Collège sur Facebook</h3><p>Projets, sorties, réussites et informations pratiques, au fil de l’année.</p></div><a class="btn" href="{C["facebook"]}" target="_blank" rel="noopener noreferrer">@collegesfx1 <span aria-hidden="true">↗</span></a></div>'

def press_card(n):
    pay = '<span class="badge">Article payant</span>' if n.get("payant") else ""
    return (f'<a class="press-card scroll-reveal" href="{n["url"]}" target="_blank" rel="noopener noreferrer">'
            f'<div class="press-top"><span class="press-src">{esc(n["source"])}</span><span class="press-date">{esc(n["date"])}</span></div>'
            f'<h3>{esc(n["titre"])}</h3><p>{esc(n["resume"])}</p><div class="press-foot"><span class="pill">{esc(n["tag"])}</span>{pay}<span class="more">{"Voir la vidéo" if n.get("video") else "Lire l’article" if n["source"] in ("RTL info", "L'Avenir", "jesuites.com") else "Voir le reportage"} ↗<span class="sr-only"> (site externe, nouvel onglet)</span></span></div></a>')

def press_grid(items):
    return '<div class="press-grid">' + "".join(press_card(n) for n in items) + "</div>"

def event_card(e):
    return (f'<div class="event scroll-reveal"><div class="date">{esc(e["date"])}</div><div><h3>{esc(e["titre"])}</h3>'
            f'<p>{esc(e["resume"])}</p><span class="pill">{esc(e["public"])}</span></div></div>')

TYPE_LABEL = {"pdf": ("PDF", "pdf", "Ouvrir le PDF"), "pdf-ext": ("PDF en ligne", "pdf", "Consulter le PDF"),
              "drive": ("Dossier Google Drive", "drive", "Ouvrir le dossier"), "ancien": ("Ancien site", "ancien", "Consulter"), "img": ("Image", "pdf", "Ouvrir l’image")}

DOC_SVG = {
    "pdf": '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/></svg>',
    "drive": '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>',
    "ancien": '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>'}

def doc_card(d, show_cat=True):
    lab, cls, action = TYPE_LABEL[d["type"]]
    target = ' target="_blank" rel="noopener noreferrer"'
    warn = tbv() if d.get("a_valider") else ""
    note = ' <span class="sr-only">(dossier contenant un ou plusieurs documents)</span>' if d["type"] == "drive" else ""
    tm = (" " + TIMED) if d.get("timed") else ""
    return (f'<div class="doc" data-cat="{esc(d["g"])}"{tm}><span class="doc-ico doc-ico-{cls}" aria-hidden="true">{DOC_SVG.get(cls, DOC_SVG["pdf"])}</span>'
            f'<div><strong>{esc(d["n"])}</strong><div class="badges"><span class="badge {cls}">{lab}</span>'
            f'{"<span class=badge>" + esc(d["g"]) + "</span>" if show_cat else ""}{warn}</div><p>{esc(d["desc"])}</p>'
            f'<a href="{d["u"]}"{target}>{action} ↗{note}<span class="sr-only"> (nouvel onglet)</span></a></div></div>')

def video_tile(v):
    if v.get("fichier"):
        warn = tbv() if v.get("a_valider") else ""
        poster = v.get("image") or "cour-automne"
        if "/" in poster or "." in poster: poster = upload_variants(poster)
        fb = sorted(IMG[poster]["sizes"])[-1]
        return (f'<article class="video-tile scroll-reveal{" featured" if v.get("vedette") else ""}"><div class="video-stage"><video controls preload="none" playsinline poster="img/{poster}-{fb}.jpg" aria-label="{esc(v["titre"])}"><source src="{esc(v["fichier"].lstrip("/"))}" type="video/mp4">Votre navigateur ne lit pas cette vidéo.</video></div>'
                f'<div class="video-copy"><h3>{esc(v["titre"])} {warn}</h3><p>{esc(v["resume"])}</p></div></article>')
    if v.get("provider") == "drive":
        trig = f'data-drive-id="{v["id"]}"'
        direct = ext("Ouvrir dans Google Drive", "https://drive.google.com/file/d/" + v["id"] + "/view")
    else:
        trig = f'data-youtube-id="{v["id"]}"'
        direct = ext("Voir directement sur YouTube", "https://www.youtube.com/watch?v=" + v["id"])
    warn = tbv() if v.get("a_valider") else ""
    return (f'<article class="video-tile scroll-reveal{" featured" if v.get("vedette") else ""}"><div class="video-stage" data-video-stage>{pic(v["image"], "", sizes="(max-width:750px) 100vw, 620px")}'
            f'<div class="video-shade"></div><button class="video-start" type="button" {trig} data-title="{esc(v["titre"])}" aria-label="Lancer la vidéo : {esc(v["titre"])}"><span aria-hidden="true">▶</span> Regarder la vidéo</button></div>'
            f'<div class="video-copy"><h3>{esc(v["titre"])} {warn}</h3><p>{esc(v["resume"])}</p>{direct}</div></article>')

def videos_grid(page=None):
    items = [v for v in C["videos"] if page is None or page in v.get("pages", [])]
    return '<div class="video-grid">' + "".join(video_tile(v) for v in items) + "</div>"

def form_html(kind="contact"):
    F = C["formulaire"]
    if F["mode"] == "ovh":
        attrs = 'action="contact.php" method="post"'
    else:
        attrs = 'action="merci.html" method="post" data-netlify="true" netlify-honeypot="site-web"'
    opts = "".join(f"<option>{esc(s)}</option>" for s in F["sujets"])
    return (f'<form class="form" name="contact" {attrs} data-contact-form data-to="{esc(F["destinataire"])}">'
            '<input type="hidden" name="form-name" value="contact">'
            '<p class="hp" aria-hidden="true"><label>Ne pas remplir <input name="site-web" tabindex="-1" autocomplete="off"></label></p>'
            '<label>Votre nom <input required autocomplete="name" name="nom" placeholder="Nom et prénom"></label>'
            '<label>Votre adresse email <input type="email" required autocomplete="email" name="email" placeholder="nom@exemple.be"></label>'
            f'<label>Sujet <select required name="sujet"><option value="">Choisir</option>{opts}</select></label>'
            '<label>Votre message <textarea required name="message" placeholder="Votre demande…"></textarea></label>'
            '<label style="font-weight:400"><input type="checkbox" name="consentement" value="oui" required style="width:auto;margin-right:8px">J’accepte que ces informations soient utilisées uniquement pour répondre à ma demande (<a href="confidentialite.html">politique de confidentialité</a>).</label>'
            '<button type="submit" class="btn">Envoyer le message ↗</button>'
            '<p class="form-result" role="status" tabindex="-1" hidden style="color:var(--wine);font-weight:800;margin:0"></p></form>')

# ------------------------------------------------------------------ navigation
NAV = [
    ("Le Collège", "college.html", [("Notre identité", "college.html", "Valeurs, 4C, projet, équipe"), ("Notre histoire", "histoire.html", "170 ans au cœur de Verviers")] + ([("Vidéos", "videos.html", "SFX1 en images")] if SHOW_VID else [])),
    ("Secondaire", "secondaire.html", [("Les trois degrés", "secondaire.html", "De la S1 à la 6e"), ("Grilles & options", "grilles.html", "Tronc commun S1–S3 et options")]),
    ("Fondamental", "fondamental.html", [("Présentation", "fondamental.html", "L’école fondamentale"), ("Maternelle", "maternelle.html", "Les premières découvertes"), ("Primaire", "primaire.html", "Apprendre et vivre ensemble")]),
    ("Immersion NL", "immersion.html", None),
    ("Portes ouvertes", "portes-ouvertes.html", "TIMED"),
    ("Vie à SFX1", "actualites.html", [("Actualités", "actualites.html", "Projets et activités"), ("Agenda", "agenda.html", "Les prochains rendez-vous")] + ([("Vidéos", "videos.html", "Nos vidéos")] if SHOW_VID else [])),
    ("Documents", "documents.html", None),
    ("Contact", "contact.html", None),
]

def nav_html(current):
    out = []
    for label, href, sub in NAV:
        timed = sub == "TIMED"
        if timed: sub = None
        hrefs = [href] + [x[1] for x in (sub or [])]
        is_sec = current in hrefs
        cur = ' aria-current="page"' if current == href else ""
        caret = ' <span class="caret" aria-hidden="true">▾</span>' if sub else ""
        sm = ""
        if sub:
            items = []
            for t, h, d in sub:
                ext_ = h.startswith("http")
                attrs = ' target="_blank" rel="noopener noreferrer" class="sub-ext"' if ext_ else (' aria-current="page"' if h == current else "")
                items.append(f'<a href="{h}"{attrs}>{t}<small>{d}</small></a>')
            sm = '<div class="submenu">' + "".join(items) + "</div>"
        cls = "nav-item" + (" is-section" if is_sec else "") + (" nav-po" if timed else "")
        out.append(f'<div class="{cls}"{" " + TIMED if timed else ""}><a href="{href}"{cur}>{label}{caret}</a>{sm}</div>')
    out.append(f'<div class="nav-item mobile-only"><a href="fondamental.html">École fondamentale</a></div>')
    out.append(f'<div class="nav-item mobile-only"><a href="{PORTAIL}" target="_blank" rel="noopener noreferrer">Mon espace ↗</a></div>')
    return "".join(out)

DEMO_NOTICE = '<div class="demo-notice" role="note">V5 · VERSION DE TEST · Formulaire actif une fois le site en ligne · Photos à autoriser avant publication publique · Les mentions <span class="tbv" style="font-size:9px">À valider</span> signalent les contenus provisoires <button type="button" data-dismiss aria-label="Masquer cet avertissement">×</button></div>'

LD_JSON = json.dumps({"@context": "https://schema.org", "@type": "School", "name": "Collège Saint-François-Xavier I (SFX1)",
    "alternateName": ["SFX1", "SFXun", "Collège SFX1 Verviers", "Centre Scolaire Saint-François-Xavier"],
    "url": "https://sfx1.org/", "logo": "https://sfx1.org/img/logo-sfxun.jpg", "telephone": "+32 87 39 39 39", "email": "info@sfx1.org",
    "address": {"@type": "PostalAddress", "streetAddress": "Rue de Rome 18", "postalCode": "4800", "addressLocality": "Verviers", "addressCountry": "BE"},
    "sameAs": ["https://www.facebook.com/collegesfx1", "https://www.instagram.com/collegesfx1/"]}, ensure_ascii=False)

def layout(fname, title, desc, body, current=None):
    current = current or fname
    canonical = SITE_URL + "/" + ("" if fname == "index.html" else fname)
    return f'''<!doctype html>
<html lang="fr-BE">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; media-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'inline-speculation-rules'; font-src 'self'; frame-src https://www.youtube-nocookie.com https://www.openstreetmap.org https://drive.google.com{AGENDA_ORIGIN}; connect-src 'self'; base-uri 'self'; form-action 'self'">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{"" if PUBLIE else '<meta name="robots" content="noindex, nofollow">'}
<meta name="theme-color" content="#98052b">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_BE">
<meta property="og:site_name" content="SFXun — Centre Scolaire Saint-François-Xavier">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE_URL}/img/cour-automne-1600.jpg">
<link rel="icon" href="favicon.png" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="stylesheet" href="css/base.css">
<link rel="stylesheet" href="css/v5.css">
{f'<script type="application/ld+json">{LD_JSON}</script>' if fname == "index.html" else ""}
<script type="speculationrules">{{"prerender":[{{"where":{{"href_matches":"/*"}},"eagerness":"moderate"}}]}}</script>
</head>
<body>
{"" if PUBLIE else DEMO_NOTICE}
<div class="progress" id="progress" aria-hidden="true"></div>
<a class="skip-link" href="#main">Aller au contenu</a>
<header class="topbar">
<a href="index.html" class="brand" aria-label="SFXun — retour à l’accueil"><img src="img/logo-sfxun.jpg" alt="Logo SFXun – Centre Scolaire Saint-François-Xavier" width="729" height="374"></a>
<nav class="nav" id="mainnav" aria-label="Navigation principale">{nav_html(current)}</nav>
<a class="portal" href="{PORTAIL}" target="_blank" rel="noopener noreferrer" title="Portail réservé aux enseignants (compte @sfx1.org)">Mon espace <span aria-hidden="true">↗</span><span class="sr-only"> (nouvel onglet, accès réservé aux enseignants)</span></a>
<button class="menu-btn" id="menuBtn" type="button" aria-expanded="false" aria-controls="mainnav" aria-label="Ouvrir le menu">☰</button>
</header>
<main id="main" tabindex="-1">
{body}
</main>
<button id="backTop" class="back-top" type="button" aria-label="Retour en haut">↑</button>
<nav class="mbar" aria-label="Accès rapides"{" hidden" if fname == "contact.html" else ""}>
<a href="tel:+3287393939"><span aria-hidden="true">☎</span>Appeler</a>
<a href="portes-ouvertes.html" class="mbar-po" {TIMED}><span aria-hidden="true">★</span>30 janvier</a>
<a href="fondamental.html"><span aria-hidden="true">✳</span>Fondamental</a>
<a href="https://www.google.com/maps/search/?api=1&amp;query=Rue+de+Rome+18+4800+Verviers" target="_blank" rel="noopener noreferrer"><span aria-hidden="true">➜</span>Itinéraire</a>
</nav>
{partners_html("A")}
<footer>
<div class="footer-inner">
<div><img src="img/logo-sfxun.jpg" alt="SFXun" class="footer-logo" width="729" height="374" loading="lazy"><p>Se situer aujourd’hui pour construire demain.</p></div>
<div><b>Découvrir</b><a href="college.html">Notre Collège</a><a href="histoire.html">Notre histoire</a><a href="secondaire.html">Secondaire</a><a href="fondamental.html">Fondamental</a><a href="immersion.html">Immersion NL</a>{"<a href=videos.html>Vidéos</a>" if SHOW_VID else ""}</div>
<div><b>Pratique</b><a href="portes-ouvertes.html" {TIMED}>Portes ouvertes</a><a href="fondamental.html">École fondamentale</a><a href="grilles.html">Grilles & options</a><a href="documents.html">Documents</a><a href="agenda.html">Agenda</a><a href="contact.html">Contact</a></div>
<div><b>Nous trouver</b><p>Rue de Rome 18<br>4800 Verviers, Belgique</p><span class="social"><a href="{C["facebook"]}" target="_blank" rel="noopener noreferrer" aria-label="Facebook du Collège (nouvel onglet)">f</a>{f'<a href="{C["instagram"]}" target="_blank" rel="noopener noreferrer" aria-label="Instagram du Collège (nouvel onglet)">◎</a>' if C.get("instagram") else ""}{f'<a href="{YT_CHANNEL}" target="_blank" rel="noopener noreferrer" aria-label="Chaîne YouTube du Collège (nouvel onglet)">▶</a>' if SHOW_VID else ""}</span><a href="tel:+3287393939">087 39 39 39</a><a href="mailto:info@sfx1.org">info@sfx1.org</a></div>
</div>
<div class="footer-bottom">© 2026 SFXun · Centre Scolaire Saint-François-Xavier I{"" if PUBLIE else " · Version de test " + VERSION}
<div class="footer-legal"><a href="mentions-legales.html">Mentions légales</a><a href="confidentialite.html">Confidentialité</a><a href="espace.html">Espace numérique</a></div></div>
</footer>
<script src="js/site.js" defer></script>
</body>
</html>'''

PAGES = {}
def page(fname, title, desc, current=None):
    def deco(fn):
        PAGES[fname] = (title, desc, fn, current)
        return fn
    return deco

VALUES = [("◎", "Conscience", "Réfléchir, se connaître et poser des choix éclairés."), ("♡", "Compassion", "Grandir dans l’attention aux autres et la solidarité."),
          ("↗", "Engagement", "Agir avec et pour les autres."), ("✦", "Compétence", "Développer ses talents et ses connaissances.")]

def values_html(items, lift=True):
    return '<div class="values">' + "".join(
        f'<div class="value scroll-reveal{" value-lift" if lift else ""}"><span class="big" aria-hidden="true">{i}</span><b>{t}</b><p>{d}</p></div>' for i, t, d in items) + "</div>"

def journey():
    tabs, panels = [], []
    for i, d in enumerate(G["degres"]):
        tabs.append(f'<button type="button" role="tab" id="jt-{d["id"]}" aria-controls="jp-{d["id"]}" aria-selected="{str(i == 0).lower()}" class="journey-tab{" active" if i == 0 else ""}" data-key="{d["id"]}"><small>0{i+1}</small>{d["nom"]}</button>')
        panels.append(f'<div id="jp-{d["id"]}" class="journey-panel" role="tabpanel" aria-labelledby="jt-{d["id"]}" tabindex="0">'
                      f'<div class="journey-picture">{pic(d["photo"], "", sizes="(max-width:800px) 100vw, 620px")}<span class="journey-count">0{i+1} / 03</span></div>'
                      f'<div class="journey-copy"><p class="eyebrow">{"S1 et S2 · tronc commun" if d["id"] == "d1" else d["annees"]}</p><h3>{d["nom"]}</h3><p>{d["intro"]}</p>'
                      f'<div class="journey-actions">{btn("Grilles et options", "grilles.html#" + ("tc" if d["id"] == "d1" else d["id"]), "outline")}<a href="documents/{"TC-Grille-horaire-tronc-commun" if d["id"] == "d1" else d["code"] + "-Grille-horaire"}-SFX1.pdf" target="_blank" rel="noopener" class="text-link">Grille PDF ↗</a></div></div></div>')
    return f'<div class="journey-tabs" role="tablist" aria-label="Les trois degrés">{"".join(tabs)}</div>' + "".join(panels)

def creneaux_html():
    return '<div class="po-slots">' + "".join(f'<span class="po-slot"><b>{c}</b><small>Créneau {i+1}</small></span>' for i, c in enumerate(PO["creneaux"])) + "</div>"

def reserve_btn(cls="light"):
    """Bouton « Je réserve mon créneau de visite » : actif quand la réservation est ouverte et le lien fourni (administration)."""
    if PO.get("reservation_ouverte") and PO.get("inscription_url"):
        return btn("Je réserve mon créneau de visite", PO["inscription_url"], cls, True)
    return '<span class="btn reserve-soon" aria-disabled="true">Je réserve mon créneau de visite <small>· ouverture prochaine</small></span>'

def po_cta():
    if PO.get("inscription_url") and PO.get("reservation_ouverte"):
        return btn("Réserver mon créneau", PO["inscription_url"], "light", True)
    return btn("Toutes les infos", "portes-ouvertes.html", "light")

def po_banner():
    return (f'<section class="po-band" {TIMED} aria-label="Portes ouvertes"><div class="wrap po-band-in">'
            f'<div class="po-poster scroll-reveal">{pic("affiche-po-2027", "Affiche des portes ouvertes du samedi 30 janvier 2027", sizes="(max-width:800px) 80vw, 380px")}</div>'
            f'<div class="po-copy"><p class="eyebrow">Bien plus qu’une école !</p><h2>Portes ouvertes<br><span>{PO["date_txt"]}</span></h2>'
            f'<p class="lead">Venez découvrir le Collège, rencontrer les équipes et poser toutes vos questions. Quatre créneaux de visite :</p>{creneaux_html()}'
            f'<div class="countdown" data-countdown="{PO["date_iso"]}" aria-live="off"></div>'
            f'<div class="buttons">{reserve_btn()}{btn("Toutes les infos", "portes-ouvertes.html", "ghost")}{btn("Télécharger l’affiche", "documents/portes-ouvertes/Affiche-Portes-ouvertes-2027-A4.pdf", "ghost", True)}</div></div></div></section>')

def fond_banner(cls=""):
    return (f'<section class="fond-band {cls}"><div class="wrap fond-in"><div class="fond-ico" aria-hidden="true">✳</div><div><p class="eyebrow">Maternelle &amp; primaire</p>'
            f'<h2>Vous cherchez l’école fondamentale ?</h2><p>Une école verte au cœur de Verviers, de la maternelle à la 6e primaire : horaires, projets et contacts.</p></div>'
            f'<a class="btn fond-btn" href="fondamental.html">Découvrir l’école fondamentale <span aria-hidden="true">→</span></a></div></section>')

# ------------------------------------------------------------------ pages
@page("index.html", "Collège SFX1 Verviers — Centre Scolaire Saint-François-Xavier I (SFXun)",
      "Collège Saint-François-Xavier I à Verviers : enseignement secondaire et fondamental, immersion en néerlandais, options et vie scolaire.")
def p_index():
    slides = [("cour-automne", "La cour, au cœur de la vie du Collège"), ("sfx-cercle", "Prendre le temps d’échanger"),
              ("sfx-classe", "Apprendre ensemble, chacun à son rythme"), ("sfx-gym", "Bouger, coopérer, se dépasser")]
    sl = "".join(pic(n, "", f'hero-slide{" active" if i == 0 else ""}', eager=(i == 0), attrs=f'data-caption="{c}"') for i, (n, c) in enumerate(slides))
    dots = "".join(f'<button class="slide-dot{" active" if i == 0 else ""}" type="button" data-slide="{i}" aria-label="Photo {i+1} : {c}"></button>' for i, (n, c) in enumerate(slides))
    quick = "".join(f'<a class="quick-item micro-rise" href="{h}"{' target="_blank" rel="noopener noreferrer"' if h.startswith("http") else ""}><span class="ico" aria-hidden="true">{a}</span><strong>{t}</strong><span aria-hidden="true">↗</span></a>'
                    for a, t, h in [("◈", "Nos enseignements", "secondaire.html"), ("▧", "Immersion NL", "immersion.html"), ("✳", "École fondamentale", FOND), ("▤", "Grilles & options", "grilles.html")])
    news = "".join(news_card(n) for n in C["actualites"][:3])
    return f'''
<section class="hero" aria-label="Bienvenue au Collège">
<div class="hero-slides" aria-hidden="true">{sl}</div>
<div class="hero-photo-caption" aria-live="off">{slides[0][1]}</div>
<div class="wrap">
<a class="hero-kicker" href="portes-ouvertes.html" {TIMED}><i aria-hidden="true"></i>Portes ouvertes · {PO["date_txt"]}</a>
<p class="eyebrow">Bien plus qu’une école · Verviers</p>
<h1>Se situer aujourd’hui<br>pour construire <em>demain.</em></h1>
<p class="intro">Une école qui cultive les talents, accompagne chaque jeune et ouvre des horizons, de la maternelle à la rhéto.</p>
<div class="buttons"><a class="btn light" href="portes-ouvertes.html" {TIMED}>Visitez-nous le 30 janvier <span aria-hidden="true">↗</span></a>{btn("Découvrir le secondaire", "secondaire.html", "ghost")}<a class="btn ghost" href="fondamental.html">École fondamentale <span aria-hidden="true">→</span></a></div>
<div class="hero-bottom"><a href="#decouvrir" class="hero-indicator">Explorer SFX1</a>
<div class="hero-slide-tools" role="group" aria-label="Diaporama de photographies"><button type="button" class="slider-arrow" data-slide-prev aria-label="Photo précédente">←</button><div class="slide-dots">{dots}</div><button type="button" class="slider-arrow" data-slide-next aria-label="Photo suivante">→</button><button type="button" class="slider-pause" data-slide-pause aria-label="Mettre le diaporama en pause">Ⅱ</button></div></div>
</div><div class="hero-progress" aria-hidden="true"></div></section>
<div class="wrap" id="decouvrir"><div class="quick-nav">{quick}</div></div>
{po_banner()}
{section("Pourquoi choisir SFX1 ?", f'<div class="section-header"><div><h2>Bien plus qu’une école.<br><span class="gradient-text">Six bonnes raisons de nous rejoindre.</span></h2></div>{btn("Notre Collège", "college.html", "outline")}</div><div class="why">{"".join(f'<div class="why-card scroll-reveal"><span class="why-ico" aria-hidden="true">{i}</span><h3>{esc(t)}</h3><p>{esc(x)}</p></div>' for i, t, x in C["pourquoi"])}</div><div class="keyfigs"><div class="keyfig scroll-reveal"><b data-count="170">170</b><span>ans d’histoire au cœur de Verviers</span></div><div class="keyfig scroll-reveal"><b data-count="8">8</b><span>dispositifs d’accompagnement</span></div><div class="keyfig scroll-reveal"><b data-count="11" data-suffix="h">11h</b><span>jusqu’à 11 h de cours en immersion par semaine</span></div><div class="keyfig scroll-reveal"><b>B2</b><span>certificat KU Leuven en immersion</span></div></div>')}
{section("Idées reçues", myths(), "soft")}
{section("Choisir son parcours", f'<div class="journey-head"><h2>De la S1 à la rhéto,<br><span class="gradient-text">chaque étape ouvre des perspectives.</span></h2></div>' + journey())}
{section("En vidéo", f'<div class="section-header"><div><h2>SFX1 en images.</h2></div>{btn("Toutes les vidéos", "videos.html", "outline")}</div><div class="video-grid">{video_tile(C["videos"][0])}</div>', "soft") if SHOW_VID else ""}
{section("Actualités", f'<div class="section-header"><div><h2>Une école qui bouge.</h2><p class="lead">Les derniers moments forts, publiés sur notre page Facebook.</p></div>{btn("Toutes les actualités", "actualites.html", "outline")}</div><div class="cards">{news}</div>')}
{fond_banner()}
{section("Nous rencontrer", f'<div class="banner"><div><h2>Et si la prochaine étape<br>commençait ici ?</h2><p>Visitez le Collège, rencontrez nos équipes, posez vos questions.</p></div><div class="buttons" style="margin:0"><a class="btn light" href="portes-ouvertes.html" {TIMED}>Portes ouvertes · 30 janvier <span aria-hidden="true">↗</span></a>{btn("Nous contacter", "contact.html", "ghost")}</div></div>')}'''

@page("college.html", "Le Collège · Collège SFX1 Verviers", "Histoire, valeurs ignaciennes, les 4C, projet éducatif et cadre de vie du Collège Saint-François-Xavier I.")
def p_college():
    docs = [d for d in C["documents"] if d["g"] in ("Institutionnels", "Règlements") and d["type"] != "ancien"]
    gal = [("sfx-entree", "L’entrée du Collège, rue de Rome"), ("sfx-couloir", "Les couloirs des classes"), ("sfx-cercle", "Un espace pour échanger"), ("sfx-gym", "La salle de sport")]
    galhtml = "".join(f'<figure class="scroll-reveal">{pic(n, c, sizes="(max-width:760px) 100vw, 600px")}<figcaption>{c}</figcaption></figure>' for n, c in gal)
    return page_hero("Notre identité", "Un Collège, une ambition : <em>faire grandir chacun.</em>",
                     "Situé au cœur de Verviers, le Centre scolaire Saint-François-Xavier I s’inscrit depuis 1855 dans la tradition éducative jésuite.", [("Le Collège", None)]) + \
        section("L’établissement", f'<div class="split"><div class="photo-frame">{pic("sfx-classe", "Élèves au travail en classe au Collège", sizes="(max-width:650px) 100vw, 600px")}</div><div><h2>Une école ancrée dans la ville.</h2><p class="lead">Rue de Rome, à proximité du centre et de la gare, le Collège réunit les apprentissages, la vie collective et un cadre de verdure. Le choix du centre-ville peut susciter des interrogations : il constitue pourtant une véritable richesse, au service de la réussite et de l’épanouissement des élèves.</p><div class="stack">{"".join(f'<div class="link-card" style="display:block"><b>{esc(t)}</b><p class="media-note" style="margin:6px 0 0">{esc(x)}</p></div>' for t, x in C["ville"])}</div></div></div>') + \
        section("Notre histoire", f'<div class="section-header"><div><h2>170 ans au service des jeunes.</h2><p class="lead">Quelques repères. Toute l’histoire en un coup d’œil sur la page dédiée.</p></div>{btn("Toute notre histoire", "histoire.html", "outline")}</div><div class="mini-tl">{"".join(f'<div class="mt scroll-reveal"><b>{y}</b><span>{esc(t)}</span></div>' for y, t in C["histoire_courte"])}</div>', "soft") + \
        section("Notre projet éducatif", f'<div class="split"><div><h2>Des hommes et des femmes pour les autres et avec les autres.</h2><p class="lead">Notre projet éducatif vise à former « des hommes et des femmes pour les autres et avec les autres ». L’éducation jésuite est une invitation à développer l’excellence humaine et à porter attention à chaque personne, dans toutes ses dimensions : intellectuelle, corporelle, psycho-affective, sociale et spirituelle.</p></div><div class="eng-grid">{"".join(f'<div class="eng scroll-reveal"><h3>{esc(t)}</h3><p>{esc(x)}</p></div>' for t, x in C["engagements"])}</div></div>') + \
        section("Notre pédagogie", pedagogie_html()) + \
        (section("En vidéo", f'<h2>Mener chacun à sa propre excellence.</h2>{videos_grid("college")}') if SHOW_VID else "") + \
        section("Cadre de vie", f'<div class="section-header"><h2>Un cadre pour apprendre et grandir.</h2></div><div class="gallery">{galhtml}</div>', "soft") + \
        section("Notre équipe", f'<h2>Une école, ce sont d’abord des personnes.</h2><p class="lead">Élèves et parents, enseignants, titulaires, éducateurs de niveau, secrétaires de direction, économe, ouvriers et dames d’ouvrage font vivre le Collège au quotidien.</p><div class="team">{"".join(f'<div class="team-card scroll-reveal"><span>{esc(r)}</span><b>{esc(n)}</b>{f"<a class=team-tel href=tel:+32{tel.replace(chr(32), str())[1:]}>Ligne directe : {esc(tel)}</a>" if tel else ""}</div>' for r, n, tel in C["equipe"])}</div>') + \
        section("Textes de référence", f'<h2>Notre projet, en détail.</h2><p class="lead-sm">Les documents restent hébergés à leur emplacement d’origine. Les liens Google Drive ouvrent des <strong>dossiers</strong>.</p><div class="doc-grid">{"".join(doc_card(d, False) for d in docs)}</div>')

@page("histoire.html", "Notre histoire · Collège SFX1 Verviers", "L’histoire du Collège Saint-François-Xavier I de Verviers en quelques moments clés, de 1855 à aujourd’hui.")
def p_histoire():
    mom = "".join(f'<article class="mom scroll-reveal"><figure>{pic(m["img"], m["cap"], sizes="(max-width:800px) 85vw, 380px")}<figcaption>{esc(m["cap"])}</figcaption></figure><div><b class="mom-y">{esc(m["y"])}</b><h3>{esc(m["t"])}</h3><p>{esc(m["r"])}</p></div></article>' for m in C["moments"])
    anc = "".join(f'<span class="anc"><b>{esc(n)}</b>{esc(r)}</span>' for n, r in C["anciens_celebres"])
    return page_hero("Le Collège · 1855-2025", "170 ans <em>au cœur de Verviers.</em>", "Une histoire jésuite, tournée vers l’avenir depuis sa première rentrée, le 30 octobre 1855.", [("Le Collège", "college.html"), ("Notre histoire", None)]) + \
        section("Moments clés", f'<div class="section-header"><div><h2>Cinq moments qui nous ont façonnés.</h2><p class="lead">Faites défiler pour remonter le temps.</p></div></div><div class="moments" tabindex="0" role="region" aria-label="Moments clés, défilement horizontal">{mom}</div>') + \
        section("Ils sont passés par SFX1", f'<h2>Des anciens qui ont marqué leur époque.</h2><div class="ancs">{anc}</div><p class="media-note">D’après le livre « Un Collège, une tradition jésuite. 1855-2005 », publié pour les 150 ans du Collège. Illustrations tirées du même ouvrage.</p>', "soft") + \
        section("Et demain ?", f'<div class="banner"><div><h2>La suite s’écrit avec vous.</h2><p>Venez découvrir le Collège d’aujourd’hui.</p></div><div class="buttons" style="margin:0"><a class="btn light" href="portes-ouvertes.html" {TIMED}>Portes ouvertes <span aria-hidden="true">↗</span></a>{btn("Le Collège aujourd’hui", "college.html", "ghost")}</div></div>')

@page("secondaire.html", "Enseignement secondaire · Collège SFX1 Verviers", "Le secondaire au Collège SFX1 : trois degrés, options, langues et immersion en néerlandais.")
def p_secondaire():
    deg = "".join(f'<div class="degree scroll-reveal"><span>{"S1 et S2" if d["id"] == "d1" else d["annees"]}</span><h3>{d["nom"]}</h3><p>{d["intro"]}</p>{btn("Grilles et options", "grilles.html#" + ("tc" if d["id"] == "d1" else d["id"]), "outline")}</div>' for d in G["degres"])
    return page_hero("Nos enseignements", "Secondaire : six années pour explorer et se construire.", "Trois degrés, des langues, des options et une attention particulière au cheminement de chaque élève.", [("Secondaire", None)]) + \
        section("Parcours interactif", f'<h2>Trois degrés, un chemin.</h2>' + journey()) + \
        section("Trois degrés", f'<div class="degree-grid">{deg}</div>', "soft") + \
        section("Réforme en cours", f'<h2>La réforme, année après année.</h2><p class="lead">Le tronc commun remplace progressivement les trois premières années. Les grilles de la 4e, de la 5e et de la 6e ne changent pas.</p><div class="sys">{"".join(f'<div class="sys-row scroll-reveal"><b class="sys-y">{y}</b><div class="sys-c"><span class="sys-l">Tronc commun</span>{"".join(f"<span class=sys-new>{x}</span>" for x in n)}</div><div class="sys-c"><span class="sys-l">Ancien 1er/2e degré</span>{"".join(f"<span class=sys-old>{x}</span>" for x in a) or "<span class=sys-none>—</span>"}</div><div class="sys-c"><span class="sys-l">Grilles inchangées</span>{"".join(f"<span class=sys-keep>{x}</span>" for x in k)}</div></div>' for y, n, a, k in C["systemes"])}</div><p class="media-note">Les élèves déjà inscrits poursuivent leur parcours avec la grille qu’ils ont commencée.</p>') + \
        section("Des possibilités pour chacun", f'<div class="cards">{card("sfx-accompagnement", "Méthodologie", "Apprendre à apprendre", "Des approches pédagogiques variées et l’attention à la progression de chacun.", "college.html")}{card("sfx-microscope", "Parcours", "Langues et options", "Des options littéraires, scientifiques, artistiques, économiques et linguistiques.", "grilles.html")}{card("immersion-mobiliteit", "Langues", "Immersion en néerlandais", "Un parcours qui donne une place concrète à l’apprentissage en langue cible.", "immersion.html")}</div>') + \
        section("L’excellence à SFX1", f'<div class="split" style="align-items:start"><div><h2>Un chemin accompagné.</h2><p class="lead">À SFX1, l’excellence consiste à permettre à chaque élève de devenir la meilleure version de lui-même, en tenant compte de son rythme, de ses forces et de ses besoins. Rigueur, sérieux et travail en sont les fondements, associés à un accompagnement humain et personnalisé.</p><blockquote class="conviction">L’excellence n’est pas un résultat, c’est un chemin.</blockquote></div><div><h3 style="margin-top:0">Une transition accompagnée et bienveillante</h3><p>Une attention particulière est portée au passage du fondamental au secondaire, même lorsqu’il implique un changement de langue. Les équipes instaurent un climat de confiance, renforcent progressivement les acquis linguistiques, travaillent les disciplines de manière transversale et permettent aux élèves de rattraper, consolider et développer leurs compétences.</p></div></div><div class="disp-grid">{"".join(f'<div class="disp scroll-reveal"><span class="n">{i+1}</span><span class="i" aria-hidden="true">{ic}</span><h3>{esc(t)}</h3><p>{esc(x)}</p></div>' for i, (t, x, ic) in enumerate(C["dispositifs"]))}</div>', "soft") + \
        (section("En vidéo", f'<h2>Un accompagnement personnalisé.</h2>{videos_grid("secondaire")}') if SHOW_VID else "") + \
        section("Après le premier degré", f'<div class="split"><div><h2>Diversifier progressivement.</h2><p class="lead">{esc(C["tronc_commun"]["apres"])}</p>{btn("Grille du tronc commun", "grilles.html#tc", "outline")}</div><div class="opt-cloud"><h3>Options actuelles</h3><p class="media-note">Susceptibles d’évoluer selon le cadre décrétal.</p><div>{"".join(f"<span>{esc(o)}</span>" for o in C["tronc_commun"]["options"])}</div><h3>Activités complémentaires</h3><div>{"".join(f"<span class=act>{esc(o)}</span>" for o in C["tronc_commun"]["activites"])}</div></div></div>', "soft") + \
        section("Informations pratiques", f'<h2>Le quotidien au Collège.</h2><div class="info-cards">{"".join(f'<div class="info-card scroll-reveal"><span class="ico" aria-hidden="true">{ic}</span><h3>{esc(t)}</h3><ul class="ticks">{"".join(f"<li>{esc(x)}</li>" for x in items)}</ul></div>' for t, items, ic in C["infos_pratiques"])}</div>') + \
        section("Les ressources", f'<div class="banner"><div><h2>Choisir ses options.</h2><p>Consulter les grilles horaires et les descriptions détaillées de chaque degré.</p></div>{btn("Voir les grilles", "grilles.html", "light")}</div>')

def grid_table(d):
    cols = d["colonnes"]
    head = "<tr><th scope=col>Formation commune obligatoire</th>" + "".join(f'<th scope="col" class="n">{c}</th>' for c in cols) + "</tr>"
    rows = ""
    for r in d["fco"]:
        lm1 = r[0].startswith("Langue moderne I ") or r[0] == "Langue moderne I"
        nl = "*" in "".join(r) or lm1
        name = r[0].replace("*", "")
        lab = f'<span class="imm">{esc(name)}</span>' if nl else esc(name)
        extra = '<small class="imm-note">néerlandais en immersion</small>' if lm1 else ""
        rows += f'<tr class="{"is-nl" if nl else ""}"><th scope="row" style="font-weight:600">{lab}{extra}{"<span class=sr-only> (cours en immersion)</span>" if nl else ""}</th>' + "".join(f'<td class="n{" imm-cell" if (lm1 or "*" in v or ("*" in r[0] and not any("*" in x for x in r[1:]))) else ""}">{esc(v.replace("*", ""))}</td>' for v in r[1:]) + "</tr>"
    foot = "<tr>" + "".join(f'<td class="{"n" if i else ""}">{esc(v)}</td>' for i, v in enumerate(d["total"])) + "</tr>"
    return f'<table class="hours"><caption class="sr-only">Grille horaire — {d["nom"]}, périodes par semaine</caption><thead>{head}</thead><tbody>{rows}</tbody><tfoot>{foot}</tfoot></table>'

def choice_blocks(d):
    out = ""
    for b in d["blocs"]:
        lines = ""
        for l in b["lignes"]:
            opts = ('<span class="or">ou</span>').join(f'<span class="{"act" if l.get("activite") else ""}">{esc(o)}</span>' for o in l["choix"])
            lines += f'<div class="choice-line"><div class="opts">{opts}</div><div class="hrs">{esc(l["h"]) + "h" if l["h"] else ""}</div></div>'
        notes = "".join(f'<p class="grid-notes">{esc(n)}</p>' for n in b["notes"])
        out += f'<div class="choice-block"><h4>{esc(b["titre"])} <span class="badge">Total : {esc(b["total"])}{"h" if b["total"].isdigit() else ""}</span></h4>{lines}{notes}</div>'
    return out

@page("grilles.html", "Grilles horaires et options · Collège SFX1 Verviers", "Grilles horaires interactives des trois degrés du secondaire, options, activités complémentaires et règles de choix.", "grilles.html")
def p_grilles():
    T = C["tronc_commun"]
    tabs = ['<button type="button" role="tab" class="grid-tab" id="gt-tc" aria-controls="gp-tc" aria-selected="true" data-key="tc">Tronc commun<small>S1 · S2 · S3</small></button>']
    IMM = {(x["cours"], a) for x in T.get("immersion", []) for a in x["annees"]}
    head = "<tr><th scope=col>Discipline</th>" + "".join(f'<th scope="col" class="n">{c}<br><span style="text-transform:none;letter-spacing:0;font-weight:600;color:var(--muted)">{st}</span></th>' for c, st in zip(T["colonnes"], T["sous_titres"])) + '</tr>'
    body = "".join(f'<tr class="grp"><th colspan="4" scope="rowgroup">{esc(g)}</th></tr>' + "".join(f'<tr><th scope="row" style="font-weight:600">{esc(r[0])}</th>' + "".join(f'<td class="n{" imm-cell" if (r[0], T["colonnes"][i]) in IMM and v not in ("–", "") else ""}">{v}</td>' for i, v in enumerate(r[1:4])) + '</tr>' for r in rows) for g, rows in T["groupes"])
    acc = ""
    foot = "<tr>" + "".join(f'<td class="{"n" if 0 < i < 4 else ("obs" if i == 4 else "")}">{v}</td>' for i, v in enumerate(T["total"][:4])) + "</tr>"
    panels = [f'''<div id="gp-tc" role="tabpanel" aria-labelledby="gt-tc" tabindex="0" class="grid-panel">
<div class="grid-layout">
<div class="table-card scroll-reveal"><h3><span>Grille horaire du tronc commun (SFX1)</span></h3><div class="table-scroll" tabindex="0" role="region" aria-label="Grille du tronc commun (défilement horizontal sur petit écran)"><table class="hours tc"><caption class="sr-only">Grille du tronc commun, périodes par semaine</caption><thead>{head}</thead><tbody>{body}</tbody><tfoot>{foot}{acc}</tfoot></table></div><p class="grid-notes"><span class="imm">Surligné en jaune</span> : cours en immersion, cours de néerlandais (langue moderne I) compris.</p><div class="buttons">{btn("Grille du tronc commun (PDF)", "documents/TC-Grille-horaire-tronc-commun-SFX1.pdf", "outline", True)}</div></div>
<div class="table-card scroll-reveal"><h3>Après le tronc commun</h3><p class="lead-sm" style="margin-top:0">{esc(T["apres"])}</p><div class="opt-cloud"><h4>Options actuelles</h4><p class="media-note">Susceptibles d’évoluer selon le cadre décrétal.</p><div>{"".join(f"<span>{esc(o)}</span>" for o in T["options"])}</div><h4>Activités complémentaires</h4><div>{"".join(f"<span class=act>{esc(o)}</span>" for o in T["activites"])}</div></div>
<p class="notice" style="margin-top:16px">S1 dès 2026-2027, S2 dès 2027-2028, S3 dès 2028-2029. Grille de référence de 32 périodes de 50 minutes. Les grilles de la 4e à la 6e restent inchangées. {tbv()} Les choix possibles en religion / morale et philosophie et citoyenneté, ainsi que les langues proposées en langue moderne II, seront précisés.</p></div>
</div></div>''']
    for i, d in enumerate(G["degres"]):
        lbl = ("Ancien 1er degré", "2e année en 2026-2027") if d["id"] == "d1" else (d["nom"], d["annees"])
        tabs.append(f'<button type="button" role="tab" class="grid-tab" id="gt-{d["id"]}" aria-controls="gp-{d["id"]}" aria-selected="false" data-key="{d["id"]}">{lbl[0]}<small>{lbl[1]}</small></button>')
        warn = f'<p class="notice" style="margin-top:14px">{tbv()} {esc(d["a_valider"])}</p>' if d.get("a_valider") else ""
        descs = "".join(f'<details><summary><span>{esc(x["t"])}</span><span class="h">{esc(x["h"])}</span></summary><p>{esc(x["r"])}</p></details>' for x in d["descriptions"])
        panels.append(f'''<div id="gp-{d["id"]}" role="tabpanel" aria-labelledby="gt-{d["id"]}" tabindex="0" class="grid-panel">
<div class="grid-layout">
<div class="table-card scroll-reveal"><h3><span>{d["nom"]} · formation commune</span></h3>{grid_table(d)}<p class="grid-notes"><span class="imm">Surligné en jaune</span> : cours en immersion, cours de néerlandais compris. {esc(d["note_immersion"].replace("* Cours en immersion", "").lstrip(". "))}</p></div>
<div class="table-card scroll-reveal"><h3>Options et activités</h3>{choice_blocks(d)}<ul class="rules">{"".join(f"<li>{esc(r)}</li>" for r in d["regles"])}</ul>{warn}</div>
</div>
<h3 style="margin:42px 0 6px">Description des options et activités</h3><p class="lead-sm">Résumés établis à partir du document officiel. Le texte complet fait foi.</p>
<div class="opt-desc">{descs}</div>
<div class="buttons">{btn("Grille horaire (PDF)", "documents/" + d["code"] + "-Grille-horaire-SFX1.pdf", "outline", True)}{btn("Description complète (PDF)", "documents/" + d["code"] + "-Description-SFX1.pdf", "outline", True)}</div><p class="media-note">Nouvelle mise en page aux couleurs SFX1, contenu identique. Versions d’origine : <a href="documents/{d["code"]}-Grille-horaire.pdf" target="_blank" rel="noopener">grille</a> · <a href="documents/{d["code"]}-Description.pdf" target="_blank" rel="noopener">description</a>.</p>
</div>''')
    return page_hero("Secondaire · Grilles horaires", "Construire son parcours.", "La grille du tronc commun (S1, S2, S3) et les options des 2e et 3e degrés, consultables directement à l’écran. Les PDF restent téléchargeables.", [("Secondaire", "secondaire.html"), ("Grilles & options", None)]) + \
        section("Sélectionner une grille", f'<p class="notice" style="margin-bottom:24px">{tbv()} Depuis 2026-2027, la 1re année devient la <b>S1</b> (tronc commun) ; en 2027-2028, la 2e année deviendra la <b>S2</b>. Les grilles des 2e et 3e degrés sont retranscrites des PDF transmis par le Collège : leur validité pour l’année en cours reste à confirmer.</p><div class="grid-tabs" role="tablist" aria-label="Choisir un degré" data-hash="1">{"".join(tabs)}</div>{"".join(panels)}')

@page("immersion.html", "Immersion en néerlandais · Collège SFX1 Verviers", "Le dispositif EMILE d’immersion en néerlandais au Collège SFX1 : organisation du parcours, cours concernés et intérêt pédagogique.")
def p_immersion():
    I = C["immersion_v2"]
    st = "".join(f'<div class="yr scroll-reveal"><span class="yr-n">{esc(a)}</span>{f"<small class=yr-s>{esc(sub)}</small>" if sub else ""}<p><span class="nl">NL</span>{esc(t)}</p><b class="yr-t">{esc(tot)}<small>en immersion</small></b></div>' for a, sub, t, tot in I["annees"])
    langs = "".join(f'<div class="info-card scroll-reveal"><h3>{esc(t)}</h3><p>{esc(x)}</p></div>' for t, x in I["langues"])
    return page_hero("Enseignements · Langues", "L’immersion en néerlandais : apprendre autrement.", "Un parcours linguistique et culturel intégré aux apprentissages du secondaire.", [("Immersion NL", None)]) + \
        section("EMILE", f'<div class="split"><div class="photo-frame">{pic("immersion-mobiliteit", "Élèves travaillant sur un dossier en néerlandais", sizes="(max-width:650px) 100vw, 600px")}<span class="photo-badge">Map I — Mobiliteit</span></div><div><h2>Apprendre en langue cible.</h2><p class="lead">Le dispositif d’immersion (EMILE : enseignement d’une matière par l’intégration d’une langue étrangère) permet aux élèves d’apprendre certaines disciplines en néerlandais et de développer progressivement leurs compétences linguistiques.</p><p>La langue n’est plus seulement une matière : elle devient un outil pour comprendre, chercher et échanger.</p>{btn("Consulter les grilles", "grilles.html", "outline")}</div></div>') + \
        section("Organisation du parcours", f'<h2>De la S1 à la 6e : les cours en immersion.</h2><p class="lead">{esc(I["intro"])}</p><div class="years">{st}</div><p class="notice" style="margin-top:16px">{esc(I["note_heures"])}</p><p class="media-note">{esc(I["evaluation"])}</p>', "soft") + \
        section("Les atouts de l’immersion", f'<div class="split" style="align-items:start"><div><h2>Choisir l’immersion, c’est développer…</h2><ul class="ticks big">{"".join(f"<li>{esc(x)}</li>" for x in I["atouts"])}</ul><h3 style="margin-top:26px">Et pour la suite</h3><ul class="ticks big">{"".join(f"<li>{esc(x)}</li>" for x in I["atouts_fb"])}</ul></div><div><h2>Des activités concrètes</h2><ul class="ticks big">{"".join(f"<li>{esc(x)}</li>" for x in I["activites"])}</ul></div></div>') + \
        section("Les langues à SFX1", f'<h2>Une progression de la S1 à la rhéto.</h2><div class="info-cards">{langs}</div>', "soft") + \
        section("En classe", f'<div class="split"><div><h2>Travailler ensemble, en néerlandais.</h2><p class="lead">Travaux en binômes, dossiers thématiques, recherches : les élèves pratiquent la langue au quotidien.</p></div><div class="photo-frame">{pic("immersion-binome", "Deux élèves travaillant sur un exercice en néerlandais", sizes="(max-width:650px) 100vw, 600px")}</div></div>') + \
        (section("En vidéo", f'<h2>L’immersion racontée par le Collège.</h2>{videos_grid("immersion")}') if SHOW_VID else "") + \
        section("Se renseigner", f'<div class="banner"><div><h2>Une question sur l’immersion ?</h2><p>Notre équipe pourra préciser les conditions d’accès et les modalités actuelles.</p></div>{btn("Nous contacter", "contact.html", "light")}</div>')

F = C["fondamental"]
DECO = ('<svg class="kd-deco" viewBox="0 0 600 420" aria-hidden="true" focusable="false">'
        '<circle class="kd-sun" cx="470" cy="110" r="58" fill="#ffc845"/>'
        '<g class="kd-rays" stroke="#ffc845" stroke-width="10" stroke-linecap="round">' + "".join(f'<line x1="470" y1="20" x2="470" y2="0" transform="rotate({a} 470 110)"/>' for a in range(0, 360, 45)) + '</g>'
        '<path class="kd-cloud" d="M70 150a40 40 0 0 1 70-26 50 50 0 0 1 92 18 34 34 0 0 1-6 66H82a38 38 0 0 1-12-58z" fill="#fff"/>'
        '<g class="kd-crayons"><rect x="90" y="300" width="150" height="26" rx="8" fill="#e36f67" transform="rotate(-12 90 300)"/><rect x="120" y="335" width="170" height="26" rx="8" fill="#39b8a6" transform="rotate(-6 120 335)"/><rect x="160" y="370" width="150" height="26" rx="8" fill="#5aa9e6" transform="rotate(4 160 370)"/></g>'
        '<path d="M330 360c40-60 90-60 130 0s90 60 130 0" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity=".55"/>'
        '<g fill="#fff" opacity=".9"><path class="kd-star" d="M360 210l9 19 21 3-15 15 4 21-19-10-19 10 4-21-15-15 21-3z"/></g></svg>')

def kid_child(x, y, skin, shirt, hair, s=1.0, arm=0):
    """Petit personnage stylisé (dessin original)."""
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<rect x="-22" y="40" width="44" height="58" rx="18" fill="{shirt}"/>'
            f'<rect x="-36" y="46" width="14" height="40" rx="7" fill="{shirt}" transform="rotate({-arm} -29 50)"/>'
            f'<rect x="22" y="46" width="14" height="40" rx="7" fill="{shirt}" transform="rotate({arm} 29 50)"/>'
            f'<rect x="-16" y="94" width="13" height="36" rx="6" fill="#3b2a33"/><rect x="3" y="94" width="13" height="36" rx="6" fill="#3b2a33"/>'
            f'<circle cx="0" cy="14" r="26" fill="{skin}"/><path d="M-27 10a27 27 0 0 1 54 0c-8-10-20-14-27-14s-19 4-27 14z" fill="{hair}"/>'
            f'<circle cx="-9" cy="16" r="3" fill="#2a1a21"/><circle cx="9" cy="16" r="3" fill="#2a1a21"/>'
            f'<path d="M-8 26q8 7 16 0" stroke="#2a1a21" stroke-width="3" fill="none" stroke-linecap="round"/>'
            f'<circle cx="-15" cy="24" r="4" fill="#f59a9a" opacity=".6"/><circle cx="15" cy="24" r="4" fill="#f59a9a" opacity=".6"/></g>')

def kid_illus(kind, label):
    bg = {"jardin": "#c9efe8", "classe": "#ffe7a3", "cour": "#d6e9fa"}[kind]
    sc = [f'<rect width="600" height="420" fill="{bg}"/>', '<circle cx="510" cy="80" r="44" fill="#ffc845"/>',
          '<path d="M0 330q150-40 300 0t300 0v90H0z" fill="#8fd18a"/>']
    if kind == "jardin":
        sc += ['<rect x="90" y="170" width="22" height="150" rx="8" fill="#8a5a3c"/><circle cx="101" cy="150" r="70" fill="#39b8a6"/><circle cx="60" cy="190" r="40" fill="#2fa494"/>',
               '<g fill="#e36f67"><circle cx="330" cy="330" r="9"/><circle cx="360" cy="342" r="7"/><circle cx="520" cy="335" r="8"/></g>',
               kid_child(250, 200, "#f2c7a5", "#e36f67", "#5b3a29", 1, 25), kid_child(400, 210, "#8d5a3b", "#5aa9e6", "#1f1410", .9, -20)]
    elif kind == "classe":
        sc += ['<rect x="60" y="60" width="300" height="150" rx="12" fill="#2f6b5e"/><text x="90" y="125" font-family="Inter,sans-serif" font-size="44" font-weight="800" fill="#fff">a b c</text><text x="90" y="180" font-family="Inter,sans-serif" font-size="36" font-weight="700" fill="#ffe94d">1 + 2 = 3</text>',
               '<rect x="40" y="300" width="520" height="22" rx="8" fill="#c98b5e"/>',
               '<g><rect x="200" y="282" width="60" height="18" rx="4" fill="#5aa9e6"/><rect x="330" y="285" width="70" height="8" rx="4" fill="#e36f67" transform="rotate(-10 330 285)"/><rect x="420" y="286" width="60" height="8" rx="4" fill="#39b8a6"/></g>',
               kid_child(180, 160, "#f2c7a5", "#98052b", "#c47a2c", .95, 40), kid_child(450, 170, "#c98a64", "#39b8a6", "#2a1a21", .9, 35)]
    else:
        sc += ['<rect x="420" y="190" width="12" height="140" fill="#98052b"/><rect x="520" y="190" width="12" height="140" fill="#98052b"/><rect x="410" y="182" width="132" height="14" rx="7" fill="#98052b"/>',
               '<path d="M450 196v80M500 196v80" stroke="#2a1a21" stroke-width="3"/><rect x="440" y="272" width="72" height="10" rx="4" fill="#ffc845"/>',
               '<circle cx="320" cy="350" r="22" fill="#e36f67"/><path d="M298 350h44M320 328v44" stroke="#fff" stroke-width="3"/>',
               kid_child(160, 190, "#f2c7a5", "#ffc845", "#7a4b2a", 1, 60), kid_child(270, 205, "#6e4329", "#e36f67", "#1f1410", .85, -45)]
    return f'<svg class="kd-illus" viewBox="0 0 600 420" role="img" aria-label="{label}">' + "".join(sc) + '</svg>'

def kid_hero(kicker, h1, lead, crumbs, chips):
    cr = '<a href="index.html">Accueil</a>' + "".join(f'<span aria-hidden="true">/</span>' + (f'<a href="{u}">{t}</a>' if u else t) for t, u in crumbs)
    return (f'<section class="kd-hero"><div class="wrap kd-hero-in"><div><nav class="crumbs" aria-label="Fil d’Ariane">{cr}</nav>'
            f'<p class="kd-kicker">{kicker}</p><h1>{h1}</h1><p class="lead">{lead}</p><div class="kd-chips">{"".join(f"<span>{c}</span>" for c in chips)}</div></div>{DECO}</div>'
            '<svg class="kd-wave" viewBox="0 0 1440 80" preserveAspectRatio="none" aria-hidden="true"><path d="M0 40c240 50 480 50 720 0s480-50 720 0v40H0z" fill="#fffaf3"/></svg></section>')

def kid_day(items):
    return '<ol class="kd-day">' + "".join(f'<li class="scroll-reveal"><span class="kd-e" aria-hidden="true">{e}</span><b>{h or "&nbsp;"}</b><span>{esc(t)}</span></li>' for e, h, t in items) + '</ol>'

def kid_projects(items):
    return '<div class="kd-proj">' + "".join(f'<article class="kd-card scroll-reveal"><span class="kd-e" aria-hidden="true">{e}</span><h3>{esc(t)}</h3><p>{esc(r)}</p></article>' for e, t, r in items) + '</div>'

def kid_contacts():
    out = []
    for e, role, who, tel, mail in F["contacts"]:
        t = f'<a href="tel:+32{tel.replace(" ", "")[1:]}">{tel}</a>'
        m = f'<br><a href="mailto:{mail}">{mail}</a>' if mail else ""
        out.append(f'<div class="kd-contact scroll-reveal"><span class="kd-e" aria-hidden="true">{e}</span><small>{role}</small><b>{esc(who)}</b><p>{t}{m}</p></div>')
    return '<div class="kd-contacts">' + "".join(out) + '</div>'

def kid_bridge():
    return section("Et après la 6e ?", f'<div class="kd-bridge"><div><h2>Le Collège, juste à côté.</h2><p class="lead">Après la 6e primaire, la S1 du secondaire se vit sur le même site, avec des visages connus et un passage accompagné, y compris en immersion en néerlandais.</p></div><div class="buttons" style="margin:0">{btn("Le secondaire", "secondaire.html")}<a class="btn outline" href="portes-ouvertes.html" {TIMED}>Portes ouvertes du 30 janvier <span aria-hidden="true">↗</span></a></div></div>')

@page("fondamental.html", "École fondamentale · Collège SFX1 Verviers", "L’école fondamentale du Collège SFX1 à Verviers : maternelle et primaire, une école verte au cœur de la ville. Projets, horaires et contacts.")
def p_fondamental():
    return '<div class="kid">' + kid_hero("École fondamentale · maternelle &amp; primaire", "Ici, on grandit<br><span>en s’amusant !</span>", "Une école verte au cœur de Verviers, où chaque enfant apprend, découvre et prend confiance, de la maternelle à la 6e primaire.", [("Fondamental", None)], ["🌳 Une école verte", "🧭 Pédagogie ignatienne", "🏊 À deux pas du parc Fabiola"]) + \
        section("Bienvenue !", f'<div class="kd-split"><div class="kd-photo">{kid_illus("jardin", "Illustration : deux enfants jouent dans le jardin de l’école")}</div><div><h2>Une école où l’on ose <span class="kd-hl">se dépasser</span>.</h2><p class="lead">Liée à la Compagnie de Jésus, notre école vit la pédagogie ignatienne au quotidien.</p><p>Nous proposons un enseignement varié qui combine exigence, méthode et persévérance, et qui encourage chaque élève à donner le meilleur de lui-même, à son rythme, dans un cadre verdoyant et rassurant.</p></div></div>') + \
        section("Nos deux écoles", f'<h2>Choisis ton école !</h2><div class="kd-doors"><a class="kd-door kd-door-m scroll-reveal" href="maternelle.html"><span class="kd-e" aria-hidden="true">🧸</span><small>De la 1re à la 3e maternelle</small><b>L’école maternelle</b><span>Jouer, explorer, découvrir les autres et grandir en confiance.</span><i aria-hidden="true">→</i></a><a class="kd-door kd-door-p scroll-reveal" href="primaire.html"><span class="kd-e" aria-hidden="true">✏️</span><small>De la 1re à la 6e primaire</small><b>L’école primaire</b><span>Apprendre, créer, agir ensemble et devenir un vrai citoyen.</span><i aria-hidden="true">→</i></a></div>', "kd-soft") + \
        section("Nos projets", f'<h2>Une école pleine de projets.</h2>{kid_projects(F["projets"])}') + \
        section("Infos pratiques", f'<h2>On vous répond.</h2>{kid_contacts()}<div class="kd-access scroll-reveal"><span class="kd-e" aria-hidden="true">📍</span><div><b>Rue de Rome 18, 4800 Verviers</b><p>On entre par la rue de Rome ou par le parc Fabiola, où se trouve la piscine communale.</p></div>{btn("Itinéraire", "https://www.google.com/maps/search/?api=1&amp;query=Rue+de+Rome+18+4800+Verviers", "outline", True)}</div>', "kd-soft", "infos-pratiques") + \
        kid_bridge() + '</div>'

@page("maternelle.html", "École maternelle · Collège SFX1 Verviers", "L’école maternelle du Collège SFX1 à Verviers : jouer, découvrir, grandir. Horaires et informations pratiques.", "maternelle.html")
def p_maternelle():
    return '<div class="kid">' + kid_hero("École fondamentale · maternelle", "Mes premiers pas<br><span>à l’école !</span>", "Jouer, explorer, découvrir les autres et grandir en confiance, dans une école verte au cœur de Verviers.", [("Fondamental", "fondamental.html"), ("Maternelle", None)], ["🧸 Accueil dès 8h15", "🍎 Collation en classe", "🌳 Un cadre verdoyant"]) + \
        section("Une journée chez les petits", f'<h2>Ma journée, pas à pas.</h2>{kid_day(F["h_mat"])}<p class="media-note">{tbv()} Horaires repris de l’ancien site : à confirmer pour l’année en cours.</p>') + \
        section("Grandir ensemble", f'<div class="kd-split"><div><h2>Apprendre en <span class="kd-hl">jouant</span>.</h2><p class="lead">En maternelle, chaque enfant découvre le plaisir d’apprendre : on manipule, on chante, on crée, on s’exprime et on apprend à vivre avec les autres.</p><p>Les équipes accompagnent chacun à son rythme, avec bienveillance, pour préparer en douceur l’entrée en primaire.</p>{btn("Nous contacter", "fondamental.html#infos-pratiques", "outline")}</div><div class="kd-photo">{kid_illus("classe", "Illustration : deux enfants en classe devant le tableau")}</div></div>', "kd-soft") + \
        section("Et ensuite ?", f'<div class="kd-bridge"><div><h2>Cap sur la primaire !</h2><p class="lead">Projets citoyens, sorties, spectacles : découvrez la vie à l’école primaire.</p></div>{btn("L’école primaire", "primaire.html")}</div>') + '</div>'

@page("primaire.html", "École primaire · Collège SFX1 Verviers", "L’école primaire du Collège SFX1 à Verviers : apprendre, agir et vivre ensemble. Projets, sorties, horaires.", "primaire.html")
def p_primaire():
    return '<div class="kid">' + kid_hero("École fondamentale · primaire", "Apprendre, agir<br><span>et vivre ensemble !</span>", "Des apprentissages solides, des projets citoyens et plein de découvertes, de la 1re à la 6e primaire.", [("Fondamental", "fondamental.html"), ("Primaire", None)], ["🐘 L’éléphant des lois", "🐄 Classes vertes", "🎭 Théâtre"]) + \
        section("Une journée en primaire", f'<h2>Ma journée, pas à pas.</h2>{kid_day(F["h_prim"])}<p class="media-note">{tbv()} Horaires repris de l’ancien site : à confirmer pour l’année en cours.</p>') + \
        section("Nos projets", f'<h2>Des projets qui font grandir.</h2>{kid_projects(F["projets"])}', "kd-soft") + \
        section("Dehors aussi", f'<div class="kd-split"><div class="kd-photo">{kid_illus("cour", "Illustration : des enfants jouent dans la cour de récréation")}</div><div><h2>On apprend <span class="kd-hl">partout</span>.</h2><p class="lead">Selon l’âge : classes à la ferme, sorties nature, classes vertes, spectacles de théâtre à l’école et à l’extérieur.</p><p>Une fois par an, les élèves partent à la rencontre d’autres cultures, et une année sur deux, toute l’école prépare le spectacle de Noël.</p></div></div>') + \
        kid_bridge() + '</div>'

@page("portes-ouvertes.html", "Portes ouvertes 2027 · Collège SFX1 Verviers", "Portes ouvertes du Collège Saint-François-Xavier I : samedi 30 janvier 2027, quatre créneaux de visite (9h, 11h, 14h, 16h). Inscription obligatoire.")
def p_po():
    reg = (btn("Je réserve mon créneau de visite", PO["inscription_url"], "", True) if (PO.get("inscription_url") and PO.get("reservation_ouverte"))
           else reserve_btn("") + f'<p class="notice" style="margin-top:14px"><b>Inscription obligatoire.</b> La réservation des créneaux en ligne ouvrira très bientôt sur cette page. En attendant, contactez-nous : <a href="mailto:info@sfx1.org?subject=Portes%20ouvertes%2030%20janvier%202027">info@sfx1.org</a> · <a href="tel:+3287393939">087 39 39 39</a>.</p>')
    why = ["Un enseignement de qualité, une perspective d’excellence", "Un encadrement individualisé, un réel soutien", "Une école ouverte aux autres, humaine et solidaire", "Une école à la découverte du monde", "Une école jésuite alliant tradition et innovation"]
    proj = ["Plateforme numérique Cabanga", "EcoTeam", "Chaque année, un thème de la pédagogie ignacienne : cura personalis, discernement, foi et justice, a priori favorable, exercices, excellence", "Le gospel", "Projet numérique : un Chromebook pour tous les élèves de S1 et de 4e, avec casier sécurisé — un outil, pas une finalité, pour une utilisation cadrée et raisonnable"]
    return f'''<section class="po-hero"><div class="wrap po-hero-in"><div><nav class="crumbs" aria-label="Fil d’Ariane"><a href="index.html">Accueil</a><span aria-hidden="true">/</span>Portes ouvertes</nav>
<p class="eyebrow">Bien plus qu’une école !</p><h1>Portes ouvertes<br><span>{PO["date_txt"]}</span></h1>
<p class="lead">Quatre créneaux pour découvrir le Collège, ses lieux, ses équipes et son projet. {esc(PO["inscription_note"])}.</p>{creneaux_html()}
<div class="countdown big" data-countdown="{PO["date_iso"]}" aria-live="off"></div>
<div class="buttons">{reserve_btn()}</div>
<p class="po-past notice" hidden>Les portes ouvertes 2027 ont eu lieu. Merci pour votre visite ! Pour toute question : <a href="contact.html">contactez-nous</a>.</p></div>
<div class="po-poster big">{pic("affiche-po-2027", "Affiche des portes ouvertes du samedi 30 janvier 2027 : quatre créneaux, 9h, 11h, 14h et 16h", sizes="(max-width:800px) 90vw, 460px", eager=True)}</div></div></section>''' + \
        section("S’inscrire", f'<div class="split"><div><h2>Réservez votre créneau.</h2><p class="lead">L’inscription est obligatoire pour organiser l’accueil de chaque groupe dans de bonnes conditions.</p>{reg}</div><div class="info-cards" style="grid-template-columns:1fr 1fr"><div class="info-card"><span class="ico" aria-hidden="true">📍</span><h3>Où ?</h3><p>Rue de Rome 18, 4800 Verviers — à deux pas de la gare centrale et de la gare du Palais.</p></div><div class="info-card"><span class="ico" aria-hidden="true">🕘</span><h3>Quand ?</h3><p>{PO["date_txt"]}, à 9h, 11h, 14h ou 16h.</p></div></div></div>') + \
        section("Pourquoi choisir SFXun ?", f'<div class="split" style="align-items:start"><div><h2>Ce que vous découvrirez.</h2><ul class="ticks big">{"".join(f"<li>{esc(x)}</li>" for x in why)}</ul></div><div><h2>Nos projets actuels</h2><ul class="ticks">{"".join(f"<li>{esc(x)}</li>" for x in proj)}</ul></div></div>', "soft") + \
        section("Idées reçues", myths(), "") + \
        section("À voir avant de venir", f'<div class="cards">{card("sfx-microscope", "Secondaire", "Grilles et options", "Le tronc commun S1–S3 et les options du 2e et du 3e degré.", "grilles.html")}{card("immersion-binome", "Langues", "Immersion en néerlandais", "Le parcours EMILE de la S1 à la 6e.", "immersion.html")}{card("sfx-ecrit", "Accompagnement", "L’excellence, un chemin accompagné", "Co-enseignement, tutorat, coaching, école des devoirs…", "secondaire.html")}</div>') + \
        section("Partager", f'<div class="banner"><div><h2>Faites passer le mot !</h2><p>Affiche A4 à imprimer et visuel pour les réseaux sociaux.</p></div><div class="buttons" style="margin:0">{btn("Affiche A4 (PDF)", "documents/portes-ouvertes/Affiche-Portes-ouvertes-2027-A4.pdf", "light", True)}{btn("Visuel réseaux sociaux", "documents/portes-ouvertes/Visuel-Portes-ouvertes-2027-reseaux-sociaux.jpg", "ghost", True)}</div></div>', "soft") + \
        fond_banner()

@page("actualites.html", "Vie à SFX1 · Actualités", "Projets, activités et moments forts de la vie au Collège SFX1.", "actualites.html")
def p_actualites():
    cats = ["Tous"] + list(dict.fromkeys(n["tag"] for n in C["actualites"]))
    chips = "".join(f'<button type="button" class="chip{" selected" if i == 0 else ""}" data-value="{c}" aria-pressed="{str(i == 0).lower()}">{c}</button>' for i, c in enumerate(cats))
    return page_hero("La vie à SFX1", "Des projets, des visages, des histoires.", "Découvrez les activités, les initiatives et les événements qui font vivre le Collège.", [("Vie à SFX1", None)]) + \
        section("À la une", f'{fb_banner()}<div class="toolbar" role="group" aria-label="Filtrer par catégorie" data-filter-group="newsbox">{chips}</div><p id="newsbox-live" class="sr-only" aria-live="polite"></p><div class="cards" id="newsbox">{"".join(news_card(n) for n in C["actualites"])}</div><div class="empty-state">Aucune actualité dans cette catégorie.</div>') + \
        section("Dans les médias", f'<h2>Ils parlent de nous.</h2><p class="lead">Reportages et articles consacrés au Collège. Les liens ouvrent le site du média.</p>{press_grid(C["presse"])}<div class="placeholder" style="margin-top:22px"><strong>Semaine RCD — reportage Vedia</strong> : emplacement réservé, lien à fournir.</div>', "soft", "medias") + \
        section("Les événements", f'<div class="banner"><div><h2>Ce qui arrive à SFX1.</h2><p>Un agenda scolaire sera alimenté par les personnes chargées de la communication.</p></div>{btn("Voir l’agenda", "agenda.html", "light")}</div>', "soft")

@page("agenda.html", "Agenda · Collège SFX1 Verviers", "L’agenda du Collège SFX1 : réunions, congés, examens, activités et événements.", "agenda.html")
def p_agenda():
    A = C["agenda_app"]
    if A.get("url"):
        emb = f'<div class="agenda-frame"><iframe src="{esc(A["url"])}" title="Agenda du Collège" loading="lazy"></iframe></div>' if A.get("integration") else ""
        body = f'<div class="section-header"><div><h2>Toutes les dates de l’année.</h2><p class="lead">{esc(A["texte"])}</p></div>{btn("Ouvrir l’agenda en grand", A["url"], "", True)}</div>{emb}'
    else:
        body = f'<div class="agenda-soon"><span aria-hidden="true">📅</span><div><h2>L’agenda arrive bientôt ici.</h2><p class="lead">{esc(A["texte"])} L’agenda en ligne du Collège sera intégré directement sur cette page.</p></div></div>'
    return page_hero("Vie scolaire · Agenda", "Les prochains rendez-vous.", "Réunions de parents, congés, examens, activités : toutes les dates de l’année au même endroit.", [("Vie à SFX1", "actualites.html"), ("Agenda", None)]) + \
        section("Agenda", body)

@page("videos.html", "Vidéos · Collège SFX1 Verviers", "Découvrir le Collège SFX1 à travers les vidéos de sa chaîne YouTube officielle.", "videos.html")
def p_videos():
    topics = "".join(f'<a href="{YT_CHANNEL}" target="_blank" rel="noopener noreferrer">{t} <span aria-hidden="true">↗</span></a>' for t in ["Le Collège au cœur de la ville"])
    return page_hero("Notre Collège · Vidéos", "SFX1 en images.", "Découvrir le Collège à travers les vidéos publiées sur sa chaîne YouTube officielle.", [("Vidéos", None)]) + \
        section("Les plus récentes", f'<h2>Les dernières vidéos du Collège.</h2><p class="lead">De la plus récente à la plus ancienne. Titres et descriptions à préciser. {tbv()}</p>{videos_grid("videos-recentes")}') + \
        section("Vidéos de la chaîne", f'<h2>Entrez dans la vie du Collège.</h2><p class="lead">Les vidéos de la chaîne officielle du Collège, dont les deux vidéos de l’ancien Google Sites. Le lecteur ne se charge qu’au clic.</p>{videos_grid("videos")}', "soft") + \
        section("Retrouvez les autres vidéos", f'<h2>Explorer la chaîne du Collège</h2><p class="lead">La chaîne officielle présente aussi les thèmes suivants. Les liens renvoient à la chaîne afin de retrouver les publications originales.</p><div class="video-topics">{topics}</div><div class="buttons">{btn("Ouvrir la chaîne YouTube officielle", YT_CHANNEL, "", True)}</div><p class="media-note">Chaîne : @collegesaint-francois-xavi4810</p>')

@page("documents.html", "Documents · Collège SFX1 Verviers", "Bibliothèque documentaire du Collège SFX1 : grilles horaires, options, projet éducatif, ROI, RGE, frais scolaires, charte numérique.")
def p_documents():
    cats = ["Tous", "Institutionnels", "Règlements", "Grilles · tronc commun", "Grilles · 2e degré", "Grilles · 3e degré", "Portes ouvertes"]
    chips = "".join(f'<button type="button" class="chip{" selected" if i == 0 else ""}" data-value="{c}" aria-pressed="{str(i == 0).lower()}"{(" " + TIMED) if c == "Portes ouvertes" else ""}>{c}</button>' for i, c in enumerate(cats))
    return page_hero("Ressources · Téléchargements", "Les documents utiles, au même endroit.", "Grilles, options, projets pédagogiques et règlements : une bibliothèque accessible aux familles.", [("Documents", None)]) + \
        section("Bibliothèque", f'<div class="doc-tools"><div class="toolbar" style="margin:0" role="group" aria-label="Filtrer par catégorie" data-filter-group="docsbox">{chips}</div><label class="doc-search"><span class="sr-only">Rechercher un document</span><input type="search" placeholder="Rechercher un document…" data-search="docsbox"></label></div><p id="docsbox-live" class="sr-only" aria-live="polite"></p><div class="doc-grid" id="docsbox">{"".join(doc_card(d) for d in C["documents"])}</div><div class="empty-state">Aucun document ne correspond à votre recherche.</div><p class="media-note">Légende : <span class="badge pdf">PDF</span> fichier à télécharger · <span class="badge drive">Dossier Google Drive</span> dossier contenant un ou plusieurs documents · <span class="badge ancien">Ancien site</span> lien provisoire. Les documents institutionnels restent hébergés à leur emplacement d’origine.</p>')

@page("contact.html", "Contact & accès · Collège SFX1 Verviers", "Coordonnées, plan d’accès et formulaire de contact du Collège Saint-François-Xavier I, rue de Rome 18, 4800 Verviers.")
def p_contact():
    osm = "https://www.openstreetmap.org/export/embed.html?bbox=5.8560%2C50.5850%2C5.8720%2C50.5930&amp;layer=mapnik"
    return page_hero("Contact & accès", "Rencontrons-nous.", "Une question sur le Collège, les enseignements, les inscriptions ou la vie scolaire ?", [("Contact", None)]) + \
        section("Nos coordonnées", f'<div class="two-col"><div><h2>Au cœur de Verviers.</h2><p class="lead"><strong>Centre Scolaire Saint-François-Xavier I</strong><br>Rue de Rome 18<br>4800 Verviers, Belgique</p><p><strong>Secondaire</strong><br><a href="tel:+3287393939">087 39 39 39</a><br><a href="mailto:info@sfx1.org">info@sfx1.org</a></p><p id="fondamental"><strong>Fondamental</strong><br><a href="tel:+3287393930">087 39 39 30</a><br><a href="mailto:direction.fondamental@sfx1.org">direction.fondamental@sfx1.org</a></p></div>{form_html("contact")}</div>') + \
        section("Plan d’accès", f'<div class="section-header"><div><h2>Venir au Collège.</h2><p class="lead">À proximité du centre-ville et de la gare de Verviers.</p></div>{btn("Itinéraire sur Google Maps", "https://www.google.com/maps/search/?api=1&query=Rue+de+Rome+18+4800+Verviers", "outline", True)}</div><div class="map-stage">{pic("cour-automne", "", sizes="100vw")}<div class="map-cta"><h3 style="color:#fff;margin:0">Afficher la carte interactive</h3><p>La carte OpenStreetMap n’est chargée qu’après votre clic. Une connexion Internet est nécessaire.</p><button type="button" class="btn light" data-map="{osm}">Afficher la carte <span aria-hidden="true">↗</span></button></div></div><p class="media-note">{tbv()} La carte montre le centre de Verviers ; un repère précis sur l’entrée du Collège sera ajouté après vérification des coordonnées. L’itinéraire Google Maps utilise l’adresse exacte.</p>', "soft")

@page("espace.html", "Espace numérique · Collège SFX1 Verviers", "Portail des enseignants et outils numériques du Collège SFX1.")
def p_espace():
    tools = "".join(f'<a class="link-card" href="{u}" target="_blank" rel="noopener noreferrer">{t} <span aria-hidden="true">↗</span></a>' for t, u in [("Google Classroom", "https://classroom.google.com"), ("Gmail", "https://mail.google.com"), ("Google Drive", "https://drive.google.com")])
    return page_hero("Espace numérique", "Les outils du Collège.", "Le portail des enseignants et les services numériques, accessibles avec un compte @sfx1.org.", [("Espace numérique", None)]) + \
        section("Portail des enseignants", f'<div class="portal-card"><span class="portal-ico" aria-hidden="true">🔐</span><div><h2>Portail des enseignants</h2><p class="lead">Ressources, documents internes et communications de l’établissement. L’accès est réservé aux enseignants : la connexion se fait automatiquement avec le compte Google @sfx1.org.</p></div><a class="btn" href="{PORTAIL}" target="_blank" rel="noopener noreferrer">Ouvrir le portail <span aria-hidden="true">↗</span></a></div>') + \
        section("Élèves et enseignants", f'<div class="split"><div><h2>Les services Google du Collège.</h2><p class="lead">Classroom, messagerie et Drive, avec le compte @sfx1.org remis par l’école.</p></div><div class="stack">{tools}</div></div>', "soft")

@page("mentions-legales.html", "Mentions légales · Collège SFX1 Verviers", "Mentions légales du site du Collège Saint-François-Xavier I.")
def p_ml():
    return page_hero("Informations légales", "Mentions légales.", "Informations relatives à l’éditeur et à l’hébergement du site.", [("Mentions légales", None)]) + \
        section("Éditeur", f'''<div class="prose">
<h2>Éditeur du site</h2><p>Centre Scolaire Saint-François-Xavier I<br>Rue de Rome 18, 4800 Verviers, Belgique<br>Téléphone : 087 39 39 39 · Email : info@sfx1.org<br>Pouvoir organisateur : Centre Scolaire Saint-François-Xavier ASBL, numéro d’entreprise 0411.614.748<br>Responsable de la publication : Anthony Cipolla, directeur</p>
<h2>Hébergement</h2><p>Netlify, Inc., San Francisco (États-Unis) — <a href="https://www.netlify.com" target="_blank" rel="noopener noreferrer">www.netlify.com</a></p>
<h2>Conditions générales d’utilisation</h2><p>{ext("Conditions générales d’utilisation du site web (PDF)", "https://drive.google.com/file/d/1puGryP46W3saOhaFFTnrgbVZE2Ae8xKv/view?usp=sharing")}</p>
<h2>Propriété intellectuelle</h2><p>Le logo, les textes et les photographies sont la propriété du Collège ou utilisés avec autorisation. Toute reproduction nécessite un accord préalable.</p>
<h2>Droit à l’image</h2><p>Les photographies d’élèves ne sont publiées qu’avec les autorisations requises. Pour toute demande de retrait : info@sfx1.org.</p></div>''')

@page("confidentialite.html", "Confidentialité · Collège SFX1 Verviers", "Politique de confidentialité et de protection des données du site du Collège SFX1.")
def p_conf():
    return page_hero("Protection des données", "Confidentialité.", "Comment ce site traite les données personnelles, conformément au RGPD.", [("Confidentialité", None)]) + \
        section("Vos données", f'''<div class="prose"><p>Responsable du traitement : Centre Scolaire Saint-François-Xavier ASBL, rue de Rome 18, 4800 Verviers — info@sfx1.org. {ext("Déclaration de confidentialité intégrale (PDF)", "https://drive.google.com/file/d/1jw-B91oml6LNjYW9U3DVEg97c--e7hAO/view?usp=sharing")}</p>
<h2>Cookies et traceurs</h2><p>Ce site n’utilise aucun cookie de mesure d’audience ni de publicité. Les polices sont hébergées sur le site lui-même.</p>
<h2>Contenus externes chargés à la demande</h2><p>Les vidéos YouTube (via youtube-nocookie.com) et la carte OpenStreetMap ne sont chargées qu’après un clic du visiteur. Ces services peuvent alors traiter des données techniques (adresse IP, navigateur) selon leurs propres politiques.</p>
<h2>Formulaire de contact</h2><p>Les informations saisies (nom, adresse email, sujet, message) servent uniquement à répondre à votre demande. Elles sont transmises par email au secrétariat du Collège (info@sfx1.org) et ne sont ni revendues ni utilisées à d’autres fins. Base légale : votre consentement. Le formulaire est traité par notre hébergeur, Netlify ; les messages sont conservés le temps nécessaire au traitement de votre demande.</p>
<h2>Vos droits</h2><p>Vous pouvez demander l’accès, la rectification ou l’effacement de vos données en écrivant à info@sfx1.org. Vous pouvez aussi introduire une plainte auprès de l’Autorité de protection des données (Belgique).</p></div>''')

@page("merci.html", "Message envoyé · Collège SFX1 Verviers", "Votre message a bien été envoyé au Collège Saint-François-Xavier I.")
def p_merci():
    return f'<section class="section not-found"><div class="wrap"><h1 style="font-size:64px">Merci !</h1><h2>Votre message est bien parti.</h2><p class="lead" style="margin:0 auto 20px">Nous vous répondrons dans les meilleurs délais à l’adresse indiquée.</p><div class="buttons" style="justify-content:center">{btn("Retour à l’accueil", "index.html")}{btn("Portes ouvertes", "portes-ouvertes.html", "outline")}</div></div></section>'

@page("404.html", "Page introuvable · Collège SFX1 Verviers", "Cette page n’existe pas ou a été déplacée.")
def p_404():
    return f'<section class="section not-found"><div class="wrap"><h1>404</h1><h2>Cette page s’est égarée.</h2><p class="lead" style="margin:0 auto 20px">Elle n’existe pas ou a été déplacée.</p><div class="buttons" style="justify-content:center">{btn("Retour à l’accueil", "index.html")}{btn("Plan des documents", "documents.html", "outline")}</div></div></section>'

# ------------------------------------------------------------------ build
def build():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for d in ["css", "js", "fonts", "img", "icons", "documents", "videos", "admin"]:
        if (SRC / d).exists(): shutil.copytree(SRC / d, OUT / d, ignore=shutil.ignore_patterns(".gitkeep"))
    if not SHOW_VID: PAGES.pop("videos.html", None)
    for fname, (title, desc, fn, cur) in PAGES.items():
        (OUT / fname).write_text(layout(fname, title, desc, fn(), cur), encoding="utf-8")
    # favicon from logo square
    from PIL import Image
    lg = Image.open(SRC / "img/logo-sfxun.jpg").convert("RGB")
    sq = lg.crop((18, 8, 18 + 266, 8 + 266))
    sq.resize((64, 64), Image.LANCZOS).save(OUT / "favicon.png"); sq.resize((180, 180), Image.LANCZOS).save(OUT / "apple-touch-icon.png")
    urls = "".join(f"<url><loc>{SITE_URL}/{'' if f == 'index.html' else f}</loc></url>" for f in PAGES if f not in ("404.html", "merci.html"))
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    if PUBLIE:
        (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {SITE_URL}/sitemap.xml\n")
    else:
        (OUT / "robots.txt").write_text("# VERSION DE TEST : indexation désactivée.\nUser-agent: *\nDisallow: /\n")
    for f in ["netlify.toml", ".htaccess", "contact.php"]:
        shutil.copy(SRC / "deploy" / f, OUT / f)
    print(f"{len(PAGES)} pages générées dans {OUT}")

if __name__ == "__main__":
    build()
