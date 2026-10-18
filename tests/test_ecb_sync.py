#!/usr/bin/env python3
"""
Unit tests for ecb_rates_sync.py
"""

import unittest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ecb_rates_sync import parse_ecb_xml, enrich_supplementary_currencies, OFFLINE_BENCHMARK_RATES


class TestEcbRatesSync(unittest.TestCase):

    def test_parse_ecb_xml(self):
        sample_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-05-01" xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">
    <Cube>
        <Cube time="2026-10-16">
            <Cube currency="USD" rate="1.0850"/>
            <Cube currency="GBP" rate="0.8550"/>
            <Cube currency="CHF" rate="0.9720"/>
            <Cube currency="JPY" rate="164.50"/>
        </Cube>
    </Cube>
</gesmes:Envelope>"""
        eff_date, rates = parse_ecb_xml(sample_xml)
        self.assertEqual(eff_date, "2026-10-16")
        self.assertEqual(rates["EUR"], 1.0)
        self.assertEqual(rates["USD"], 1.0850)
        self.assertEqual(rates["GBP"], 0.8550)
        self.assertEqual(rates["CHF"], 0.9720)
        self.assertEqual(rates["JPY"], 164.50)

    def test_enrich_supplementary_currencies(self):
        partial_rates = {"EUR": 1.0, "USD": 1.0850}
        enriched = enrich_supplementary_currencies(partial_rates)
        self.assertIn("MAD", enriched)
        self.assertIn("AED", enriched)
        self.assertIn("GBP", enriched)
        self.assertGreater(enriched["MAD"], 0)


if __name__ == "__main__":
    unittest.main()
