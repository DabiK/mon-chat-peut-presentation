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

`build.py` régénère aussi `sitemap.xml`. Les pages légales (`privacy-policy.html`, `terms-of-service.html`, `user-rights.html`) sont écrites à la main.

## Déployer

Le site est servi tel quel par le conteneur nginx `website` du VPS, depuis le dossier `~/html`, qui est un clone de ce dépôt.
