# Mon chat peut ? · site de présentation

Landing page de l'app [Mon chat peut ?](https://play.google.com/store/apps/details?id=com.dabik.monchatpeut), en ligne sur https://mon-chat-peut.com (français) et https://mon-chat-peut.com/en/ (anglais).

## Modifier la page

Les pages `index.html` et `en/index.html` sont générées. On modifie les sources dans `src/`, puis on régénère :

```bash
python3 build.py
```

- `src/template.html` : le balisage, avec des clés `{{nom}}`
- `src/i18n/fr.json` et `src/i18n/en.json` : les textes et les aliments de la démo (mêmes clés dans les deux fichiers)
- `src/styles.css` et `src/app.js` : intégrés dans chaque page au build, pour éviter des requêtes bloquantes
- `img/` : illustrations en WebP, images de partage `og-fr.png` et `og-en.png`
- `assets/fonts/` : Gluten, Figtree et DM Mono, hébergées ici (licence SIL OFL)

`build.py` régénère aussi `sitemap.xml`, puis recopie dans `dist/` tout ce qui est publié : les pages, `img/`, `assets/fonts/`, les icônes, `robots.txt`, `sitemap.xml`, les pages légales et `_headers`. `src/`, les notes `.md` et `build.py` n'y vont pas. `dist/` n'est pas versionné.

Les pages légales (`privacy-policy.html`, `terms-of-service.html`, `user-rights.html`) sont écrites à la main. Cloudflare les sert sans l'extension (`/privacy-policy`) ; les anciennes adresses en `.html` redirigent vers les nouvelles.

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
- Dans la zone `pasdansmonfil.fr` : `mon-chat-peut-saas` est un enregistrement AAAA `100::` proxifié, qui ne sert que de cible ; la route `mon-chat-peut.com/*` envoie le domaine vers le Worker (`wrangler.toml`) ; une règle de redirection envoie `www.mon-chat-peut.com` vers `https://mon-chat-peut.com` en 301.
- Les certificats sont émis et renouvelés par Cloudflare (validation HTTP).
