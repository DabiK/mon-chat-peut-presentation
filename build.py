#!/usr/bin/env python3
"""Génère le site de Mon chat peut ? en français et en anglais.

Sources dans src/ :
  template.html     la landing, avec des clés {{nom}}
  legal.html        le gabarit des pages légales
  footer.html       le pied de page, commun à toutes les pages
  base.css          polices, couleurs, en-tête et pied de page (toutes les pages)
  landing.css       la landing ; legal.css : les pages légales
  app.js            le script de la landing
  i18n/fr.json      les textes et les aliments de la démo, en français
  i18n/en.json      les mêmes clés, en anglais
  legal/fr/*.html   le contenu des pages légales, en français ; legal/en/*.html : en anglais

Sorties : index.html et en/index.html, les pages légales (privacy-policy.html, terms-of-service.html,
user-rights.html et leurs versions en/), sitemap.xml, puis dist/, le dossier publié par le Worker
Cloudflare : les pages et les fichiers publics, sans src/, les notes ni ce script.
Usage : python3 build.py
"""
import datetime
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
SITE = "https://mon-chat-peut.com"
STORE = "https://play.google.com/store/apps/details?id=com.dabik.monchatpeut"
LANGS = ("fr", "en")
PAGES = {"fr": ROOT / "index.html", "en": ROOT / "en" / "index.html"}
# Pages légales : nom du fichier (et de l'adresse, que Cloudflare sert sans .html) -> clé du libellé
LEGAL = {"terms-of-service": "legal_terms", "privacy-policy": "legal_privacy", "user-rights": "legal_rights"}
DIST = ROOT / "dist"
# Tout ce que sert le site. Le reste du dépôt n'est pas publié.
PUBLIC = ("index.html", "en", "img", "assets/fonts", "favicon-96.png", "apple-touch-icon.png",
          "robots.txt", "sitemap.xml", "privacy-policy.html", "terms-of-service.html",
          "user-rights.html", "_headers")


def plain(text):
    """Texte brut d'une valeur HTML (pour les données structurées)."""
    return html.unescape(re.sub(r"<[^>]+>", "", text)).replace(" ", " ")


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


def script_json(data):
    """JSON prêt à vivre dans une balise <script> sans pouvoir la refermer."""
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def legal_path(lang, page):
    return f"/{page}" if lang == "fr" else f"/en/{page}"


def structured_data(t):
    faq = [
        {"@type": "Question", "name": plain(t[f"faq{i}_q"]),
         "acceptedAnswer": {"@type": "Answer", "text": plain(t[f"faq{i}_a"])}}
        for i in range(1, 6)
    ]
    return {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/",
             "name": "Mon chat peut ?", "inLanguage": ["fr", "en"]},
            {"@type": "MobileApplication", "name": "Mon chat peut ?", "operatingSystem": "Android",
             "applicationCategory": "LifestyleApplication", "description": plain(t["description"]),
             "url": STORE, "installUrl": STORE, "inLanguage": t["lang"],
             "image": f"{SITE}{t['og_image']}",
             "author": {"@type": "Person", "name": "Dabi Keita"}},
            {"@type": "FAQPage", "url": t["url"], "inLanguage": t["lang"], "mainEntity": faq},
        ],
    }


def legal_data(t, page, url):
    meta = t["legal_pages"][page]
    return {
        "@context": "https://schema.org",
        "@type": "WebPage", "name": plain(meta["h1"]), "description": meta["description"],
        "url": url, "inLanguage": t["lang"], "isPartOf": {"@id": f"{SITE}/#website"},
        "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Mon chat peut ?", "item": t["url"]},
            {"@type": "ListItem", "position": 2, "name": plain(meta["h1"]), "item": url},
        ]},
    }


def render(template, values):
    def sub(match):
        key = match.group(1)
        if key not in values:
            raise KeyError(f"clé manquante dans le dictionnaire : {key}")
        return values[key]
    return re.sub(r"\{\{(\w+)\}\}", sub, template)


def chips_html(chips):
    return "".join(
        f'<button type="button" class="chip" data-q="{html.escape(q)}" aria-pressed="false">{html.escape(label)}</button>'
        for q, label in chips
    )


def stamp_word(stamp):
    """« Oui ! » -> « Oui » : le mot seul, pour les tampons d'illustration."""
    return re.sub(r"[\s ]*[!.…]+$", "", stamp)


def publish():
    """Recopie les fichiers publics dans dist/, vidé à chaque build."""
    shutil.rmtree(DIST, ignore_errors=True)
    for name in PUBLIC:
        src, dst = ROOT / name, DIST / name
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".*"))
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    count = sum(1 for f in DIST.rglob("*") if f.is_file())
    print(f"dist/ : {count} fichiers")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"{path.relative_to(ROOT)} : {path.stat().st_size // 1024} Ko")


def main():
    read = lambda name: (SRC / name).read_text(encoding="utf-8")
    template, legal_template, footer = read("template.html"), read("legal.html"), read("footer.html")
    base = read("base.css")
    css_landing, css_legal = minify_css(base + read("landing.css")), minify_css(base + read("legal.css"))
    js = read("app.js").strip()

    for lang in LANGS:
        t = json.loads(read(f"i18n/{lang}.json"))
        t["og_image"] = f"/img/og-carnet-{lang}.png"
        values = {k: v for k, v in t.items() if isinstance(v, str)}
        verdict = t["js"]["verdict"]
        values.update(
            css=css_landing, js=js, i18n_json=script_json(t["js"]),
            jsonld=script_json(structured_data(t)),
            chips_html=chips_html(t["js"]["chips"]),
            count_init=t["count_init"].replace("{n}", str(len(t["js"]["foods"]))),
            v_oui=stamp_word(verdict["oui"]["stamp"]), v_peu=stamp_word(verdict["peu"]["stamp"]),
            v_non=stamp_word(verdict["non"]["stamp"]),
        )
        values["footer"] = render(footer, values)
        write(PAGES[lang], render(template, values))

        # Pages légales : même en-tête et même pied de page, le sélecteur de langue mène à la même page traduite
        other = "en" if lang == "fr" else "fr"
        for page in LEGAL:
            meta = t["legal_pages"][page]
            url = SITE + legal_path(lang, page)
            v = dict(values, css=css_legal, lang_href=legal_path(other, page))
            v.update(
                page_title=meta["title"], page_description=meta["description"], page_h1=meta["h1"],
                page_url=url, page_url_fr=SITE + legal_path("fr", page), page_url_en=SITE + legal_path("en", page),
                page_jsonld=script_json(legal_data(t, page, url)),
                page_content=read(f"legal/{lang}/{page}.html").strip(),
                page_others="\n      ".join(
                    f'<a href="{legal_path(lang, p)}">{t[key]}</a>' for p, key in LEGAL.items() if p != page
                ),
            )
            v["footer"] = render(footer, v)
            out = ROOT / f"{page}.html" if lang == "fr" else ROOT / "en" / f"{page}.html"
            write(out, render(legal_template, v))

    today = datetime.date.today().isoformat()

    def entry(fr_path, en_path):
        alternates = (f'    <xhtml:link rel="alternate" hreflang="fr" href="{SITE}{fr_path}"/>\n'
                      f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}{en_path}"/>\n'
                      f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{fr_path}"/>\n')
        return "".join(
            f"  <url>\n    <loc>{SITE}{path}</loc>\n    <lastmod>{today}</lastmod>\n{alternates}  </url>\n"
            for path in (fr_path, en_path)
        )

    urls = entry("/", "/en/") + "".join(entry(legal_path("fr", p), legal_path("en", p)) for p in LEGAL)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n",
        encoding="utf-8",
    )
    print("sitemap.xml")
    publish()


if __name__ == "__main__":
    main()
