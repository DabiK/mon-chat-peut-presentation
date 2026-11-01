# 🎯 Section "Comment ça marche" - Landing Page

## ✨ Vue d'ensemble

Nouvelle section animée kawaii style workflow, inspirée de `OnboardingStorySlide`, qui présente les 4 étapes clés de l'application en mode interactif et visuel.

---

## 🎨 Design & Style

### **Gradient de fond**

```css
background: linear-gradient(135deg, #fff5f0 0%, #ffe8dd 50%, #ffd4e5 100%);
```

- Harmonisé avec le reste de la landing page
- Emojis décoratifs flottants (✨ 💫)

### **Cards workflow**

- **4 étapes** sous forme de cartes blanches arrondies
- Effet slide-in progressif (animation décalée)
- Hover avec élévation
- Numéro circulaire avec gradient kawaii
- Icône emoji animée (bounce)
- Connecteurs visuels entre les étapes (mobile)

### **Mockup phone animé**

- Écran de téléphone noir avec border-radius 30px
- Encoche supérieure simulée
- 4 contenus différents qui s'animent selon l'étape active
- Animation float 3D perpétuelle

---

## 📱 Les 4 Étapes du Workflow

### **Step 1: Créez le profil 🐱**

- **Titre:** "Créez le profil"
- **Description:** "Ajoutez votre chat avec sa photo, son poids, son âge et ses caractéristiques"
- **Mockup:**
  - Avatar circulaire avec emoji 🐱
  - 3 champs de formulaire avec effet shimmer (loading)
  - Animation pulse sur l'avatar

### **Step 2: Générez son plan 🎯**

- **Titre:** "Générez son plan"
- **Description:** "Un plan personnalisé basé sur 8 critères avec calculs vétérinaires (RER/DER)"
- **Mockup:**
  - Gauge circulaire avec rotation (185 kcal)
  - Liste de 3 critères avec animation expand-width
  - Gradient de couleurs kawaii

### **Step 3: Scannez ses produits 🔍**

- **Titre:** "Scannez ses produits"
- **Description:** "Vérifiez la qualité de ses croquettes et comparez avec 500+ produits"
- **Mockup:**
  - Zone de scan avec bordure dashed pulsante
  - Ligne de scan animée (haut-bas)
  - Code-barres stylisé
  - Badge score vert "85/100" avec bounce

### **Step 4: Suivez son évolution 📊**

- **Titre:** "Suivez son évolution"
- **Description:** "Macros, hydratation, poids — visualisez sa transformation au quotidien"
- **Mockup:**
  - 4 barres de graphique animées (croissance progressive)
  - 2 mini-stats avec gradient bleu-violet
  - Animation growBar avec délais

---

## 🎬 Animations Implémentées

### **CSS Animations**

1. **slideInStep** - Entrée progressive des cartes (0.6s)
2. **pulse** - Pulsation des numéros et badges (2s infini)
3. **bounce** - Rebond des emojis (2s infini)
4. **rotate** - Rotation du numéro actif (2s infini)
5. **shimmer** - Effet de brillance sur les champs (2s infini)
6. **spin** - Rotation du gauge (2s infini)
7. **expandWidth** - Expansion des barres de critères (1s)
8. **scan** - Ligne de scan barcode (2s infini)
9. **growBar** - Croissance des barres de graphique (1s)
10. **float** - Flottement 3D du mockup (4s infini)
11. **fadeInScale** - Apparition des écrans (0.6s)

### **JavaScript Interactif**

- **Auto-cycle:** Les étapes changent automatiquement toutes les 3 secondes
- **Intersection Observer:** L'animation démarre quand la section est visible (30% threshold)
- **Click handlers:** Clic sur une étape pour la voir immédiatement
- **Pause intelligente:** Après un clic, pause de 5s avant de reprendre l'auto-cycle
- **Synchronisation:** Le mockup screen change en sync avec l'étape active

---

## 📐 Responsive Design

### **Mobile (< 968px)**

- Layout vertical 1 colonne
- Connecteurs entre étapes (flèches verticales)
- Mockup centré sous les étapes
- Texte aligné à gauche

### **Desktop (≥ 968px)**

- Grid 2x2 pour les 4 étapes
- Texte centré dans chaque carte
- Flèches horizontales "→" entre steps 1-2 et 3-4
- Mockup plus large (450px)
- Pas de connecteurs verticaux

---

## 🎯 Classes CSS Principales

### **Structure**

- `.how-it-works-section` - Container principal
- `.workflow-container` - Grid des étapes
- `.workflow-step` - Carte individuelle
- `.workflow-mockup` - Container du téléphone
- `.mockup-screen` - Écran du téléphone

### **Composants Step**

- `.step-number` - Badge numéro circulaire
- `.step-icon` - Emoji animé
- `.step-content` - Texte titre + description
- `.step-connector` - Ligne de connexion

### **Mockup Screens**

- `.screen-content` - Container d'un écran (4 au total)
- `.screen-content.active` - Écran actuellement visible

### **Mockup Content**

- `.form-mockup` - Formulaire (Step 1)
- `.gauge-mockup` - Gauge calorique (Step 2)
- `.barcode-mockup` - Scanner barcode (Step 3)
- `.chart-mockup` - Graphique bars (Step 4)

---

## 🔧 Configuration JavaScript

### **Variables clés**

```javascript
const workflowSteps = document.querySelectorAll(".workflow-step");
const mockupScreen = document.getElementById("mockupScreen");
let currentStep = 0;
let workflowInterval;
```

### **Timing**

- **Durée par étape:** 3000ms (3 secondes)
- **Pause après clic:** 5000ms (5 secondes)
- **Threshold viewport:** 0.3 (30% visible)

### **Fonction principale**

```javascript
function activateStep(stepIndex) {
  // 1. Retire .active de toutes les steps
  // 2. Retire .active de tous les screens
  // 3. Ajoute .active à la step courante
  // 4. Ajoute .active au screen correspondant
}
```

---

## 🎨 Palette de Couleurs

### **Gradients utilisés**

- **Step numbers:** `#ff9a76` → `#ffb3d9` (primary → kawaii-pink)
- **Avatar:** `#ffb3d9` → `#d4a5ff` (kawaii-pink → kawaii-purple)
- **Criteria bars:** `#ffcc99` → `#ffb3d9` (accent → kawaii-pink)
- **Score badge:** `#4caf50` → `#45a049` (vert succès)
- **Chart bars:** `#ff9a76` → `#ffb3d9` (primary → kawaii-pink)
- **Stat mini:** `#a5d8ff` → `#d4a5ff` (kawaii-blue → kawaii-purple)

---

## 📊 Hiérarchie des Animations

### **Délais d'entrée (slideInStep)**

1. Step 1: `0.2s`
2. Step 2: `0.4s`
3. Step 3: `0.6s`
4. Step 4: `0.8s`

### **Délais bounce (emojis)**

1. Step 1: `0s`
2. Step 2: `0.2s`
3. Step 3: `0.4s`
4. Step 4: `0.6s`

### **Délais criteria bars**

1. Bar 1: `0s`
2. Bar 2: `0.2s`
3. Bar 3: `0.4s`

### **Délais chart bars**

1. Bar 1: `0s`
2. Bar 2: `0.2s`
3. Bar 3: `0.4s`
4. Bar 4: `0.6s`

---

## 🚀 Intégration avec OnboardingStorySlide

### **Similarités**

- ✅ Structure en 3-4 actes narratifs
- ✅ Animations automatiques avec auto-play
- ✅ Mockups stylisés et animés
- ✅ Palette de couleurs kawaii cohérente
- ✅ Transitions fluides entre états
- ✅ Bouton skip/pause disponible (clic manuel)

### **Différences**

- 🔄 Landing page: Auto-cycle infini (pas de fin)
- 🔄 OnboardingStorySlide: Progression linéaire avec bouton "Suivant"
- 🔄 Landing page: Click pour voir une étape spécifique
- 🔄 OnboardingStorySlide: Skip pour sauter à la fin

---

## 🎯 Points d'Attention

### **Performance**

- ✅ Animations CSS optimisées (transform/opacity)
- ✅ Intersection Observer pour activer uniquement quand visible
- ✅ Interval cleared quand hors viewport
- ✅ Pas de manipulation DOM excessive

### **Accessibilité**

- ⚠️ À ajouter: `aria-label` sur les étapes
- ⚠️ À ajouter: Indication visuelle de l'étape active pour lecteurs d'écran
- ✅ Contrastes de couleurs respectés
- ✅ Tailles de police lisibles

### **SEO**

- ✅ Titres sémantiques (h2, h3)
- ✅ Texte descriptif complet
- ✅ Pas de contenu caché important

---

## 📱 Tests Recommandés

### **Navigateurs**

- [ ] Chrome/Edge (animations transform)
- [ ] Firefox (gradient rendering)
- [ ] Safari (backdrop-filter support)
- [ ] Mobile Safari (touch events)

### **Devices**

- [ ] Mobile portrait (320px-480px)
- [ ] Mobile landscape (480px-768px)
- [ ] Tablet (768px-968px)
- [ ] Desktop (968px+)

### **Interactions**

- [ ] Auto-cycle fonctionne en arrivant sur section
- [ ] Clic sur step change immédiatement
- [ ] Pause après clic manuel (5s)
- [ ] Reprise auto-cycle après pause
- [ ] Arrêt quand section hors viewport

---

## 🎨 Customisation Facile

### **Changer la durée d'une étape**

```javascript
}, 3000); // ← Modifier ici (en millisecondes)
```

### **Changer la pause après clic**

```javascript
setTimeout(() => {
  // ...
}, 5000); // ← Modifier ici
```

### **Ajouter une 5ème étape**

1. Ajouter une div `.workflow-step[data-step="5"]` dans HTML
2. Ajouter un `.screen-content[data-screen="5"]` dans mockup
3. Changer `% 4` en `% 5` dans le JavaScript
4. Ajouter le délai d'animation CSS

---

## 💡 Améliorations Futures (Optionnel)

### **V2 Ideas**

- 🎯 Indicateurs de progression (dots) sous le mockup
- 🎯 Boutons prev/next manuels
- 🎯 Animation de transition entre screens plus sophistiquée
- 🎯 Parallax sur les emojis décoratifs
- 🎯 Sound effects subtils (optionnel)
- 🎯 Intégration de vraies captures d'écran de l'app

### **Librairies externes (si besoin)**

Actuellement **100% vanilla** (pas de dépendances), mais si besoin :

- **GSAP:** Animations plus complexes
- **Lottie:** Animations vectorielles
- **Intersection Observer Polyfill:** Support IE11
- **ScrollMagic:** Scroll-triggered animations avancées

---

**Status:** ✅ Implémenté et prêt à l'emploi  
**Code:** 100% vanilla JS + CSS (pas de dépendances externes)  
**Compatible:** Tous navigateurs modernes  
**Responsive:** Mobile, tablet, desktop  
**Style:** Kawaii, cohérent avec le reste de la landing page
