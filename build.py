#!/usr/bin/env python3
"""Génère la landing de Mon chat peut ? en français et en anglais.

Sources dans src/ :
  template.html   le balisage, avec des clés {{nom}}
  styles.css      la feuille de style, intégrée dans chaque page
  app.js          le script, intégré dans chaque page
  i18n/fr.json    les textes et les aliments de la démo, en français
  i18n/en.json    les mêmes clés, en anglais

Sorties : index.html (fr), en/index.html (en) et sitemap.xml.
Usage : python3 build.py
"""
import datetime
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
SITE = "https://mon-chat-peut.com"
STORE = "https://play.google.com/store/apps/details?id=com.dabik.monchatpeut"
PAGES = {"fr": ROOT / "index.html", "en": ROOT / "en" / "index.html"}


def plain(text):
    """Texte brut d'une valeur HTML (pour les données structurées)."""
    return html.unescape(re.sub(r"<[^>]+>", "", text)).replace(" ", " ")


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


def script_json(data):
    """JSON prêt à vivre dans une balise <script> sans pouvoir la refermer."""
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


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
             "image": f"{SITE}/img/og-{t['lang']}.png",
             "author": {"@type": "Person", "name": "Dabi Keita"}},
            {"@type": "FAQPage", "url": t["url"], "inLanguage": t["lang"], "mainEntity": faq},
        ],
    }


def render(template, values):
    def sub(match):
        key = match.group(1)
        if key not in values:
            raise KeyError(f"clé manquante dans le dictionnaire : {key}")
        return values[key]
    return re.sub(r"\{\{(\w+)\}\}", sub, template)


def main():
    template = (SRC / "template.html").read_text(encoding="utf-8")
    css = minify_css((SRC / "styles.css").read_text(encoding="utf-8"))
    js = (SRC / "app.js").read_text(encoding="utf-8").strip()
    for lang, out in PAGES.items():
        t = json.loads((SRC / "i18n" / f"{lang}.json").read_text(encoding="utf-8"))
        values = {k: v for k, v in t.items() if isinstance(v, str)}
        values.update(css=css, js=js, i18n_json=script_json(t["js"]),
                      jsonld=script_json(structured_data(t)))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(template, values), encoding="utf-8")
        print(f"{out.relative_to(ROOT)} : {out.stat().st_size // 1024} Ko")

    today = datetime.date.today().isoformat()
    alternates = (f'    <xhtml:link rel="alternate" hreflang="fr" href="{SITE}/"/>\n'
                  f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/en/"/>\n'
                  f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/"/>\n')
    urls = "".join(
        f"  <url>\n    <loc>{SITE}{path}</loc>\n    <lastmod>{today}</lastmod>\n{alternates}  </url>\n"
        for path in ("/", "/en/")
    ) + "".join(
        f"  <url>\n    <loc>{SITE}/{page}</loc>\n  </url>\n"
        for page in ("privacy-policy.html", "terms-of-service.html", "user-rights.html")
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n",
        encoding="utf-8",
    )
    print("sitemap.xml")


if __name__ == "__main__":
    main()
