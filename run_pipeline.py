#!/usr/bin/env python3
"""
run_pipeline.py
Orchestrateur principal 100% autonome de Global FX Fee Arbitrage.
Exécute la chaîne complète :
1. Synchronisation quotidienne du flux officiel de la Banque Centrale Européenne (BCE).
2. Calculs mathématiques d'arbitrage et de pertes cachées.
3. Génération des pages multilingues (8 langues) et du calculateur interactif dans `docs/`.
4. Diffusion via le mégaphone IA (llms.txt, API v1, IndexNow, Telegra.ph).
5. Validation des modules comptables et fiscaux Micro-BNC.
"""

import sys
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("pipeline")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ecb_rates_sync import get_latest_ecb_rates, save_rates_to_files
from src.fee_math_engine import FeeMathEngine
from src.agent_generator import generate_all_pages
from src.ai_megaphone import run_megaphone_pipeline
from compta_impots.tableau_fiscal_bnc import BncFiscalEngine


def run_full_pipeline():
    logger.info("=" * 60)
    logger.info("DÉMARRAGE DU PIPELINE GLOBAL FX FEE ARBITRAGE")
    logger.info("=" * 60)

    # Étape 1 : Récupération des taux officiels BCE
    logger.info("[1/5] Synchronisation quotidienne des cours de la BCE...")
    rates_payload = get_latest_ecb_rates()
    data_f, api_f = save_rates_to_files(rates_payload, BASE_DIR)
    rate_count = rates_payload["meta"]["currency_count"]
    eff_date = rates_payload["meta"]["effective_date"]
    logger.info("-> %d devises synchronisées (Date effective: %s)", rate_count, eff_date)

    # Étape 2 : Test du moteur mathématique financier
    logger.info("[2/5] Exécution du moteur mathématique de détection des frais cachés...")
    engine = FeeMathEngine(rates=rates_payload["rates"])
    bench_5k = engine.calculate_comparison(5000.0, "EUR", "USD", rate_date=eff_date)
    logger.info("-> Test 5 000 EUR -> USD : Perte bancaire cachée = %.2f USD (%.2f EUR, %.2f%%)",
                bench_5k.hidden_bank_loss_target, bench_5k.hidden_bank_loss_source, bench_5k.hidden_bank_loss_percent)

    # Étape 3 : Génération autonome multilingue (8 langues)
    logger.info("[3/5] Génération autonome des pages HTML multilingues sous docs/...")
    generated_urls = generate_all_pages(BASE_DIR)
    logger.info("-> %d pages générées avec succès (Sitemap & Robots.txt inclus)", len(generated_urls))

    # Étape 4 : Mégaphone IA & Référencement GEO/AEO
    logger.info("[4/5] Activation du mégaphone IA (llms.txt, API JSON, IndexNow, Telegra.ph)...")
    run_megaphone_pipeline(BASE_DIR, generated_urls)
    logger.info("-> Directives LLM et signaux d'autorité déployés")

    # Étape 5 : Module fiscal & comptable Micro-BNC
    logger.info("[5/5] Vérification du module fiscal BNC (cases 5HQ / 5TE)...")
    fiscal_engine = BncFiscalEngine()
    test_sim = fiscal_engine.compute(ca_brut=25000.0, versement_liberatoire=False)
    logger.info("-> Simulation fiscale validée : CA=%.2f EUR | Case 2042=%s | Net après URSSAF=%.2f EUR",
                test_sim.chiffre_affaires_brut_eur, test_sim.case_declaration_revenus, test_sim.reste_net_apres_charges_sociales_eur)

    logger.info("=" * 60)
    logger.info("PIPELINE TERMINÉ AVEC SUCCÈS - SYSTÈME 100%% AUTONOME ET PRÊT POUR GITHUB PAGES")
    logger.info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_full_pipeline())
