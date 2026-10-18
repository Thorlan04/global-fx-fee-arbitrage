#!/usr/bin/env python3
"""
Unit tests for fee_math_engine.py
"""

import unittest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.fee_math_engine import FeeMathEngine, quantize_currency


class TestFeeMathEngine(unittest.TestCase):

    def setUp(self):
        self.mock_rates = {
            "EUR": 1.0,
            "USD": 1.1000,
            "GBP": 0.8500,
            "CHF": 0.9500,
            "JPY": 160.00
        }
        self.engine = FeeMathEngine(rates=self.mock_rates)

    def test_mid_market_rate_calculation(self):
        # EUR to USD
        self.assertAlmostEqual(self.engine.get_mid_market_rate("EUR", "USD"), 1.1000, places=4)
        # USD to EUR
        self.assertAlmostEqual(self.engine.get_mid_market_rate("USD", "EUR"), 1.0 / 1.1000, places=4)
        # Cross-rate: USD to GBP = (EUR->GBP) / (EUR->USD) = 0.85 / 1.10
        expected_cross = 0.8500 / 1.1000
        self.assertAlmostEqual(self.engine.get_mid_market_rate("USD", "GBP"), expected_cross, places=4)
        # Same currency
        self.assertEqual(self.engine.get_mid_market_rate("EUR", "EUR"), 1.0)

    def test_quantize_currency(self):
        self.assertEqual(quantize_currency(123.456, 2), 123.46)
        self.assertEqual(quantize_currency(123.454, 2), 123.45)
        self.assertEqual(quantize_currency(123.4, 0), 123.0)

    def test_bank_loss_comparison(self):
        # Pour 5000 EUR vers USD
        res = self.engine.calculate_comparison(5000.0, "EUR", "USD")
        self.assertEqual(res.source_amount, 5000.0)
        self.assertEqual(res.source_currency, "EUR")
        self.assertEqual(res.target_currency, "USD")
        
        # Le montant FinTech doit être strictement supérieur à la banque traditionnelle
        self.assertGreater(res.best_fintech.net_amount_target, res.traditional_bank.net_amount_target)
        # La perte cachée doit être positive
        self.assertGreater(res.hidden_bank_loss_target, 0)
        self.assertGreater(res.hidden_bank_loss_source, 0)
        # Le montant PayPal doit être inférieur au montant FinTech
        self.assertGreater(res.best_fintech.net_amount_target, res.paypal.net_amount_target)

    def test_zero_or_negative_protection(self):
        res = self.engine.calculate_comparison(10.0, "EUR", "USD")
        # Sur un montant inférieur aux frais fixes (37€), la banque retourne 0
        self.assertEqual(res.traditional_bank.net_amount_target, 0.0)


if __name__ == "__main__":
    unittest.main()
