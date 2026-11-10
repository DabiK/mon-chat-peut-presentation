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
PUBLIC = ("index.html", "en", "mon-chat-peut-il-manger", "img", "assets/fonts", "favicon-96.png",
          "apple-touch-icon.png", "robots.txt", "sitemap.xml", "privacy-policy.html", "terms-of-service.html",
          "user-rights.html", "_headers")
# Pages aliment : un dossier par langue, une page par aliment, plus un index (index.html du dossier)
FOODS_DIR = {"fr": "/mon-chat-peut-il-manger/", "en": "/en/can-cats-eat/"}
VIVI_H = {"oui": 342, "peu": 336, "non": 351}
# Aliments de la démo de la landing (nom affiché en français) -> fiche détaillée
DEMO_PAGES = {
    "Chocolat": "chocolat", "Oignon": "oignon", "Ail": "ail", "Poireau": "poireau", "Raisin": "raisin", "Mafé": "mafe",
    "Courgette": "courgette", "Thon": "thon", "Lait": "lait", "Fromage": "fromage", "Yaourt nature": "yaourt",
    "Poulet cuit": "poulet", "Dinde cuite": "dinde", "Bœuf cuit": "boeuf", "Jambon": "jambon", "Saucisson": "saucisson",
    "Saumon cuit": "saumon", "Saumon fumé": "saumon-fume", "Poisson cru": "poisson-cru", "Sardines": "sardines",
    "Crevettes": "crevettes", "Œuf cuit": "oeuf", "Œuf cru": "oeuf-cru", "Os cuits": "os", "Foie": "foie",
    "Riz cuit": "riz", "Pâtes": "pates", "Pain": "pain", "Pâte à pain crue": "pate-crue", "Carotte": "carotte",
    "Concombre": "concombre", "Haricots verts": "haricots-verts", "Citrouille": "citrouille", "Petits pois": "petits-pois",
    "Brocoli": "brocoli", "Épinards": "epinards", "Tomate": "tomate", "Pomme de terre": "pomme-de-terre",
    "Avocat": "avocat", "Pomme": "pomme", "Banane": "banane", "Melon": "melon", "Pastèque": "pasteque",
    "Fraise": "fraise", "Myrtilles": "myrtille", "Agrumes": "orange", "Cerises": "cerise", "Fruits à coque": "noix",
    "Cacahuètes": "cacahuetes", "Café": "cafe", "Alcool": "alcool", "Lys": "lys", "Herbe à chat": "herbe-a-chat",
    "Croquettes pour chien": "croquettes-chien", "Glace": "glace", "Pizza": "pizza", "Maïs": "mais",
    "Huile d'olive": "huile-olive", "Chewing-gum": "chewing-gum", "Champignons": "champignons",
    "Yaourt": "yaourt", "Jambon blanc": "jambon",
}


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
            {"@type": "MobileApplication", "name": "Mon chat peut ?", "operatingSystem": "Android, iOS",
             "applicationCategory": "LifestyleApplication", "description": plain(t["description"]),
             "url": STORE, "installUrl": [t["appstore_href"], STORE], "inLanguage": t["lang"],
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


def fr_typo(text):
    """Espace fine insécable avant ? ! : ; et à l'intérieur des guillemets, en français."""
    text = re.sub(r" ([?!:;»])", " \\1", text)
    return text.replace("« ", "« ")


def esc(text):
    return html.escape(text, quote=False)


def load_foods():
    """La liste des aliments (src/foods/list.json) et leur contenu rédigé (src/foods/content/*.json)."""
    foods = json.loads((SRC / "foods" / "list.json").read_text(encoding="utf-8"))
    content = {}
    for path in sorted((SRC / "foods" / "content").glob("*.json")):
        for entry in json.loads(path.read_text(encoding="utf-8")):
            content[entry["id"]] = entry
    missing = [f["id"] for f in foods if f["id"] not in content]
    if missing:
        print(f"attention : {len(missing)} aliment(s) sans contenu, pas de page : {', '.join(missing[:8])}…")
    out = []
    for f in foods:
        if f["id"] in content:
            c = content[f["id"]]
            # nom, adresse et question viennent de la liste ; le texte de la fiche du contenu
            out.append({**f, "verdict": c["verdict"], "related": c["related"],
                        "fr": {**f["fr"], **c["fr"]}, "en": {**f["en"], **c["en"]}})
    return out


def food_url(lang, food):
    return FOODS_DIR[lang] + food[lang]["slug"]


def food_pages(t, lang, foods, values, template, index_template, footer, css):
    """Écrit les pages aliment d'une langue et leur index. Renvoie (chemin FR, chemin EN) de chaque page pour le sitemap."""
    typo = fr_typo if lang == "fr" else (lambda s: s)
    other = "en" if lang == "fr" else "fr"
    by_id = {f["id"]: f for f in foods}
    words = t["verdict_words"]
    plus = '<span class="faq-plus" aria-hidden="true"><svg viewBox="0 0 18 18"><path d="M9 2v14M2 9h14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg></span>'
    out_dir = ROOT / FOODS_DIR[lang].strip("/")
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    base_values = dict(values, css=css)
    home_url = SITE + values["home_href"]
    index_url = SITE + FOODS_DIR[lang]

    for f in foods:
        c, names = f[lang], f[lang]
        question = typo(names["question"])
        url = SITE + food_url(lang, f)
        related = "".join(
            f'<li data-v="{by_id[r]["verdict"]}"><a class="food-link" href="{food_url(lang, by_id[r])}">'
            f'{esc(by_id[r][lang]["name"])}<span class="pill">{words[by_id[r]["verdict"]]}</span></a></li>'
            for r in f["related"] if r in by_id
        )
        faq_items = [(typo(q["q"]), typo(q["a"])) for q in c["faq"]]
        v = dict(base_values)
        v.update(
            page_title=f"{question} · Mon chat peut{chr(0x202f) if lang == 'fr' else ' '}?",
            page_description=html.escape(typo(c["short"])),
            page_url=url, page_url_fr=SITE + food_url("fr", f), page_url_en=SITE + food_url("en", f),
            lang_href=food_url(other, f),
            # les mots à trait d'union (« peut-il ») ne se coupent pas en fin de ligne dans le titre
            food_question=re.sub(r"(\w+(?:-\w+)+)", r'<span class="nowrap">\1</span>', esc(question)),
            food_question_plain=html.escape(question),
            food_name=esc(names["name"]), cat_label=t["categories"][f["cat"]],
            verdict=f["verdict"], verdict_word=words[f["verdict"]], vivi_h=str(VIVI_H[f["verdict"]]),
            food_short=esc(typo(c["short"])), food_text_why=esc(typo(c["why"])), food_text_amount=esc(typo(c["amount"])),
            food_text_ifeaten=esc(typo(c["ifEaten"])), food_text_alternatives=esc(typo(c["alternatives"])),
            food_risks_html="".join(f"<li>{esc(typo(r))}</li>" for r in c["risks"]),
            food_faq_html="".join(f"<details><summary>{esc(q)}{plus}</summary><p>{esc(a)}</p></details>" for q, a in faq_items),
            food_related_html=related,
            page_jsonld=script_json({
                "@context": "https://schema.org",
                "@graph": [
                    {"@type": "FAQPage", "url": url, "inLanguage": lang, "mainEntity": [
                        {"@type": "Question", "name": question,
                         "acceptedAnswer": {"@type": "Answer", "text": typo(c["short"]) + " " + typo(c["why"])}},
                        *[{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_items],
                    ]},
                    {"@type": "BreadcrumbList", "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Mon chat peut ?", "item": home_url},
                        {"@type": "ListItem", "position": 2, "name": plain(t["foods_link"]), "item": index_url},
                        {"@type": "ListItem", "position": 3, "name": names["name"], "item": url},
                    ]},
                ],
            }),
        )
        v["footer"] = render(footer, v)
        (out_dir / f"{names['slug']}.html").parent.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{names['slug']}.html").write_text(render(template, v), encoding="utf-8")

    # Index : les aliments par famille, avec recherche et filtre par verdict
    order = list(t["categories"])
    groups = []
    for cat in order:
        items = sorted((f for f in foods if f["cat"] == cat), key=lambda f: plain(f[lang]["name"]).lower())
        if not items:
            continue
        lis = "".join(
            f'<li data-v="{f["verdict"]}" data-k="{html.escape(norm_key(f[lang]["name"] + " " + f[lang]["phrase"]))}">'
            f'<a class="food-link" href="{food_url(lang, f)}">{esc(f[lang]["name"])}<span class="pill">{words[f["verdict"]]}</span></a></li>'
            for f in items
        )
        groups.append(f'      <section class="cat" aria-labelledby="cat-{cat}"><h2 id="cat-{cat}">{t["categories"][cat]}</h2><ul>{lis}</ul></section>')
    v = dict(base_values)
    v.update(
        page_url=index_url, page_url_fr=SITE + FOODS_DIR["fr"], page_url_en=SITE + FOODS_DIR["en"],
        lang_href=FOODS_DIR[other],
        foods_lede_n=t["foods_lede"].replace("{n}", str(len(foods))),
        verdict_oui=words["oui"], verdict_peu=words["peu"], verdict_non=words["non"],
        categories_html="\n".join(groups),
        page_jsonld=script_json({
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "CollectionPage", "name": plain(t["foods_h1"]), "url": index_url, "inLanguage": lang,
                 "isPartOf": {"@id": f"{SITE}/#website"},
                 "mainEntity": {"@type": "ItemList", "numberOfItems": len(foods), "itemListElement": [
                     {"@type": "ListItem", "position": i + 1, "url": SITE + food_url(lang, f), "name": f[lang]["question"]}
                     for i, f in enumerate(foods)]}},
                {"@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Mon chat peut ?", "item": home_url},
                    {"@type": "ListItem", "position": 2, "name": plain(t["foods_link"]), "item": index_url},
                ]},
            ],
        }),
    )
    v["footer"] = render(footer, v)
    (out_dir / "index.html").write_text(render(index_template, v), encoding="utf-8")
    print(f"{out_dir.relative_to(ROOT)}/ : {len(foods)} pages aliment + index")


def norm_key(text):
    import unicodedata
    text = text.lower().replace("œ", "oe")
    return "".join(ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn")


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
    food_template, foods_index_template = read("food.html"), read("foods-index.html")
    base = read("base.css")
    css_landing, css_legal = minify_css(base + read("landing.css")), minify_css(base + read("legal.css"))
    css_food = minify_css(base + read("food.css"))
    js = read("app.js").strip()
    foods = load_foods()
    foods_by_id = {f["id"]: f for f in foods}
    # La démo de la landing mène à la fiche de chaque aliment qui en a une (repérée par son nom français)
    demo_ids = [DEMO_PAGES.get(entry[0]) for entry in json.loads(read("i18n/fr.json"))["js"]["foods"]]

    for lang in LANGS:
        t = json.loads(read(f"i18n/{lang}.json"))
        t["og_image"] = f"/img/og-carnet-{lang}.png"
        for entry, fid in zip(t["js"]["foods"], demo_ids):
            entry[5:] = [food_url(lang, foods_by_id[fid]) if fid in foods_by_id else ""]
            if fid in foods_by_id and foods_by_id[fid]["verdict"] != entry[2]:
                print(f"attention : verdict différent entre la démo et la fiche pour {entry[0]} ({entry[2]} / {foods_by_id[fid]['verdict']})")
        values = {k: v for k, v in t.items() if isinstance(v, str)}
        verdict = t["js"]["verdict"]
        first = t["js"]["foods"][0]
        values["init_link"] = first[5] if len(first) > 5 else ""
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

        food_pages(t, lang, foods, values, food_template, foods_index_template, footer, css_food)

    today = datetime.date.today().isoformat()

    def entry(fr_path, en_path):
        alternates = (f'    <xhtml:link rel="alternate" hreflang="fr" href="{SITE}{fr_path}"/>\n'
                      f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}{en_path}"/>\n'
                      f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{fr_path}"/>\n')
        return "".join(
            f"  <url>\n    <loc>{SITE}{path}</loc>\n    <lastmod>{today}</lastmod>\n{alternates}  </url>\n"
            for path in (fr_path, en_path)
        )

    urls = (entry("/", "/en/")
            + entry(FOODS_DIR["fr"], FOODS_DIR["en"])
            + "".join(entry(food_url("fr", f), food_url("en", f)) for f in foods)
            + "".join(entry(legal_path("fr", p), legal_path("en", p)) for p in LEGAL))
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
