#!/usr/bin/env python3
"""
tableau_fiscal_bnc.py
Tableau de bord fiscal et comptable pour Micro-Entreprise BNC (Prestations de services intellectuelles / Affiliation FinTech).
Gère les déclarations URSSAF, l'abattement forfaitaire BNC de 34% (Art. 102 ter du CGI),
les cases 5HQ (sans versement libératoire) et 5TE (avec versement libératoire de 2,2%),
les seuils de franchise en base de TVA et la Cotisation Foncière des Entreprises (CFE).
"""

import sys
import json
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional


def round_cur(val: float) -> float:
    return float(Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


@dataclass
class BncTaxSimulation:
    chiffre_affaires_brut_eur: float
    regime_imposition: str  # "5HQ_BAREME_PROGRESSIF" ou "5TE_VERSEMENT_LIBERATOIRE"
    taux_urssaf_pct: float
    taux_formation_pro_pct: float
    versement_liberatoire_pct: float
    
    # Cotisations sociales et formation
    cotisations_urssaf_eur: float
    contribution_formation_pro_eur: float
    total_charges_sociales_eur: float
    
    # Fiscalité sur le revenu (Impôt sur le Revenu)
    impot_versement_liberatoire_eur: float
    abattement_forfaitaire_bnc_pct: float
    abattement_forfaitaire_bnc_eur: float
    revenu_net_imposable_bareme_eur: float
    
    # Reste net en poche avant impôt sur le revenu global
    reste_net_apres_charges_sociales_eur: float
    reste_net_final_apres_prelevements_eur: float
    pourcentage_prelevements_total_pct: float
    
    # Diagnostic seuils & plafonds
    plafond_micro_bnc_eur: float
    seuil_franchise_tva_eur: float
    depassement_plafond_micro: bool
    depassement_franchise_tva: bool
    
    # Case exacte à renseigner sur la 2042-C-PRO
    case_declaration_revenus: str
    montant_a_declarer_impots_eur: float
    note_explicative: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BncFiscalEngine:
    """Moteur de calcul fiscal certifié Micro-BNC."""

    PLAFOND_MICRO_BNC_2026 = 77700.00  # Seuil annuel du régime micro-BNC
    SEUIL_TVA_BASE_2026 = 36800.00      # Seuil franchise en base TVA
    SEUIL_TVA_MAJORÉ_2026 = 39100.00    # Seuil de tolérance majoré
    ABATTEMENT_BNC_CGI = 34.00          # 34% d'abattement forfaitaire de frais (min 305 €)
    TAUX_URSSAF_BNC_STANDARD = 21.10    # Taux cotisations sociales BNC standard
    TAUX_CFP_BNC = 0.20                 # Contribution formation professionnelle (0,2% pour BNC)
    TAUX_VERSEMENT_LIBERATOIRE = 2.20   # Versement libératoire de l'IR pour BNC (2,2%)

    def __init__(self, acre: bool = False):
        self.acre = acre
        # Si ACRE active (1ère année), taux URSSAF réduit de 50%
        self.taux_urssaf = 10.60 if acre else self.TAUX_URSSAF_BNC_STANDARD

    def compute(self, ca_brut: float, versement_liberatoire: bool = False) -> BncTaxSimulation:
        ca = max(0.0, float(ca_brut))
        
        # Charges sociales
        urssaf_amt = round_cur(ca * (self.taux_urssaf / 100.0))
        cfp_amt = round_cur(ca * (self.TAUX_CFP_BNC / 100.0))
        total_social = round_cur(urssaf_amt + cfp_amt)

        # Fiscalité
        abattement_amt = round_cur(max(305.0 if ca > 0 else 0.0, ca * (self.ABATTEMENT_BNC_CGI / 100.0)))
        net_imposable_bareme = round_cur(max(0.0, ca - abattement_amt))

        if versement_liberatoire:
            regime = "5TE_VERSEMENT_LIBERATOIRE"
            ir_liberatoire = round_cur(ca * (self.TAUX_VERSEMENT_LIBERATOIRE / 100.0))
            net_final = round_cur(ca - total_social - ir_liberatoire)
            case_impots = "5TE"
            pct_total = round_cur(((total_social + ir_liberatoire) / ca * 100.0) if ca > 0 else 0.0)
            note = "Option Versement Libératoire : l'impôt est définitivement payé chaque mois/trimestre avec l'URSSAF (2,2%). À reporter case 5TE."
        else:
            regime = "5HQ_BAREME_PROGRESSIF"
            ir_liberatoire = 0.0
            net_final = round_cur(ca - total_social)
            case_impots = "5HQ"
            pct_total = round_cur((total_social / ca * 100.0) if ca > 0 else 0.0)
            note = f"Régime standard BNC : l'administration applique automatiquement l'abattement forfaitaire de 34%. Base taxable au barème progressif de l'IR = {net_imposable_bareme} €. À reporter case 5HQ."

        net_apres_charges = round_cur(ca - total_social)

        return BncTaxSimulation(
            chiffre_affaires_brut_eur=round_cur(ca),
            regime_imposition=regime,
            taux_urssaf_pct=self.taux_urssaf,
            taux_formation_pro_pct=self.TAUX_CFP_BNC,
            versement_liberatoire_pct=self.TAUX_VERSEMENT_LIBERATOIRE if versement_liberatoire else 0.0,
            cotisations_urssaf_eur=urssaf_amt,
            contribution_formation_pro_eur=cfp_amt,
            total_charges_sociales_eur=total_social,
            impot_versement_liberatoire_eur=ir_liberatoire,
            abattement_forfaitaire_bnc_pct=self.ABATTEMENT_BNC_CGI,
            abattement_forfaitaire_bnc_eur=abattement_amt,
            revenu_net_imposable_bareme_eur=net_imposable_bareme,
            reste_net_apres_charges_sociales_eur=net_apres_charges,
            reste_net_final_apres_prelevements_eur=net_final,
            pourcentage_prelevements_total_pct=pct_total,
            plafond_micro_bnc_eur=self.PLAFOND_MICRO_BNC_2026,
            seuil_franchise_tva_eur=self.SEUIL_TVA_BASE_2026,
            depassement_plafond_micro=(ca > self.PLAFOND_MICRO_BNC_2026),
            depassement_franchise_tva=(ca > self.SEUIL_TVA_BASE_2026),
            case_declaration_revenus=case_impots,
            montant_a_declarer_impots_eur=round_cur(ca),  # Sur la 2042, on déclare toujours le CA BRUT ENTIER !
            note_explicative=note
        )

    def print_report(self, sim: BncTaxSimulation):
        """Affiche un rapport clair et pédagogique pour l'entrepreneur."""
        print("=" * 70)
        print("TABLEAU DE BORD FISCAL & COMPTABLE MICRO-ENTREPRISE BNC (2026)")
        print("Activités : Affiliation FinTech, Commissions Partenaires, Conseil")
        print("=" * 70)
        print(f"Chiffre d'Affaires Brut Encaissé      : {sim.chiffre_affaires_brut_eur:,.2f} €")
        print("-" * 70)
        print("1. CHARGES SOCIALES (URSSAF & FORMATION PROFESSIONNELLE) :")
        print(f"   - Taux Cotisations Sociales URSSAF : {sim.taux_urssaf_pct:.1f}%")
        print(f"   - Montant Cotisations URSSAF       : {sim.cotisations_urssaf_eur:,.2f} €")
        print(f"   - Contribution Formation (CFP 0.2%): {sim.contribution_formation_pro_eur:,.2f} €")
        print(f"   => TOTAL CHARGES SOCIALES          : {sim.total_charges_sociales_eur:,.2f} €")
        print(f"   => NET EN POCHE APRÈS URSSAF       : {sim.reste_net_apres_charges_sociales_eur:,.2f} €")
        print("-" * 70)
        print("2. IMPÔT SUR LE REVENU & DÉCLARATION CERFA 2042-C-PRO :")
        print(f"   - Régime sélectionné               : {sim.regime_imposition}")
        print(f"   - Case exacte sur la déclaration   : [ {sim.case_declaration_revenus} ]")
        print(f"   - Montant brut exact à inscrire    : {sim.montant_a_declarer_impots_eur:,.2f} €")
        if sim.regime_imposition == "5TE_VERSEMENT_LIBERATOIRE":
            print(f"   - Impôt Libératoire (2,2% direct)  : {sim.impot_versement_liberatoire_eur:,.2f} €")
            print(f"   => NET FINAL APRÈS TOUT PRÉLÈVEMENT: {sim.reste_net_final_apres_prelevements_eur:,.2f} € ({100 - sim.pourcentage_prelevements_total_pct:.1f}% du CA net)")
        else:
            print(f"   - Abattement forfaitaire BNC (34%) : -{sim.abattement_forfaitaire_bnc_eur:,.2f} €")
            print(f"   - Revenu net imposable au barème   : {sim.revenu_net_imposable_bareme_eur:,.2f} € (66% du CA)")
            print(f"   => NET DISPONIBLE AVANT IR GLOBAL  : {sim.reste_net_final_apres_prelevements_eur:,.2f} €")
        print("-" * 70)
        print("3. VÉRIFICATION DES SEUILS LÉGAUX :")
        tva_status = "[ATTENTION] Seuil franchise TVA depasse (36 800 EUR) !" if sim.depassement_franchise_tva else "[OK] Sous le seuil de franchise en base de TVA (Art. 293 B du CGI)"
        micro_status = "[DEPASSEMENT] Plafond micro depasse (77 700 EUR) !" if sim.depassement_plafond_micro else "[OK] Eligible au regime fiscal de la Micro-Entreprise"
        print(f"   - Statut TVA : {tva_status}")
        print(f"   - Statut Micro-BNC : {micro_status}")

        print("=" * 70)
        print(f"Note : {sim.note_explicative}")
        print("=" * 70)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Simulateur fiscal Micro-Entreprise BNC 2026")
    parser.add_argument("--ca", type=float, default=24000.0, help="Chiffre d'affaires brut annuel en euros (défaut: 24 000 €)")
    parser.add_argument("--versement-liberatoire", action="store_true", help="Activer l'option du versement libératoire de l'impôt (2,2%, case 5TE)")
    parser.add_argument("--acre", action="store_true", help="Bénéficiaire de l'ACRE (cotisations URSSAF réduites de 50%)")
    parser.add_argument("--json", action="store_true", help="Sortie au format JSON pour intégration API/Script")

    args = parser.parse_args()

    engine = BncFiscalEngine(acre=args.acre)
    sim = engine.compute(ca_brut=args.ca, versement_liberatoire=args.versement_liberatoire)

    if args.json:
        print(json.dumps(sim.to_dict(), indent=2, ensure_ascii=False))
    else:
        engine.print_report(sim)

    return 0


if __name__ == "__main__":
    sys.exit(main())
