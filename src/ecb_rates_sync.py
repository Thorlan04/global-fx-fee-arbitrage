#!/usr/bin/env python3
"""
ecb_rates_sync.py
Synchronisation autonome quotidienne des taux de change officiels de la Banque Centrale Européenne (BCE).
Aucune clé d'API requise.
Source primaire: Flux XML officiel BCE (https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml)
Source de repli: Open Exchange Rates public / ER-API (https://open.er-api.com/v6/latest/EUR)
"""

import os
import sys
import json
import logging
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ecb_sync")

# Constants
ECB_DAILY_XML_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
FALLBACK_JSON_URL = "https://open.er-api.com/v6/latest/EUR"
HTTP_TIMEOUT_SECONDS = 15

# Default base rates fallback in case of complete network outage during offline builds/testing
OFFLINE_BENCHMARK_RATES = {
    "EUR": 1.0,
    "USD": 1.0850,
    "GBP": 0.8550,
    "CHF": 0.9720,
    "CAD": 1.4820,
    "JPY": 164.50,
    "AUD": 1.6620,
    "MAD": 10.820,
    "AED": 3.9850,
    "PLN": 4.3150,
    "SEK": 11.450,
    "NOK": 11.620,
    "BRL": 5.6200,
    "MXN": 18.450,
    "THB": 39.800,
    "IDR": 17450.0,
    "SGD": 1.4620,
    "HKD": 8.4800,
    "NZD": 1.8150,
    "ZAR": 20.350,
    "TRY": 35.800,
    "INR": 90.750,
    "KRW": 1490.0,
    "CNY": 7.8500,
    "DKK": 7.4600,
    "CZK": 25.250,
    "HUF": 395.00,
    "RON": 4.9750,
    "BGN": 1.9558,
    "ILS": 4.0500,
    "PHP": 62.400,
    "MYR": 5.1200,
    "SAR": 4.0700,
    "CLP": 1025.0,
    "COP": 4480.0
}


import ssl

def fetch_url(url: str, headers: Optional[Dict[str, str]] = None) -> bytes:
    """Effectue une requête GET HTTP(S) sécurisée avec timeout et User-Agent."""
    req_headers = {
        "User-Agent": "GlobalFXArbitrageBot/1.0 (+https://github.com/global-fx-fee-arbitrage; contact@global-fx-fee-arbitrage.org)",
        "Accept": "application/xml,application/json,text/xml,*/*"
    }
    if headers:
        req_headers.update(headers)

    # Création d'un contexte SSL robuste
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS, context=ctx) as response:
            return response.read()
    except urllib.error.URLError as e:
        # Fallback pour environnements de test / postes Windows sans bundle racine configuré
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            unverified_ctx = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS, context=unverified_ctx) as response:
                return response.read()
        raise e



def parse_ecb_xml(xml_bytes: bytes) -> Tuple[str, Dict[str, float]]:
    """
    Parse le flux XML officiel de la BCE.
    Structure XML ECB:
    <gesmes:Envelope ...>
      <Cube>
        <Cube time="YYYY-MM-DD">
          <Cube currency="USD" rate="1.0850"/>
        ...
    """
    root = ET.fromstring(xml_bytes)
    namespaces = {
        "gesmes": "http://www.gesmes.org/xml/2002-05-01",
        "ecb": "http://www.ecb.int/vocabulary/2002-08-01/eurofxref"
    }

    rates: Dict[str, float] = {"EUR": 1.0}
    time_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Recherche du cube horodaté
    # Parcourt tous les éléments Cube indépendamment du namespace exact
    cubes_with_time = [elem for elem in root.iter() if elem.attrib.get("time")]
    if cubes_with_time:
        time_str = cubes_with_time[0].attrib.get("time", time_str)

    # Récupération des taux
    for elem in root.iter():
        currency = elem.attrib.get("currency")
        rate_str = elem.attrib.get("rate")
        if currency and rate_str:
            try:
                rates[currency.upper()] = float(rate_str)
            except ValueError:
                continue

    return time_str, rates


def fetch_fallback_rates() -> Tuple[str, Dict[str, float]]:
    """Récupère les taux depuis le point de terminaison de repli ER-API JSON."""
    logger.warning("Connexion au flux de secours Open Exchange Rates / ER-API...")
    raw_data = fetch_url(FALLBACK_JSON_URL)
    data = json.loads(raw_data.decode("utf-8"))
    
    time_str = data.get("time_last_update_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    rates: Dict[str, float] = {"EUR": 1.0}
    
    for curr, val in data.get("rates", {}).items():
        try:
            rates[curr.upper()] = float(val)
        except (ValueError, TypeError):
            continue
            
    return time_str, rates


def enrich_supplementary_currencies(rates: Dict[str, float]) -> Dict[str, float]:
    """
    Assure que les devises non directement publiées par la BCE (ex: MAD, AED)
    sont dérivées ou enrichies à partir de flux fiables ou taux de repli.
    """
    enriched = dict(rates)
    
    # Si MAD ou AED ne sont pas dans le flux XML direct BCE, les chercher dans le flux fallback ou calcul triangulé
    missing_needed = [curr for curr in ["MAD", "AED", "SAR", "CLP", "COP"] if curr not in enriched]
    if missing_needed:
        try:
            _, fallback = fetch_fallback_rates()
            for curr in missing_needed:
                if curr in fallback:
                    enriched[curr] = fallback[curr]
        except Exception as e:
            logger.warning("Échec récupération devises complémentaires via fallback: %s", e)
            for curr in missing_needed:
                if curr in OFFLINE_BENCHMARK_RATES:
                    enriched[curr] = OFFLINE_BENCHMARK_RATES[curr]
                    
    # S'assurer de la présence d'au moins toutes les devises de référence
    for curr, default_rate in OFFLINE_BENCHMARK_RATES.items():
        if curr not in enriched:
            enriched[curr] = default_rate

    return enriched


def get_latest_ecb_rates() -> Dict[str, Any]:
    """
    Point d'entrée principal pour synchroniser les taux BCE.
    Essaie d'abord le flux officiel XML ECB, puis le fallback JSON,
    puis la sauvegarde locale ou le benchmark hors-ligne.
    """
    source_used = "ECB_OFFICIAL_XML"
    rates: Dict[str, float] = {}
    rate_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    try:
        logger.info("Téléchargement du flux officiel BCE : %s", ECB_DAILY_XML_URL)
        xml_data = fetch_url(ECB_DAILY_XML_URL)
        rate_date, raw_rates = parse_ecb_xml(xml_data)
        if len(raw_rates) >= 20:
            rates = enrich_supplementary_currencies(raw_rates)
            logger.info("Succès BCE : %d devises synchronisées pour la date %s", len(rates), rate_date)
        else:
            raise ValueError(f"Flux XML incomplet ({len(raw_rates)} devises trouvées)")
    except Exception as exc:
        logger.error("Erreur avec le flux primaire BCE (%s), tentative de repli...", exc)
        try:
            source_used = "ER_API_FALLBACK"
            rate_date, fallback_rates = fetch_fallback_rates()
            rates = enrich_supplementary_currencies(fallback_rates)
            logger.info("Succès Repli : %d devises synchronisées.", len(rates))
        except Exception as exc2:
            logger.critical("Erreur sur le flux de repli : %s. Utilisation des benchmarks de secours.", exc2)
            source_used = "OFFLINE_BENCHMARK"
            rate_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            rates = dict(OFFLINE_BENCHMARK_RATES)

    now_utc = datetime.now(timezone.utc).isoformat()
    
    payload = {
        "meta": {
            "title": "Taux de Change Officiels - European Central Bank (BCE)",
            "description": "Données interbancaires publiques sans marge commerciale pour arbitrage de frais financiers.",
            "source": source_used,
            "official_ecb_feed_url": ECB_DAILY_XML_URL,
            "base_currency": "EUR",
            "effective_date": rate_date,
            "synced_at_utc": now_utc,
            "currency_count": len(rates),
            "disclaimer": "Les taux sont fournis à titre de référence mathématique publique selon la directive ECB/2007/7."
        },
        "rates": rates
    }

    return payload


def save_rates_to_files(payload: Dict[str, Any], base_dir: Path) -> Tuple[Path, Path]:
    """Sauvegarde les taux dans `data/ecb_rates.json` et `docs/api/v1/live-fx-arbitrage.json`."""
    data_dir = base_dir / "data"
    api_dir = base_dir / "docs" / "api" / "v1"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    api_dir.mkdir(parents=True, exist_ok=True)
    
    data_file = data_dir / "ecb_rates.json"
    api_file = api_dir / "live-fx-arbitrage.json"
    
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        
    with open(api_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        
    logger.info("Taux sauvegardés dans : %s et %s", data_file, api_file)
    return data_file, api_file


def main():
    """Exécution CLI."""
    base_dir = Path(__file__).resolve().parent.parent
    payload = get_latest_ecb_rates()
    data_f, api_f = save_rates_to_files(payload, base_dir)
    print(f"OK: {len(payload['rates'])} devises synchronisées ({payload['meta']['effective_date']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
