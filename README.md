# Mon chat peut ? · site de présentation

Landing page de l'app Mon chat peut ? ([App Store](https://apps.apple.com/fr/app/mon-chat-peut/id6757156768), [Google Play](https://play.google.com/store/apps/details?id=com.dabik.monchatpeut)), en ligne sur https://mon-chat-peut.com (français) et https://mon-chat-peut.com/en/ (anglais).

## Modifier le site

Toutes les pages HTML sont générées : la landing (`index.html`, `en/index.html`) et les pages légales (`privacy-policy.html`, `terms-of-service.html`, `user-rights.html` et leurs versions dans `en/`). On modifie les sources dans `src/`, puis on régénère :

```bash
python3 build.py
```

- `src/template.html` : la landing, avec des clés `{{nom}}`
- `src/legal.html` : le gabarit des pages légales ; `src/legal/fr/*.html` et `src/legal/en/*.html` : leur contenu
- `src/footer.html` : le pied de page, commun à toutes les pages
- `src/i18n/fr.json` et `src/i18n/en.json` : les textes, les titres et descriptions des pages légales et les aliments de la démo (mêmes clés dans les deux fichiers)
- `src/base.css` (polices, couleurs, en-tête, pied de page), `src/landing.css`, `src/legal.css` et `src/app.js` : intégrés dans chaque page au build, pour éviter des requêtes bloquantes
- `img/` : illustrations de Vivi en WebP, images de partage `og-carnet-fr.png` et `og-carnet-en.png`
- `assets/fonts/` : Bricolage Grotesque (titres), Figtree (texte) et DM Mono (étiquettes), hébergées ici (licence SIL OFL)

Direction visuelle « Le carnet de Vivi » : les couleurs sont prises sur Vivi (roux `#F7813A`, crème `#FFF4E8`, pêche `#FCE4CC`, rayure `#9C3C18`, cacao `#3A2A22` pour le texte, menthe de sa gamelle pour le « oui »), formes arrondies, tampon oui / un peu / non. Elles sont définies dans `src/base.css`.

`build.py` régénère aussi `sitemap.xml` (chaque page avec sa traduction), puis recopie dans `dist/` tout ce qui est publié : les pages, `img/`, `assets/fonts/`, les icônes, `robots.txt`, `sitemap.xml` et `_headers`. `src/`, les notes `.md` et `build.py` n'y vont pas. `dist/` n'est pas versionné.

Cloudflare sert les pages sans l'extension (`/privacy-policy`, `/en/privacy-policy`) ; les anciennes adresses en `.html` redirigent vers les nouvelles.

### Pages aliment (référencement)

Une page par aliment et par langue, pour remonter sur les recherches du type « mon chat peut-il manger des chips » / « can cats eat chips » :

- `/mon-chat-peut-il-manger/<aliment>` en français, `/en/can-cats-eat/<food>` en anglais, et un index de chaque côté (`/mon-chat-peut-il-manger/`, `/en/can-cats-eat/`) avec recherche et filtre par verdict ;
- `src/foods/list.json` : la liste des aliments (identifiant, famille, nom, formule et adresse dans chaque langue, question affichée en titre) ;
- `src/foods/content/*.json` : le contenu de chaque fiche, en français et en anglais (verdict `oui` / `peu` / `non`, réponse courte, pourquoi, quantité, risques, que faire s'il en a mangé, alternatives, deux questions fréquentes, aliments proches) ;
- `src/food.html`, `src/foods-index.html` et `src/food.css` : les gabarits et le style.

`build.py` génère les pages, leurs données structurées (FAQ, fil d'Ariane), les liens entre aliments proches, les liens depuis le test de la landing vers la fiche de l'aliment, et ajoute toutes les adresses au sitemap avec leur traduction. Il signale un aliment de la démo dont le verdict diffère de sa fiche.

La liste vient des recherches réelles des utilisateurs (collection Firestore `replyCache` du projet `mon-chat-peut-reborn`), des 60 aliments de la démo et des recherches courantes. Les verdicts et les textes ont été réécrits à partir du consensus vétérinaire, pas repris du cache. Pour ajouter un aliment : une entrée dans `list.json`, son contenu dans un fichier de `src/foods/content/`, puis `python3 build.py`.

## Déployer

Le site est un Cloudflare Worker sans code, qui sert les fichiers de `dist/` (`wrangler.toml`), sur le compte Cloudflare devcompte44@gmail.com.

Chaque push sur `master` le redéploie : le workflow `.github/workflows/deploy.yml` lance `python3 build.py`, puis `wrangler deploy`. On peut aussi le relancer à la main depuis l'onglet Actions (« Run workflow »). Il utilise deux secrets du dépôt GitHub :

- `CLOUDFLARE_ACCOUNT_ID` : l'identifiant du compte Cloudflare ;
- `CLOUDFLARE_API_TOKEN` : un jeton d'API du compte, avec le droit de déployer les Workers et de gérer les routes de la zone `pasdansmonfil.fr`.

Déploiement manuel, après `npx wrangler login` :

```bash
python3 build.py && npx wrangler deploy
```

Cache et en-têtes : `_headers`. Les pages HTML sont revalidées à chaque visite, les polices gardées un an, les images 30 jours (pour remplacer une image tout de suite, changer son nom). Cloudflare compresse les réponses lui-même.

### Domaine

Le DNS de `mon-chat-peut.com` reste chez Hostinger, où sont aussi les e-mails (MX et SPF, à ne pas toucher). Comme `demeure.iamdabi.com`, le domaine passe par Cloudflare for SaaS : `mon-chat-peut.com` et `www.mon-chat-peut.com` sont des noms de domaine personnalisés de la zone `pasdansmonfil.fr` (compte devcompte44@gmail.com).

- Chez Hostinger : `@` en ALIAS (saisi comme un CNAME sur `@`) et `www` en CNAME, vers `mon-chat-peut-saas.pasdansmonfil.fr`.
- Dans la zone `pasdansmonfil.fr` : `mon-chat-peut-saas` est un enregistrement AAAA `100::` proxifié, qui ne sert que de cible ; la route `mon-chat-peut.com/*` envoie le domaine vers le Worker (`wrangler.toml`) ; une règle de redirection (Rules → Redirect Rules) envoie `www.mon-chat-peut.com` vers `https://mon-chat-peut.com` en 301, sauf `/.well-known/`, où Cloudflare valide le certificat.
- Les certificats sont émis et renouvelés par Cloudflare (validation HTTP), sans rien à faire chez Hostinger.
- Jeton d'API de la CI (`github-actions mon-chat-peut`, jetons d'API du compte) : Workers Scripts Write sur le compte, Zone Read et Workers Routes Write sur `pasdansmonfil.fr`.

Avant novembre 2026, le site était servi par le conteneur nginx `website` du VPS, depuis `~/html` (un clone de ce dépôt).
