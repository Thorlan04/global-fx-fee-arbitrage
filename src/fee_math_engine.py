#!/usr/bin/env python3
"""
fee_math_engine.py
Moteur de calcul mathématique exact des frais bancaires cachés, commissions Stripe/PayPal
et arbitrage FinTech (Wise, Revolut, OFX, Remitly) basé sur les taux interbancaires réels de la BCE.
"""

from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Optional
import json
from pathlib import Path


def quantize_currency(amount: float, precision: int = 2) -> float:
    """Arrondi mathématique financier rigoureux selon la norme bancaire (HALF_UP)."""
    d = Decimal(str(amount))
    q_str = "1." + ("0" * precision) if precision > 0 else "1"
    rounded = d.quantize(Decimal(q_str), rounding=ROUND_HALF_UP)
    return float(rounded)


@dataclass
class ChannelSimulation:
    channel_id: str
    channel_name: str
    channel_type: str  # "fintech", "legacy_bank", "payment_processor"
    gross_amount_source: float
    source_currency: str
    target_currency: str
    mid_market_rate: float
    effective_applied_rate: float
    exchange_markup_percent: float
    fixed_fees_source: float
    variable_fee_percent: float
    variable_fees_source: float
    total_fees_source: float
    net_amount_target: float
    hidden_exchange_loss_source: float
    hidden_exchange_loss_target: float
    total_drag_percent: float
    badge: str
    cta_url: str
    cta_label: str


@dataclass
class ComparisonResult:
    source_amount: float
    source_currency: str
    target_currency: str
    mid_market_rate: float
    theoretical_fair_target: float
    rate_date: str
    best_fintech: ChannelSimulation
    traditional_bank: ChannelSimulation
    paypal: ChannelSimulation
    stripe: ChannelSimulation
    all_channels: List[ChannelSimulation]
    
    # Métriques clés d'arbitrage
    hidden_bank_loss_source: float
    hidden_bank_loss_target: float
    hidden_bank_loss_percent: float
    
    hidden_paypal_loss_source: float
    hidden_paypal_loss_target: float
    hidden_paypal_loss_percent: float
    
    immediate_savings_vs_bank_source: float
    immediate_savings_vs_bank_target: float
    immediate_savings_vs_paypal_source: float
    immediate_savings_vs_paypal_target: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FeeMathEngine:
    """Moteur de calcul mathématique financier haute précision."""

    def __init__(self, rates: Optional[Dict[str, float]] = None, config_path: Optional[Path] = None):
        self.rates: Dict[str, float] = rates or {"EUR": 1.0, "USD": 1.085, "GBP": 0.855, "CHF": 0.972}
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        if config_path and config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        
        # Tentative de chemin par défaut
        default_p = Path(__file__).resolve().parent.parent / "config" / "fintech_partners.json"
        if default_p.exists():
            with open(default_p, "r", encoding="utf-8") as f:
                return json.load(f)

        # Configuration de repli
        return {
            "partners": [
                {
                    "id": "wise",
                    "name": "Wise",
                    "default_url": "https://wise.com/",
                    "affiliate_url": "https://wise.com/",
                    "average_percent_fee": 0.41,
                    "fixed_fee_eur": 0.50,
                    "exchange_markup_percent": 0.00,
                    "badge": "Taux Réel Interbancaire #1"
                },
                {
                    "id": "revolut",
                    "name": "Revolut",
                    "default_url": "https://www.revolut.com/",
                    "affiliate_url": "https://www.revolut.com/",
                    "average_percent_fee": 0.30,
                    "fixed_fee_eur": 0.00,
                    "exchange_markup_percent": 0.15,
                    "badge": "Idéal Carte & Multi-Devises"
                },
                {
                    "id": "ofx",
                    "name": "OFX",
                    "default_url": "https://www.ofx.com/",
                    "affiliate_url": "https://www.ofx.com/",
                    "average_percent_fee": 0.35,
                    "fixed_fee_eur": 0.00,
                    "exchange_markup_percent": 0.30,
                    "badge": "Top Gros Volumes (> 5 000 €)"
                }
            ],
            "benchmarks": {
                "traditional_bank": {
                    "name": "Banque Traditionnelle (SWIFT)",
                    "fixed_fee_eur": 22.00,
                    "average_exchange_markup_percent": 3.10,
                    "correspondent_bank_fee_eur": 15.00
                },
                "paypal": {
                    "name": "PayPal International",
                    "fixed_fee_eur": 0.35,
                    "percentage_fee": 3.40,
                    "exchange_markup_percent": 3.50
                },
                "stripe": {
                    "name": "Stripe Cross-Border",
                    "fixed_fee_eur": 0.25,
                    "percentage_fee": 1.50,
                    "cross_border_addon_percent": 1.50,
                    "currency_conversion_markup_percent": 2.00
                }
            }
        }

    def get_mid_market_rate(self, source_curr: str, target_curr: str) -> float:
        """
        Calcule le taux interbancaire pur (mid-market) entre deux devises.
        Toutes les devises de la BCE sont indexées sur EUR (EUR = 1.0).
        Rate(A -> B) = Rate(EUR -> B) / Rate(EUR -> A)
        """
        src = source_curr.upper()
        tgt = target_curr.upper()

        if src == tgt:
            return 1.0

        if src not in self.rates:
            raise ValueError(f"Devise source inconnue dans le flux BCE : {src}")
        if tgt not in self.rates:
            raise ValueError(f"Devise cible inconnue dans le flux BCE : {tgt}")

        rate_eur_src = self.rates[src]
        rate_eur_tgt = self.rates[tgt]

        mid_rate = rate_eur_tgt / rate_eur_src
        return mid_rate

    def simulate_channel(
        self,
        channel_id: str,
        channel_name: str,
        channel_type: str,
        amount_source: float,
        source_curr: str,
        target_curr: str,
        fixed_fee_in_source: float,
        variable_fee_percent: float,
        exchange_markup_percent: float,
        badge: str = "",
        cta_url: str = "",
        cta_label: str = "Voir l'offre",
        precision_target: int = 2
    ) -> ChannelSimulation:
        """Calcule la simulation exacte pour un canal donné."""
        mid_rate = self.get_mid_market_rate(source_curr, target_curr)

        # 1. Taux effectif après marge de change cachée
        # Le taux appliqué au client est dégradé de exchange_markup_percent
        effective_rate = mid_rate * (1.0 - (exchange_markup_percent / 100.0))

        # 2. Frais variables et fixes
        var_fee = amount_source * (variable_fee_percent / 100.0)
        fixed_fee = fixed_fee_in_source
        total_explicit_fees_src = var_fee + fixed_fee

        # 3. Montant source net converti
        net_source_converted = max(0.0, amount_source - total_explicit_fees_src)

        # 4. Montant reçu en devise cible
        net_amount_target = net_source_converted * effective_rate

        # 5. Calcul de la perte sur le taux de change (marge cachée)
        theoretical_target_if_no_markup = net_source_converted * mid_rate
        hidden_loss_target = max(0.0, theoretical_target_if_no_markup - net_amount_target)
        hidden_loss_source = hidden_loss_target / mid_rate if mid_rate > 0 else 0.0

        # 6. Drag total (frais visibles + marge cachée)
        fair_ideal_target = amount_source * mid_rate
        total_drag_amount_target = max(0.0, fair_ideal_target - net_amount_target)
        total_drag_percent = (total_drag_amount_target / fair_ideal_target * 100.0) if fair_ideal_target > 0 else 0.0

        return ChannelSimulation(
            channel_id=channel_id,
            channel_name=channel_name,
            channel_type=channel_type,
            gross_amount_source=quantize_currency(amount_source, 2),
            source_currency=source_curr.upper(),
            target_currency=target_curr.upper(),
            mid_market_rate=quantize_currency(mid_rate, 5),
            effective_applied_rate=quantize_currency(effective_rate, 5),
            exchange_markup_percent=quantize_currency(exchange_markup_percent, 2),
            fixed_fees_source=quantize_currency(fixed_fee, 2),
            variable_fee_percent=quantize_currency(variable_fee_percent, 2),
            variable_fees_source=quantize_currency(var_fee, 2),
            total_fees_source=quantize_currency(total_explicit_fees_src, 2),
            net_amount_target=quantize_currency(net_amount_target, precision_target),
            hidden_exchange_loss_source=quantize_currency(hidden_loss_source, 2),
            hidden_exchange_loss_target=quantize_currency(hidden_loss_target, precision_target),
            total_drag_percent=quantize_currency(total_drag_percent, 2),
            badge=badge,
            cta_url=cta_url,
            cta_label=cta_label
        )

    def calculate_comparison(
        self,
        amount_source: float,
        source_curr: str = "EUR",
        target_curr: str = "USD",
        lang: str = "fr",
        precision_target: int = 2,
        rate_date: str = ""
    ) -> ComparisonResult:
        """
        Génère la comparaison complète et chiffrée entre :
        - FinTechs (Wise, Revolut, OFX, Remitly)
        - Banque Traditionnelle (SWIFT + marge cachée de 3.10%)
        - PayPal International (3.4% + 0.35€ + 3.5% marge)
        - Stripe Cross-Border (1.5% + 1.5% international + 2.0% conversion + 0.25€)
        """
        source_curr = source_curr.upper()
        target_curr = target_curr.upper()
        mid_rate = self.get_mid_market_rate(source_curr, target_curr)
        fair_target = quantize_currency(amount_source * mid_rate, precision_target)

        # Conversion des frais fixes exprimés en EUR vers la devise source si nécessaire
        rate_eur_to_src = self.get_mid_market_rate("EUR", source_curr)

        benchmarks = self.config.get("benchmarks", {})
        bank_bench = benchmarks.get("traditional_bank", {})
        paypal_bench = benchmarks.get("paypal", {})
        stripe_bench = benchmarks.get("stripe", {})

        # 1. Banque Traditionnelle SWIFT
        bank_fixed_src = (bank_bench.get("fixed_fee_eur", 22.0) + bank_bench.get("correspondent_bank_fee_eur", 15.0)) * rate_eur_to_src
        bank_markup = bank_bench.get("average_exchange_markup_percent", 3.10)
        bank_sim = self.simulate_channel(
            channel_id="traditional_bank",
            channel_name="Banque Traditionnelle (SWIFT)",
            channel_type="legacy_bank",
            amount_source=amount_source,
            source_curr=source_curr,
            target_curr=target_curr,
            fixed_fee_in_source=bank_fixed_src,
            variable_fee_percent=0.0,
            exchange_markup_percent=bank_markup,
            badge="Frais Cachés Élevés",
            cta_url="#compare",
            cta_label="Éviter les frais bancaires",
            precision_target=precision_target
        )

        # 2. PayPal International
        paypal_fixed_src = paypal_bench.get("fixed_fee_eur", 0.35) * rate_eur_to_src
        paypal_var_pct = paypal_bench.get("percentage_fee", 3.40)
        paypal_markup = paypal_bench.get("exchange_markup_percent", 3.50)
        paypal_sim = self.simulate_channel(
            channel_id="paypal",
            channel_name="PayPal International",
            channel_type="payment_processor",
            amount_source=amount_source,
            source_curr=source_curr,
            target_curr=target_curr,
            fixed_fee_in_source=paypal_fixed_src,
            variable_fee_percent=paypal_var_pct,
            exchange_markup_percent=paypal_markup,
            badge="Très coûteux en conversion",
            cta_url="#compare",
            cta_label="Remplacer PayPal",
            precision_target=precision_target
        )

        # 3. Stripe Cross-Border
        stripe_fixed_src = stripe_bench.get("fixed_fee_eur", 0.25) * rate_eur_to_src
        stripe_var_pct = stripe_bench.get("percentage_fee", 1.50) + stripe_bench.get("cross_border_addon_percent", 1.50)
        stripe_markup = stripe_bench.get("currency_conversion_markup_percent", 2.00)
        stripe_sim = self.simulate_channel(
            channel_id="stripe",
            channel_name="Stripe Cross-Border",
            channel_type="payment_processor",
            amount_source=amount_source,
            source_curr=source_curr,
            target_curr=target_curr,
            fixed_fee_in_source=stripe_fixed_src,
            variable_fee_percent=stripe_var_pct,
            exchange_markup_percent=stripe_markup,
            badge="Paiement Carte Internationale",
            cta_url="#compare",
            cta_label="Optimiser ses paiements Stripe",
            precision_target=precision_target
        )

        # 4. FinTech Partners
        fintech_sims: List[ChannelSimulation] = []
        for partner in self.config.get("partners", []):
            fixed_eur = partner.get("fixed_fee_eur", 0.0)
            fixed_src = fixed_eur * rate_eur_to_src
            var_pct = partner.get("average_percent_fee", 0.40)
            markup = partner.get("exchange_markup_percent", 0.00)
            
            cta_txt = partner.get("cta_text", {}).get(lang, partner.get("cta_text", {}).get("en", "Choisir"))
            aff_url = partner.get("affiliate_url", partner.get("default_url", ""))

            sim = self.simulate_channel(
                channel_id=partner.get("id", "fintech"),
                channel_name=partner.get("name", "FinTech"),
                channel_type="fintech",
                amount_source=amount_source,
                source_curr=source_curr,
                target_curr=target_curr,
                fixed_fee_in_source=fixed_src,
                variable_fee_percent=var_pct,
                exchange_markup_percent=markup,
                badge=partner.get("badge", "Transparence Garantie"),
                cta_url=aff_url,
                cta_label=cta_txt,
                precision_target=precision_target
            )
            fintech_sims.append(sim)

        # Trier les fintechs par montant reçu décroissant
        fintech_sims.sort(key=lambda x: x.net_amount_target, reverse=True)
        best_fintech = fintech_sims[0]

        all_channels = [best_fintech] + fintech_sims[1:] + [stripe_sim, paypal_sim, bank_sim]

        # Calculs d'arbitrage
        # Perte bancaire cachée
        bank_loss_target = max(0.0, best_fintech.net_amount_target - bank_sim.net_amount_target)
        bank_loss_src = quantize_currency(bank_loss_target / mid_rate, 2)
        bank_loss_pct = quantize_currency((bank_loss_src / amount_source * 100.0) if amount_source > 0 else 0.0, 2)

        # Perte PayPal
        paypal_loss_target = max(0.0, best_fintech.net_amount_target - paypal_sim.net_amount_target)
        paypal_loss_src = quantize_currency(paypal_loss_target / mid_rate, 2)
        paypal_loss_pct = quantize_currency((paypal_loss_src / amount_source * 100.0) if amount_source > 0 else 0.0, 2)

        return ComparisonResult(
            source_amount=quantize_currency(amount_source, 2),
            source_currency=source_curr,
            target_currency=target_curr,
            mid_market_rate=quantize_currency(mid_rate, 5),
            theoretical_fair_target=fair_target,
            rate_date=rate_date,
            best_fintech=best_fintech,
            traditional_bank=bank_sim,
            paypal=paypal_sim,
            stripe=stripe_sim,
            all_channels=all_channels,
            hidden_bank_loss_source=bank_loss_src,
            hidden_bank_loss_target=quantize_currency(bank_loss_target, precision_target),
            hidden_bank_loss_percent=bank_loss_pct,
            hidden_paypal_loss_source=paypal_loss_src,
            hidden_paypal_loss_target=quantize_currency(paypal_loss_target, precision_target),
            hidden_paypal_loss_percent=paypal_loss_pct,
            immediate_savings_vs_bank_source=bank_loss_src,
            immediate_savings_vs_bank_target=quantize_currency(bank_loss_target, precision_target),
            immediate_savings_vs_paypal_source=paypal_loss_src,
            immediate_savings_vs_paypal_target=quantize_currency(paypal_loss_target, precision_target)
        )


def main():
    """Démo rapide du moteur mathématique."""
    import sys
    engine = FeeMathEngine()
    for test_amt in [100.0, 1000.0, 5000.0, 10000.0]:
        res = engine.calculate_comparison(test_amt, "EUR", "USD")
        print(f"\n=== Transfert {test_amt} EUR vers USD (Taux BCE: {res.mid_market_rate}) ===")
        print(f"  FinTech Leader ({res.best_fintech.channel_name}) : Reçu = {res.best_fintech.net_amount_target} USD")
        print(f"  Banque Trad (SWIFT) : Reçu = {res.traditional_bank.net_amount_target} USD (Frais: {res.traditional_bank.total_fees_source} EUR + Marge: {res.traditional_bank.exchange_markup_percent}%)")
        print(f"  PayPal International : Reçu = {res.paypal.net_amount_target} USD")
        print(f"  PERTE BANCAIRE CACHÉE : {res.hidden_bank_loss_target} USD ({res.hidden_bank_loss_source} EUR soit {res.hidden_bank_loss_percent}%)")
        print(f"  PERTE PAYPAL CACHÉE   : {res.hidden_paypal_loss_target} USD ({res.hidden_paypal_loss_source} EUR soit {res.hidden_paypal_loss_percent}%)")


if __name__ == "__main__":
    main()
