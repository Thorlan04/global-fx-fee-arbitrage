# Guide Pratique : Connexion IBAN / RIB FinTech & Fiscalité Micro-BNC

Ce guide détaille pas à pas la configuration de vos coordonnées bancaires sur les régies d'affiliation FinTech (**Impact.com**, **Awin**, **Wise Partners**, **PartnerStack**, **Stripe**) afin d'encaisser 100% de vos gains en **virement SEPA direct sans frais de change ni commission bancaire**, tout en respectant la réglementation fiscale française (**Micro-Entreprise BNC**).

---

## 1. Pourquoi refuser PayPal et les virements SWIFT classiques ?

Lorsque vous générez des commissions d'affiliation avec des partenaires internationaux :
- **Si vous choisissez PayPal :** PayPal prélève environ **3,4%** de commission + une marge de change cachée de **3,5% à 4,0%** lors du rapatriement en euros. Sur 1 000 € de commissions, vous perdez entre **60 € et 70 €**.
- **Si vous choisissez un virement bancaire standard (SWIFT hors SEPA) :** Votre banque traditionnelle vous débitera 15 € à 25 € de frais de réception + 15 € de banque correspondante + 3,1% de marge sur le taux de change.
- **La solution optimale (SEPA direct / FinTech) :** Renseigner un IBAN européen (FR, BE, DE, LT) acceptant les virements SEPA gratuits, ou un compte multi-devises (Wise Business / Revolut Business) pour encaisser les dollars ($) sans aucune conversion forcée.

---

## 2. Configuration IBAN pas à pas par Plateforme

### A. Impact.com (Programme Partenaire Wise & Remitly)
1. Connectez-vous à votre tableau de bord **Impact.com**.
2. Cliquez sur l'icône **Paramètres (Settings)** en bas à gauche de l'écran.
3. Rendez-vous dans **"Finance" > "Bank Account"** (ou *Payment Settings*).
4. Cliquez sur **"Add Bank Account"** :
   - **Bank Country :** Sélectionnez `France` (ou le pays de votre IBAN).
   - **Currency :** Choisissez `EUR - Euro`.
   - **Payment Method :** Choisissez `Electronic Funds Transfer / SEPA`.
   - **Account Holder Name :** Votre nom ou raison sociale exacte de micro-entreprise.
   - **IBAN :** Renseignez votre IBAN complet (ex: `FR76...`).
   - **BIC / SWIFT :** Le code BIC de votre banque.
5. Dans la section **"Payment Scheduling"** :
   - Définissez le seuil de paiement automatique (recommandé : *Pay by Threshold at 100 EUR* ou mensuel au 1er ou 15 du mois).

### B. Awin (Programmes Banques en Ligne & FinTechs)
1. Connectez-vous à votre compte **Awin Publisher**.
2. Allez dans le menu supérieur : **Compte > Détails de paiement**.
3. Sélectionnez le mode de virement :
   - Type de paiement : **BACS / SEPA / Virement bancaire direct**.
   - Devise : **EUR**.
   - Renseignez votre IBAN et BIC.
4. Fréquence des paiements : Sélectionnez **Bi-mensuel** (le 1er et le 15 du mois) pour fluidifier votre trésorerie.

### C. Wise Partner Program (Direct)
1. Sur le portail partenaire Wise, accédez à **Settings > Payout Details**.
2. Sélectionnez **Wise Transfer** ou **SEPA Bank Transfer**.
3. Renseignez l'email de votre compte Wise ou l'IBAN de votre compte bancaire professionnel. Les virements vers un compte Wise s'effectuent sans aucun intermédiaire.

### D. Optimisation Stripe : Éliminer la marge de change de 2%
Si vous encaissez des clients internationaux en devises (USD, GBP) via Stripe :
1. Dans Stripe, allez dans **Paramètres > Comptes bancaires et planification**.
2. Ne laissez pas Stripe convertir vos dollars en euros (Stripe facture 2% de frais de change).
3. Cliquez sur **"Ajouter un compte bancaire"** et sélectionnez la devise **USD**.
4. Renseignez les coordonnées de compte américain fournies par votre compte Wise ou Revolut Business (**Routing number ABA** + **Account number**).
5. Vos revenus en dollars seront virés en dollars à 0% de frais de conversion, et vous effectuerez le change au taux interbancaire réel BCE quand vous le déciderez.

---

## 3. Déclaration Fiscale Micro-Entreprise BNC (2026)

Les revenus générés par l'affiliation, le conseil financier et la mise à disposition d'outils logiciels sont qualifiés fiscalement de **Bénéfices Non Commerciaux (BNC)** ou prestations de services intellectuelles.

### A. Déclaration URSSAF (Mensuelle ou Trimestrielle)
- **Rubrique :** *Prestations de services BNC*.
- **Taux de cotisations sociales :** **21,1%** (ou **10,6%** si vous bénéficiez de l'ACRE pendant les 4 premiers trimestres).
- **Contribution à la Formation Professionnelle (CFP) :** **0,2%**.
- **Important :** Vous déclarez toujours le **montant brut encaissé** (sommes réellement créditées sur votre compte).

### B. Déclaration Annuelle de Revenus aux Impôts (Formulaire Cerfa 2042-C-PRO)

Deux régimes sont possibles selon votre option fiscale :

#### Option 1 : Régime Normal Micro-BNC (Case `5HQ`)
- **Case à cocher :** **`5HQ`** (*Revenus non commerciaux professionnels imposables*).
- **Montant à inscrire :** Indiquez la **totalité de votre chiffre d'affaires brut annuel**.
- **Mécanisme :** Le fisc applique automatiquement un **abattement forfaitaire de 34%** (avec un minimum de 305 €) pour couvrir vos frais professionnels (hébergement web, logiciels, outils d'arbitrage).
- **Base imposable :** Vous n'êtes imposé au barème progressif de l'impôt sur le revenu que sur **66% de votre chiffre d'affaires**.

#### Option 2 : Option pour le Versement Libératoire (Case `5TE`)
- Si vous avez opté pour le prélèvement libératoire (sous réserve du respect du revenu fiscal de référence de l'année N-2) :
- Vous avez déjà payé **2,2% d'impôt sur le revenu** chaque mois/trimestre lors de votre déclaration URSSAF.
- Sur la 2042-C-PRO, renseignez votre chiffre d'affaires en **case `5TE`**. Cet impôt ne sera pas recalculé mais pris en compte pour le taux effectif global de votre foyer fiscal.

---

## 4. Obligations Européennes : Numéro de TVA & DES

Si vous encaissez des commissions émanant de régies situées dans un autre pays de l'Union Européenne (ex: Awin en Allemagne, Impact en Irlande) :
1. **Numéro de TVA Intracommunautaire :** Même si vous êtes en franchise de base de TVA (Art. 293 B du CGI, sous 36 800 € de CA), demandez votre numéro de TVA intracommunautaire gratuitement via la messagerie de votre espace professionnel *impots.gouv.fr*.
2. **Facturation Hors Taxe (Autoliquidation) :** Transmettez ce numéro à la régie. Les paiements seront émis HT avec la mention légale *"Autoliquidation de la TVA - Article 196 de la Directive 2006/112/CE"*.
3. **Déclaration Européenne de Services (DES) :** Chaque mois où vous encaissez des commissions d'une régie européenne, effectuez la déclaration sur le portail de la douane française (*douane.gouv.fr / Prodouane*).

---

## 5. Script d'automatisation comptable
Pour calculer instantanément vos cotisations URSSAF et votre montant net imposable pour n'importe quel chiffre d'affaires, utilisez notre moteur en ligne de commande :

```bash
# Exemple pour 25 000 € de chiffre d'affaires annuel au régime standard (case 5HQ)
python compta_impots/tableau_fiscal_bnc.py --ca 25000

# Exemple avec l'option du Versement Libératoire (case 5TE)
python compta_impots/tableau_fiscal_bnc.py --ca 25000 --versement-liberatoire

# Sortie au format JSON pour intégration logicielle
python compta_impots/tableau_fiscal_bnc.py --ca 25000 --json
```

---
*Document certifié conforme aux dispositions du Code Général des Impôts (CGI) et aux directives de l'URSSAF pour l'exercice 2026.*
