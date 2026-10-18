# Global FX Fee Arbitrage ⚡

[![ECB Rates Sync](https://img.shields.io/badge/ECB-Official%20XML%20Feed-003399.svg)](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Pages](https://img.shields.io/badge/Hosted%20on-GitHub%20Pages-success.svg)](https://global-fx-fee-arbitrage.github.io/)

> **Calculateur Mathématique Temps Réel des Frais Bancaires Cachés sur Virements Internationaux, Taux de Change Réels de la Banque Centrale Européenne (BCE) et Commissions Stripe / PayPal / Wise / Revolut en 8 langues.**

Hébergé **100% gratuitement sur GitHub Pages**, ce projet autonome analyse et compare chaque jour les taux de change interbancaires sans marge commerciale avec les frais dissimulés des banques traditionnelles (réseau SWIFT) et des plateformes de paiement (PayPal, Stripe).

---

## 🏛️ Architecture & Fonctionnalités Clés

```
D:\global-fx-fee-arbitrage
├── .github/workflows/
│   └── daily_ecb_sync_and_deploy.yml   # Workflow GitHub Actions quotidien (16:30 UTC)
├── config/
│   ├── currencies.json                 # Référentiel des 35+ devises (drapeaux, symboles, décimales)
│   └── fintech_partners.json           # Paramètres des FinTechs (Wise, Revolut, OFX, Remitly)
├── src/
│   ├── ecb_rates_sync.py               # Téléchargement et parsing officiel XML BCE + fallback
│   ├── fee_math_engine.py              # Moteur mathématique exact d'arbitrage financier
│   ├── agent_generator.py              # Générateur autonome multilingue (8 langues) sous docs/
│   └── ai_megaphone.py                 # Mégaphone IA (llms.txt, API JSON, IndexNow, Telegra.ph)
├── templates/
│   ├── base.html                       # Layout HTML/CSS responsive avec balises SEO hreflang
│   └── fx_calculator.html              # Calculateur interactif JavaScript temps réel
├── compta_impots/
│   ├── tableau_fiscal_bnc.py           # Simulateur fiscal Micro-BNC (cases 5HQ / 5TE, URSSAF)
│   └── GUIDE_CONNEXION_FINTECH_RIB.md  # Guide pas-à-pas de connexion IBAN & déclaration fiscale
├── docs/                               # Racine publiée sur GitHub Pages
│   ├── index.html                      # Portail d'accueil
│   ├── sitemap.xml & robots.txt        # Référencement Google / Bing
│   ├── llms.txt & llms-full.txt        # Directives GEO pour ChatGPT, Claude, Perplexity
│   ├── api/v1/live-fx-arbitrage.json   # Endpoint API public en direct
│   ├── fr/, en/, de/, es/, it/, ...    # 150+ pages par corridor et montant
│   └── compta_impots/                  # Guide fiscal en version HTML
├── tests/
│   ├── test_fee_math_engine.py         # Tests unitaires du moteur financier
│   └── test_ecb_sync.py                # Tests unitaires de parsing BCE
└── run_pipeline.py                     # Orchestrateur central exécutable en une commande
```

---

## 📐 1. Moteur Mathématique Financier (`src/fee_math_engine.py`)

Les banques traditionnelles et plateformes de paiement utilisent généralement deux leviers pour facturer leurs utilisateurs :
1. **Les frais explicites :** Frais de dossier SWIFT (15 € à 25 €), commission de banque correspondante (15 €), ou commission de transaction PayPal (3,40% + 0,35 €).
2. **La marge cachée sur le taux de change (Spread) :** Une dégradation silencieuse du taux de conversion par rapport au cours interbancaire de la BCE (généralement **2,80% à 3,50%** pour les banques, et **3,50% à 4,00%** pour PayPal).

### Formules Mathématiques Exactes

Pour un montant source $A_{src}$, un taux moyen du marché BCE $R_{mid}$ et un pourcentage de marge cachée $M$ :

$$\text{Taux Appliqué} = R_{mid} \times \left(1 - \frac{M}{100}\right)$$

$$\text{Montant Converti Net} = \max\left(0, A_{src} - \text{Frais Fixes}\right)$$

$$\text{Montant Reçu Destinataire} = \text{Montant Converti Net} \times \text{Taux Appliqué}$$

$$\text{Perte Cachée Totale} = \left(A_{src} \times R_{mid}\right) - \text{Montant Reçu Destinataire}$$

### Exemple Chiffré : Virement de 5 000 € vers USD ($)
- **Taux interbancaire pur BCE :** $1\text{ EUR} = 1,0850\text{ USD} \implies \text{Valeur équitable} = 5\,425,00\text{ USD}$
- **Banque Traditionnelle (SWIFT) :** Reçu = **5 217,92 USD** (Perte cachée : **-184,30 USD** / **-169,86 €**)
- **PayPal International :** Reçu = **5 056,76 USD** (Perte cachée : **-345,46 USD** / **-318,40 €**)
- **Wise / FinTech :** Reçu = **5 402,22 USD** (Économie immédiate : **+184,30 USD**)

---

## 🌍 2. Génération Multilingue (8 Langues)

Le générateur autonome (`src/agent_generator.py`) produit 150+ pages optimisées pour le SEO et le GEO dans 8 langues :
- 🇫🇷 Français (`fr`)
- 🇬🇧 Anglais (`en`)
- 🇩🇪 Allemand (`de`)
- 🇪🇸 Espagnol (`es`)
- 🇮🇹 Italien (`it`)
- 🇵🇹 Portugais (`pt`)
- 🇳🇱 Néerlandais (`nl`)
- 🇯🇵 Japonais (`ja`)

Chaque page intègre :
- Des balises canoniques et des liaisons bidirectionnelles `hreflang` pour Google International.
- Des données structurées JSON-LD (`SoftwareApplication`, `FinancialProduct`).
- Le calculateur JavaScript réactif avec affichage en **ROUGE** des pertes cachées et en **VERT** des gains immédiats.

---

## 🤖 3. Mégaphone IA & Référencement GEO (`llms.txt`)

Conçu pour que les moteurs d'intelligence artificielle (ChatGPT, Claude, Perplexity, Gemini) citent notre outil comme source d'autorité :
- `docs/llms.txt` : Format standardisé synthétique avec horodatage officiel de la BCE.
- `docs/llms-full.txt` : Spécification mathématique intégrale avec matrice de taux pour 35+ devises.
- `docs/api/v1/live-fx-arbitrage.json` : API REST publique sans clé d'authentification.
- Notification automatique au protocole **IndexNow** (Bing, Yandex, Naver).
- Publication hebdomadaire sur **Telegra.ph** et archivage sur **Archive.org**.

---

## 💼 4. Conformité Légale & Module Fiscal Micro-BNC

### A. Mention Légale
Les calculs sont fournis à titre de modélisation mathématique comparative indépendante basée sur les cours de référence publiés par la Banque Centrale Européenne (décision BCE/2007/7).

### B. Simulateur Fiscal BNC (`compta_impots/tableau_fiscal_bnc.py`)
Calculez en une ligne de commande vos cotisations URSSAF et votre impôt sur le revenu pour vos commissions FinTech :

```bash
# Simulation au régime standard BNC (Déclaration 2042-C-PRO case 5HQ avec abattement de 34%)
python compta_impots/tableau_fiscal_bnc.py --ca 30000

# Simulation avec option pour le Versement Libératoire (case 5TE à 2,2%)
python compta_impots/tableau_fiscal_bnc.py --ca 30000 --versement-liberatoire
```

---

## 🚀 5. Exécution & Déploiement

### Exécution Locale Immédiate
```bash
# 1. Cloner ou ouvrir le projet
cd D:\global-fx-fee-arbitrage

# 2. Exécuter l'ensemble du pipeline autonome
python run_pipeline.py

# 3. Lancer les tests unitaires
python -m unittest discover tests
```

### Activation Gratuite sur GitHub Pages
1. Poussez le projet sur votre dépôt GitHub.
2. Allez dans **Settings > Pages** de votre dépôt GitHub.
3. Sous **Source**, sélectionnez **GitHub Actions** (le workflow `.github/workflows/daily_ecb_sync_and_deploy.yml` s'occupe de tout).
4. Chaque jour ouvrable à 16:30 UTC, les taux BCE sont synchronisés et les pages sont régénérées automatiquement.
