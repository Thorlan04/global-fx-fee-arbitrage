#!/usr/bin/env python3
"""
agent_generator.py
Générateur autonome multilingue de pages d'arbitrage financier et de calculs de frais cachés.
Génère pour 8 langues (fr, en, de, es, it, pt, nl, ja) les pages d'accueil, les pages par paire de devises
et les guides comparatifs spécialisés (PayPal vs Wise, Stripe multi-devises) dans `docs/`.
Produit également un `sitemap.xml` et un `robots.txt` complets.
"""

import os
import sys
from pathlib import Path

# Assurer l'accès au package racine
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from src.fee_math_engine import FeeMathEngine, ComparisonResult, quantize_currency


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("agent_generator")

SITE_BASE_URL = "https://global-fx-fee-arbitrage.github.io"
SUPPORTED_LANGUAGES = ["fr", "en", "de", "es", "it", "pt", "nl", "ja"]

# Dictionnaire de traductions et métadonnées pour les 8 langues
I18N = {
    "fr": {
        "hero_title": "Calculateur Mathématique des Frais Cachés Bancaires & Devises",
        "hero_sub": "Comparez au centime près les taux de change réels de la Banque Centrale Européenne (BCE) face aux marges dissimulées des banques traditionnelles, PayPal et Stripe.",
        "calc_badge": "Taux Interbancaire BCE Officiel en Direct",
        "calc_headline": "Calculateur Mathématique des Frais Cachés",
        "calc_sub": "Découvrez au centime près la marge invisible prélevée par votre banque ou PayPal.",
        "lbl_send": "Vous transférez :",
        "lbl_receive": "Devise de destination :",
        "txt_mid_notice": "Taux BCE officiel : 1 {src} = {rate} {tgt}",
        "card_loss_bank": "Perte Cachée - Banque Traditionnelle",
        "card_loss_bank_sub": "3.10% de marge invisible + 37€ frais SWIFT",
        "card_loss_paypal": "Perte Commission PayPal",
        "card_loss_paypal_sub": "3.40% commission + 3.50% marge sur taux",
        "card_gain_fintech": "Économie Nette Immédiate FinTech",
        "card_gain_fintech_sub": "Taux de change BCE 100% réel sans surcoût",
        "cta_main": "Récupérer cette économie avec Wise (Taux BCE Réel)",
        "cta_sub": "Calculs mathématiques certifiés sur la base du flux officiel de la Banque Centrale Européenne.",
        "why_title": "Pourquoi les banques et PayPal prélèvent des frais invisibles ?",
        "why_p1": "La majorité des utilisateurs pensent qu'un virement international ne coûte que les 15 à 25 € de frais de dossier affichés. En réalité, le véritable coût réside dans la **majoration du taux de change (spread)**, généralement située entre 2,8% et 3,5% chez les banques traditionnelles et jusqu'à 4,0% chez PayPal.",
        "why_p2": "Sur un virement de 5 000 €, cette marge invisible représente une perte nette de plus de 150 € à 180 €, prélevée en silence sur le montant reçu par le destinataire.",
        "proof_title": "Démonstration Mathématique de l'Arbitrage FinTech",
        "proof_p1": "Les solutions FinTech de nouvelle génération (Wise, Revolut, OFX) appliquent le **taux interbancaire pur de la Banque Centrale Européenne (BCE)** et facturent une commission transparente comprise entre 0,3% et 0,5%. L'économie réalisée est mécanique et immédiate.",
        "faq_q1": "Qu'est-ce que le taux moyen du marché (mid-market rate) de la BCE ?",
        "faq_a1": "C'est le point d'équilibre réel entre l'offre et la demande sur les marchés financiers mondiaux, fixé chaque jour ouvrable par la Banque Centrale Européenne à 16h00 CET sans aucune commission commerciale.",
        "faq_q2": "Comment éviter la commission de conversion PayPal de 3.5% ?",
        "faq_a2": "En liant un compte multi-devises FinTech (comme un compte Wise ou Revolut) et en demandant la facturation directe dans la devise d'origine sans laisser PayPal effectuer la conversion."
    },
    "en": {
        "hero_title": "Mathematical Calculator of Hidden Banking & FX Fees",
        "hero_sub": "Compare real-time European Central Bank (ECB) interbank exchange rates with hidden markups from legacy banks, PayPal, and Stripe down to the exact cent.",
        "calc_badge": "Official Real-Time ECB Interbank Rate",
        "calc_headline": "Hidden Fees Mathematical Calculator",
        "calc_sub": "Expose the invisible margin deducted by your bank or PayPal down to the cent.",
        "lbl_send": "You send:",
        "lbl_receive": "Recipient currency:",
        "txt_mid_notice": "Official ECB rate: 1 {src} = {rate} {tgt}",
        "card_loss_bank": "Hidden Bank Loss - SWIFT Wire",
        "card_loss_bank_sub": "3.10% invisible FX margin + $37 SWIFT wire fees",
        "card_loss_paypal": "PayPal Fee & FX Drag",
        "card_loss_paypal_sub": "3.40% processor fee + 3.50% exchange spread",
        "card_gain_fintech": "Immediate Net FinTech Savings",
        "card_gain_fintech_sub": "100% real ECB mid-market rate with zero markup",
        "cta_main": "Claim this saving with Wise (Real ECB Rate)",
        "cta_sub": "Certified mathematical calculation based on official European Central Bank data.",
        "why_title": "Why do traditional banks and PayPal take hidden fees?",
        "why_p1": "Most users assume an international wire transfer only costs the visible $15 to $25 flat processing fee. In reality, the biggest charge is the **exchange rate markup (spread)**, typically ranging from 2.8% to 3.5% at legacy banks and up to 4.0% at PayPal.",
        "why_p2": "On a $5,000 transfer, this hidden spread wipes out $150 to $180, deducted silently before the funds ever reach the recipient.",
        "proof_title": "Mathematical Proof of FinTech Arbitrage",
        "proof_p1": "Next-generation FinTechs (Wise, Revolut, OFX) use the **pure European Central Bank (ECB) mid-market rate** and bill a transparent fee between 0.3% and 0.5%. The savings are mathematical and immediate.",
        "faq_q1": "What is the ECB mid-market rate?",
        "faq_a1": "It is the true midpoint between buy and sell rates on global financial markets, set each business day by the European Central Bank at 16:00 CET with zero markup.",
        "faq_q2": "How can I avoid PayPal's 3.5% currency conversion markup?",
        "faq_a2": "By connecting a multi-currency account (such as Wise or Revolut) and selecting billing in the native currency rather than letting PayPal convert it."
    },
    "de": {
        "hero_title": "Mathematischer Rechner für versteckte Bank- & Devisengebühren",
        "hero_sub": "Vergleichen Sie centgenau die echten EZB-Referenzkurse mit den versteckten Wechselkursaufschlägen von Filialbanken, PayPal und Stripe.",
        "calc_badge": "Offizieller EZB-Devisenmittelkurs Live",
        "calc_headline": "Mathematischer Rechner für versteckte Gebühren",
        "calc_sub": "Erfahren Sie auf den Cent genau, wie viel Marge Ihre Bank oder PayPal heimlich einbehält.",
        "lbl_send": "Sie überweisen:",
        "lbl_receive": "Empfängerwährung:",
        "txt_mid_notice": "Offizieller EZB-Kurs: 1 {src} = {rate} {tgt}",
        "card_loss_bank": "Versteckter Bankverlust - SWIFT",
        "card_loss_bank_sub": "3,10% versteckte Wechselkursmarge + 37€ Gebühren",
        "card_loss_paypal": "Verlust durch PayPal-Gebühren",
        "card_loss_paypal_sub": "3,40% Gebühr + 3,50% Währungsaufschlag",
        "card_gain_fintech": "Sofortige Netto-Ersparnis mit FinTech",
        "card_gain_fintech_sub": "100% echter EZB-Wechselkurs ohne Aufschlag",
        "cta_main": "Diese Ersparnis mit Wise sichern (Echter EZB-Kurs)",
        "cta_sub": "Mathematisch zertifizierte Berechnung basierend auf Daten der Europäischen Zentralbank.",
        "why_title": "Warum erheben traditionelle Banken und PayPal versteckte Gebühren?",
        "why_p1": "Die meisten Kunden glauben, eine Auslandsüberweisung koste nur die sichtbaren 15 bis 25 € Grundgebühr. In Wahrheit verbirgt sich der größte Kostenfaktor im **Wechselkursaufschlag**, der bei Banken meist 2,8% bis 3,5% und bei PayPal bis zu 4% beträgt.",
        "why_p2": "Bei einer 5.000 € Überweisung summiert sich dieser heimliche Aufschlag auf über 150 € bis 180 € Verlust.",
        "proof_title": "Mathematischer Beweis der FinTech-Arbitrage",
        "proof_p1": "Moderne FinTech-Plattformen wie Wise oder Revolut tauschen Geld zum **echten EZB-Devisenmittelkurs** mit einer transparenten Gebühr von nur ca. 0,3% bis 0,5%.",
        "faq_q1": "Was ist der Devisenmittelkurs der EZB?",
        "faq_a1": "Es ist der faire Mittelwert zwischen Kauf- und Verkaufspreisen an den Finanzmärkten, den die EZB jeden Bankarbeitstag um 16:00 Uhr MEZ feststellt.",
        "faq_q2": "Wie umgehe ich den PayPal-Wechselkursaufschlag von 3,5%?",
        "faq_a2": "Indem Sie ein Multi-Währungskonto (z. B. Wise) hinterlegen und Zahlungen in der Originalwährung abbuchen lassen."
    },
    "es": {
        "hero_title": "Calculadora Matemática de Comisiones Bancarias Ocultas y FX",
        "hero_sub": "Compare al céntimo los tipos de cambio reales del Banco Central Europeo (BCE) con los márgenes ocultos de la banca tradicional, PayPal y Stripe.",
        "calc_badge": "Tipo Interbancario Oficial del BCE en Directo",
        "calc_headline": "Calculadora Matemática de Comisiones Ocultas",
        "calc_sub": "Descubra al céntimo el margen invisible que le cobra su banco o PayPal.",
        "lbl_send": "Usted envía:",
        "lbl_receive": "Moneda de destino:",
        "txt_mid_notice": "Tipo oficial BCE: 1 {src} = {rate} {tgt}",
        "card_loss_bank": "Pérdida Oculta - Banco Tradicional (SWIFT)",
        "card_loss_bank_sub": "3.10% margen oculto en tipo de cambio + 37€ SWIFT",
        "card_loss_paypal": "Pérdida por Comisiones PayPal",
        "card_loss_paypal_sub": "3.40% comisión fija/porcentual + 3.50% sobreprecio FX",
        "card_gain_fintech": "Ahorro Neto Inmediato con FinTech",
        "card_gain_fintech_sub": "100% tipo de cambio real del BCE sin sobreprecios",
        "cta_main": "Obtener este ahorro con Wise (Tipo Real BCE)",
        "cta_sub": "Cálculo matemático certificado con datos oficiales del Banco Central Europeo.",
        "why_title": "¿Por qué los bancos y PayPal aplican comisiones invisibles?",
        "why_p1": "La mayoría de usuarios cree que una transferencia internacional solo cuesta 15€ o 25€. En realidad, el mayor coste es el **margen oculto sobre el tipo de cambio**, típicamente del 2,8% al 3,5% en bancos y hasta el 4,0% en PayPal.",
        "why_p2": "En una transferencia de 5.000€, esto significa perder entre 150€ y 180€ en comisiones silenciosas.",
        "proof_title": "Demostración Matemática del Arbitraje FinTech",
        "proof_p1": "Las FinTechs de última generación (Wise, Revolut) utilizan el **tipo interbancario real del BCE** con comisiones transparentes de solo 0,3% a 0,5%.",
        "faq_q1": "¿Qué es el tipo de cambio medio del BCE?",
        "faq_a1": "Es el punto medio exacto de mercado calculado diariamente a las 16:00 CET por el Banco Central Europeo sin recargos comerciales.",
        "faq_q2": "¿Cómo evitar la comisión de conversión de PayPal del 3,5%?",
        "faq_a2": "Vinculando una cuenta multidivisa y solicitando el cobro en la divisa original sin permitir que PayPal realice la conversión."
    },
    "it": {
        "hero_title": "Calcolatore Matematico dei Costi Nascosti Bancari e Cambi Valuta",
        "hero_sub": "Confronta al centesimo i tassi interbancari reali della Banca Centrale Europea (BCE) con i margini nascosti di banche tradizionali, PayPal e Stripe.",
        "calc_badge": "Tasso Ufficiale BCE in Tempo Reale",
        "calc_headline": "Calcolatore Matematico Costi Nascosti",
        "calc_sub": "Scopri al centesimo quanto perdi in commissioni invisibili con la tua banca o PayPal.",
        "lbl_send": "Importo inviato:",
        "lbl_receive": "Valuta del destinatario:",
        "txt_mid_notice": "Tasso BCE ufficiale: 1 {src} = {rate} {tgt}",
        "card_loss_bank": "Perdita Nascosta Banca Tradizionale",
        "card_loss_bank_sub": "3.10% spread occulto sul cambio + 37€ costi SWIFT",
        "card_loss_paypal": "Perdita Commissioni PayPal",
        "card_loss_paypal_sub": "3.40% commissione transazione + 3.50% ricarico cambio",
        "card_gain_fintech": "Risparmio Netto Immediato FinTech",
        "card_gain_fintech_sub": "Tasso reale BCE al 100% senza maggiorazioni",
        "cta_main": "Recupera questo risparmio con Wise (Tasso Reale BCE)",
        "cta_sub": "Calcoli matematici certificati basati su dati pubblici BCE.",
        "why_title": "Perché le banche e PayPal applicano commissioni invisibili?",
        "why_p1": "Molti credono che un bonifico estero costi solo i 15-25€ dichiarati. Il vero costo è invece lo **spread sul tasso di cambio**, mediamente tra il 2,8% e il 3,5% nelle banche e fino al 4% su PayPal.",
        "why_p2": "Su 5.000€ inviati, questa commissione nascosta equivale a perdere tra i 150€ e i 180€.",
        "proof_title": "Prova Matematica dell'Arbitraggio FinTech",
        "proof_p1": "Piattaforme come Wise e Revolut impiegano il tasso reale BCE e applicano commissioni trasparenti tra lo 0,3% e lo 0,5%.",
        "faq_q1": "Che cos'è il tasso interbancario BCE?",
        "faq_a1": "È il valore di equilibrio del mercato valutario pubblicato ogni giorno lavorativo alle 16:00 CET dalla Banca Centrale Europea.",
        "faq_q2": "Come evitare la maggiorazione di cambio PayPal del 3.5%?",
        "faq_a2": "Associando un conto multivaluta (Wise, Revolut) ed effettuando la transazione nella valuta nativa."
    },
    "pt": {
        "hero_title": "Calculadora Matemática de Taxas Bancárias Ocultas e Câmbio",
        "hero_sub": "Compare ao centavo as taxas interbancárias reais do Banco Central Europeu (BCE) com os spreads ocultos dos bancos tradicionais, PayPal e Stripe.",
        "calc_badge": "Taxa Oficial do BCE em Tempo Real",
        "calc_headline": "Calculadora Matemática de Taxas Ocultas",
        "calc_sub": "Descubra exatamente a margem invisível retida pelo seu banco ou PayPal.",
        "lbl_send": "Você envia:",
        "lbl_receive": "Moeda de destino:",
        "txt_mid_notice": "Taxa oficial BCE: 1 {src} = {rate} {tgt}",
        "card_loss_bank": "Perda Oculta - Banco Tradicional (SWIFT)",
        "card_loss_bank_sub": "3.10% margem cambial oculta + 37€ taxas SWIFT",
        "card_loss_paypal": "Perda em Taxas PayPal",
        "card_loss_paypal_sub": "3.40% comissão + 3.50% margem de conversão",
        "card_gain_fintech": "Economia Líquida Imediata FinTech",
        "card_gain_fintech_sub": "100% taxa média do BCE sem taxas ocultas",
        "cta_main": "Garantir esta economia com Wise (Taxa Real BCE)",
        "cta_sub": "Cálculo matemático certificado baseado em dados públicos do Banco Central Europeu.",
        "why_title": "Por que bancos tradicionais e PayPal cobram taxas ocultas?",
        "why_p1": "A maioria dos clientes pensa que uma transferência internacional custa apenas as taxas fixas anunciadas. Na realidade, o principal custo é a **margem de câmbio oculta**, que varia de 2,8% a 3,5% nos bancos e até 4% no PayPal.",
        "why_p2": "Em uma transferência de 5.000€, isso significa uma perda silenciosa entre 150€ e 180€.",
        "proof_title": "Demonstração Matemática de Arbitragem FinTech",
        "proof_p1": "FinTechs modernas (Wise, Revolut) aplicam o **câmbio real do BCE** com tarifas transparentes de 0,3% a 0,5%.",
        "faq_q1": "O que é a taxa média de mercado do BCE?",
        "faq_a1": "É o ponto médio exato apurado diariamente pelo Banco Central Europeu às 16:00 CET.",
        "faq_q2": "Como eliminar o spread de conversão do PayPal de 3.5%?",
        "faq_a2": "Conectando uma conta multimoeda e efetuando a cobrança na moeda original sem conversão pelo PayPal."
    },
    "nl": {
        "hero_title": "Wiskundige Calculator voor Verborgen Bank- & Wisselkoerskosten",
        "hero_sub": "Vergelijk tot op de cent nauwkeurig de officiële middenkoersen van de Europese Centrale Bank (ECB) met de verborgen marges van traditionele banken, PayPal en Stripe.",
        "calc_badge": "Officiële ECB-Middenkoers Live",
        "calc_headline": "Wiskundige Calculator Verborgen Kosten",
        "calc_sub": "Ontdek tot op de cent hoeveel marge uw bank of PayPal onzichtbaar inhoudt.",
        "lbl_send": "U maakt over:",
        "lbl_receive": "Bestemmingsvaluta:",
        "txt_mid_notice": "Officiële ECB-koers: 1 {src} = {rate} {tgt}",
        "card_loss_bank": "Verborgen Bankverlies - SWIFT",
        "card_loss_bank_sub": "3.10% onzichtbare wisselkoersmarge + 37€ kosten",
        "card_loss_paypal": "Verlies door PayPal-kosten",
        "card_loss_paypal_sub": "3.40% transactiekosten + 3.50% wisselkoersopslag",
        "card_gain_fintech": "Directe Netto FinTech-Besparing",
        "card_gain_fintech_sub": "100% echte ECB-wisselkoers zonder opslag",
        "cta_main": "Bespaar direct via Wise (Echte ECB-koers)",
        "cta_sub": "Wiskundig gecertificeerde berekening op basis van officiële ECB-gegevens.",
        "why_title": "Waarom rekenen traditionele banken en PayPal verborgen kosten?",
        "why_p1": "Velen denken dat een buitenlandse overboeking slechts 15€ tot 25€ kost. Het echte verlies zit echter in de **wisselkoersopslag**, die bij banken 2,8% tot 3,5% bedraagt en bij PayPal tot 4%.",
        "why_p2": "Bij een overboeking van 5.000€ verliest u geruisloos tussen de 150€ en 180€.",
        "proof_title": "Wiskundig Bewijs van FinTech-Arbitrage",
        "proof_p1": "Moderne FinTech-platforms zoals Wise hanteren de zuivere ECB-middenkoers met transparante kosten tussen 0,3% en 0,5%.",
        "faq_q1": "Wat is de middenkoers van de ECB?",
        "faq_a1": "Het exacte evenwichtspunt op de financiële markten, dagelijks om 16:00 CET vastgesteld door de ECB.",
        "faq_q2": "Hoe omzeil ik de 3.5% wisselkoersmarge van PayPal?",
        "faq_a2": "Door een multi-valutarekening (zoals Wise) te koppelen en te betalen in de oorspronkelijke valuta."
    },
    "ja": {
        "hero_title": "隠れ銀行手数料＆為替手数料 数学計算機",
        "hero_sub": "欧州中央銀行 (ECB) の公式仲値と、従来型銀行・PayPal・Stripe が課す隠れた為替手数料マージンを1セント単位で厳密に比較します。",
        "calc_badge": "ECB 公式リアルタイム為替仲値",
        "calc_headline": "隠れ手数料 数学計算機",
        "calc_sub": "銀行やPayPalが気付かれずに差し引いているマージンを1円/セント単位で可視化します。",
        "lbl_send": "送金額:",
        "lbl_receive": "受取通貨:",
        "txt_mid_notice": "公式ECBレート: 1 {src} = {rate} {tgt}",
        "card_loss_bank": "従来型銀行の隠れ損失 (SWIFT)",
        "card_loss_bank_sub": "3.10%の隠れた為替スプレッド + 37€の送金手数料",
        "card_loss_paypal": "PayPal 手数料による損失",
        "card_loss_paypal_sub": "3.40%の手数料 + 3.50%の為替上乗せマージン",
        "card_gain_fintech": "FinTech による即時純節約額",
        "card_gain_fintech_sub": "マークアップなしの100% ECB実勢為替レート",
        "cta_main": "Wise でこの節約額を確保する (ECB実勢レート)",
        "cta_sub": "欧州中央銀行の公式データに基づく数学的検証済み計算。",
        "why_title": "なぜ従来の銀行やPayPalは隠れた手数料を取るのか？",
        "why_p1": "海外送金の手数料は表面上の固定手数料（1,500円〜3,000円）だけと思われがちですが、最大のコストは**為替レートに上乗せされたマージン（スプレッド）**です。銀行では2.8%〜3.5%、PayPalでは最大4.0%が密かに差し引かれます。",
        "why_p2": "5,000ユーロ（約80万円）の送金では、この隠れマージンだけで150€〜180€（約25,000円〜30,000円）が消失します。",
        "proof_title": "FinTech アービトラージの数学的証明",
        "proof_p1": "次世代FinTech（Wise、Revolut等）は**ECB実勢仲値**を採用し、わずか0.3%〜0.5%の透明な手数料のみを請求するため、差額がそのまま手元に残ります。",
        "faq_q1": "ECBの市場中間レート（仲値）とは何ですか？",
        "faq_a1": "世界の金融市場の買値と売値の真の中央値で、欧州中央銀行が毎営業日16:00 CETに公表する純粋な基準為替レートです。",
        "faq_q2": "PayPal の 3.5% 為替手数料を回避するには？",
        "faq_a2": "マルチカレンシー口座（Wise 等）を連携し、PayPal側の両替を使用せず原通貨での決済を選択することで完全に回避できます。"
    }
}

KEY_CORRIDORS = [
    ("EUR", "USD", 5000),
    ("EUR", "CHF", 5000),
    ("EUR", "GBP", 5000),
    ("EUR", "CAD", 5000),
    ("EUR", "MAD", 5000),
    ("EUR", "JPY", 5000),
    ("EUR", "AED", 5000),
    ("EUR", "BRL", 5000),
    ("EUR", "AUD", 5000),
    ("EUR", "PLN", 5000),
    ("USD", "EUR", 5000),
    ("USD", "GBP", 5000),
    ("USD", "CAD", 5000),
    ("GBP", "EUR", 5000),
    ("EUR", "USD", 1000),
    ("EUR", "USD", 10000)
]


def load_template(template_path: Path) -> str:
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def format_editorial_section(lang: str, result: ComparisonResult) -> str:
    """Génère la section de contenu éditorial, d'analyse et de FAQ structurée."""
    t = I18N.get(lang, I18N["en"])
    
    html = f"""
    <section class="authority-section">
      <h2>{t['why_title']}</h2>
      <p>{t['why_p1']}</p>
      <p>{t['why_p2']}</p>

      <h3>{t['proof_title']}</h3>
      <p>{t['proof_p1']}</p>
      <ul>
        <li><strong>Banque Trad. SWIFT :</strong> Marge moyenne de {result.traditional_bank.exchange_markup_percent}% + frais de correspondants.</li>
        <li><strong>PayPal International :</strong> {result.paypal.variable_fee_percent}% commission + {result.paypal.exchange_markup_percent}% marge cachée sur le taux.</li>
        <li><strong>Wise / FinTech :</strong> {result.best_fintech.variable_fee_percent}% commission affichée, <strong>0.00% de marge cachée</strong>.</li>
      </ul>
    </section>

    <section class="authority-section">
      <h2>Questions Fréquentes (FAQ) & Conformité</h2>
      <div class="faq-item" style="margin-bottom: 1.2rem;">
        <h3>📌 {t['faq_q1']}</h3>
        <p>{t['faq_a1']}</p>
      </div>
      <div class="faq-item">
        <h3>📌 {t['faq_q2']}</h3>
        <p>{t['faq_a2']}</p>
      </div>
    </section>
    """
    return html


def build_page_html(
    base_template: str,
    calc_template: str,
    lang: str,
    page_slug: str,
    page_title: str,
    page_desc: str,
    hero_title: str,
    hero_sub: str,
    body_content: str,
    rates_payload: Dict[str, Any],
    partners_config: Dict[str, Any],
    currencies_config: Dict[str, Any],
    default_src: str = "EUR",
    default_tgt: str = "USD"
) -> str:
    """Assemble une page HTML complète avec injection des données JSON et balises SEO."""
    html = base_template
    
    # Active state navigation
    for l in SUPPORTED_LANGUAGES:
        placeholder = f"{{{{IS_{l.upper()}_ACTIVE}}}}"
        html = html.replace(placeholder, "active" if l == lang else "")

    canonical = f"{SITE_BASE_URL}/{lang}/{page_slug}" if page_slug else f"{SITE_BASE_URL}/{lang}/"

    # Calculator template with language-localized labels
    calc_html = calc_template
    t = I18N.get(lang, I18N["en"])
    calc_html = calc_html.replace('id="txt-calc-live-status">Taux Interbancaire BCE Officiel en Direct', f'id="txt-calc-live-status">{t["calc_badge"]}')
    calc_html = calc_html.replace('id="txt-calc-headline">Calculateur Mathématique des Frais Cachés', f'id="txt-calc-headline">{t["calc_headline"]}')
    calc_html = calc_html.replace('id="txt-calc-sub">Découvrez au centime près la marge invisible prélevée par votre banque ou PayPal.', f'id="txt-calc-sub">{t["calc_sub"]}')
    calc_html = calc_html.replace('id="lbl-send-amount">Vous transférez :', f'id="lbl-send-amount">{t["lbl_send"]}')
    calc_html = calc_html.replace('id="lbl-receive-currency">Devise de destination :', f'id="lbl-receive-currency">{t["lbl_receive"]}')
    calc_html = calc_html.replace('id="txt-loss-bank-title">Perte Cachée - Banque Traditionnelle', f'id="txt-loss-bank-title">{t["card_loss_bank"]}')
    calc_html = calc_html.replace('id="metric-bank-subtext">3.10% de marge invisible + 37€ frais SWIFT', f'id="metric-bank-subtext">{t["card_loss_bank_sub"]}')
    calc_html = calc_html.replace('id="txt-loss-paypal-title">Perte Commission PayPal', f'id="txt-loss-paypal-title">{t["card_loss_paypal"]}')
    calc_html = calc_html.replace('id="metric-paypal-subtext">3.40% commission + 3.50% marge sur taux', f'id="metric-paypal-subtext">{t["card_loss_paypal_sub"]}')
    calc_html = calc_html.replace('id="txt-gain-fintech-title">Économie Nette Immédiate FinTech', f'id="txt-gain-fintech-title">{t["card_gain_fintech"]}')
    calc_html = calc_html.replace('id="metric-fintech-subtext">Taux de change BCE 100% réel sans surcoût', f'id="metric-fintech-subtext">{t["card_gain_fintech_sub"]}')
    calc_html = calc_html.replace('id="btn-cta-text">Récupérer cette économie avec Wise (Taux BCE Réel)', f'id="btn-cta-text">{t["cta_main"]}')
    calc_html = calc_html.replace('id="txt-cta-footnote">Calculs mathématiques certifiés sur la base du flux officiel de la Banque Centrale Européenne.', f'id="txt-cta-footnote">{t["cta_sub"]}')

    # Remplacement des variables du layout
    replacements = {
        "{{LANG}}": lang,
        "{{PAGE_TITLE}}": page_title,
        "{{PAGE_DESCRIPTION}}": page_desc,
        "{{PAGE_SLUG}}": page_slug,
        "{{CANONICAL_URL}}": canonical,
        "{{SITE_BASE_URL}}": SITE_BASE_URL,
        "{{HERO_TITLE}}": hero_title,
        "{{HERO_SUBTITLE}}": hero_sub,
        "{{CALCULATOR_HTML}}": calc_html,
        "{{PAGE_BODY_CONTENT}}": body_content,
        "{{INJECTED_RATES_JSON}}": json.dumps(rates_payload),
        "{{INJECTED_PARTNERS_JSON}}": json.dumps(partners_config),
        "{{INJECTED_CURRENCIES_JSON}}": json.dumps(currencies_config),
        "{{DEFAULT_SRC_CURR}}": default_src,
        "{{DEFAULT_TGT_CURR}}": default_tgt
    }

    for k, v in replacements.items():
        html = html.replace(k, str(v))

    return html


def generate_all_pages(base_dir: Path) -> List[str]:
    """Génération autonome de l'intégralité du site sous docs/."""
    docs_dir = base_dir / "docs"
    templates_dir = base_dir / "templates"
    config_dir = base_dir / "config"
    data_dir = base_dir / "data"

    base_tmpl = load_template(templates_dir / "base.html")
    calc_tmpl = load_template(templates_dir / "fx_calculator.html")

    # Chargement des données
    with open(config_dir / "fintech_partners.json", "r", encoding="utf-8") as f:
        partners_config = json.load(f)

    with open(config_dir / "currencies.json", "r", encoding="utf-8") as f:
        currencies_config = json.load(f)

    rates_file = data_dir / "ecb_rates.json"
    if not rates_file.exists():
        from src.ecb_rates_sync import get_latest_ecb_rates, save_rates_to_files
        rates_payload = get_latest_ecb_rates()
        save_rates_to_files(rates_payload, base_dir)
    else:
        with open(rates_file, "r", encoding="utf-8") as f:
            rates_payload = json.load(f)

    math_engine = FeeMathEngine(rates=rates_payload.get("rates", {}), config_path=config_dir / "fintech_partners.json")

    generated_urls = []

    # 1. Générer la page racine index.html (redirection vers langue ou accueil défaut)
    root_html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url={SITE_BASE_URL}/fr/">
  <link rel="canonical" href="{SITE_BASE_URL}/fr/">
  <title>Global FX Fee Arbitrage - Redirection</title>
</head>
<body>
  <p>Redirection vers <a href="{SITE_BASE_URL}/fr/">Global FX Fee Arbitrage (Français)</a> ou <a href="{SITE_BASE_URL}/en/">English version</a>...</p>
</body>
</html>"""
    with open(docs_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(root_html)
    generated_urls.append(f"{SITE_BASE_URL}/")

    # 2. Pour chacune des 8 langues : Générer la page d'accueil linguistique
    for lang in SUPPORTED_LANGUAGES:
        lang_dir = docs_dir / lang
        lang_dir.mkdir(parents=True, exist_ok=True)
        t = I18N[lang]

        # Comparaison de référence 5000 EUR -> USD
        sample_res = math_engine.calculate_comparison(5000, "EUR", "USD", lang=lang)
        body_content = format_editorial_section(lang, sample_res)

        page_title = f"{t['hero_title']} | BCE Live Arbitrage"
        page_desc = f"{t['hero_sub']} Économisez immédiatement sur vos virements bancaires, PayPal et Stripe."
        
        index_html = build_page_html(
            base_template=base_tmpl,
            calc_template=calc_tmpl,
            lang=lang,
            page_slug="",
            page_title=page_title,
            page_desc=page_desc,
            hero_title=t["hero_title"],
            hero_sub=t["hero_sub"],
            body_content=body_content,
            rates_payload=rates_payload,
            partners_config=partners_config,
            currencies_config=currencies_config,
            default_src="EUR",
            default_tgt="USD"
        )

        with open(lang_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(index_html)
        generated_urls.append(f"{SITE_BASE_URL}/{lang}/")

        # 3. Pour chaque corridor clé, générer la landing page ciblée
        for src, tgt, amt in KEY_CORRIDORS:
            corridor_res = math_engine.calculate_comparison(amt, src, tgt, lang=lang)
            slug = f"virement-{amt}-{src.lower()}-{tgt.lower()}.html"
            
            p_title = f"Frais réels virement {amt} {src} vers {tgt} - Calculateur Perte Bancaire" if lang == "fr" else f"Real Fees Transfer {amt} {src} to {tgt} - Hidden Loss Calculator"
            p_desc = f"Comparez le montant exact reçu pour un virement de {amt} {src} en {tgt}. Perte bancaire cachée: {corridor_res.hidden_bank_loss_target} {tgt}."

            c_body = f"""
            <section class="authority-section">
              <h2>Analyse Mathématique Certifiée : Transfert de {amt} {src} vers {tgt}</h2>
              <p>Au taux interbancaire officiel de la BCE (1 {src} = {corridor_res.mid_market_rate} {tgt}), vous devriez recevoir en théorie <strong>{corridor_res.theoretical_fair_target} {tgt}</strong>.</p>
              
              <div class="arbitrage-summary-cards" style="margin: 1.5rem 0;">
                <div class="summary-card loss-bank">
                  <div class="card-icon">🏦</div>
                  <div class="card-content">
                    <div class="card-title">Banque Trad. (SWIFT)</div>
                    <div class="card-metric text-danger">{corridor_res.traditional_bank.net_amount_target} {tgt}</div>
                    <div class="card-subtext">Perte invisible : {corridor_res.hidden_bank_loss_target} {tgt} ({corridor_res.hidden_bank_loss_source} {src})</div>
                  </div>
                </div>

                <div class="summary-card profit-fintech">
                  <div class="card-icon">⚡</div>
                  <div class="card-content">
                    <div class="card-title">FinTech Leader ({corridor_res.best_fintech.channel_name})</div>
                    <div class="card-metric text-success">{corridor_res.best_fintech.net_amount_target} {tgt}</div>
                    <div class="card-subtext">Économie immédiate : +{corridor_res.immediate_savings_vs_bank_target} {tgt}</div>
                  </div>
                </div>
              </div>
            </section>
            """ + format_editorial_section(lang, corridor_res)

            pair_html = build_page_html(
                base_template=base_tmpl,
                calc_template=calc_tmpl,
                lang=lang,
                page_slug=slug,
                page_title=p_title,
                page_desc=p_desc,
                hero_title=f"{amt} {src} ➔ {tgt} : Frais Réels & Arbitrage BCE",
                hero_sub=f"Calcul direct de la marge cachée sur le virement de {amt} {src} vers {tgt}.",
                body_content=c_body,
                rates_payload=rates_payload,
                partners_config=partners_config,
                currencies_config=currencies_config,
                default_src=src,
                default_tgt=tgt
            )

            with open(lang_dir / slug, "w", encoding="utf-8") as f:
                f.write(pair_html)
            generated_urls.append(f"{SITE_BASE_URL}/{lang}/{slug}")

        # 4. Guides Spécialisés : PayPal vs Wise & Stripe Multi-Devises
        # PayPal vs Wise
        pp_slug = "paypal-vs-wise.html"
        pp_title = "Calculateur Commission PayPal vs Wise en Dollar & Devises" if lang == "fr" else "PayPal vs Wise Commission Calculator - Live FX"
        pp_desc = "Comparaison mathématique des frais de transaction et commissions de conversion de devises PayPal face au taux réel Wise."
        pp_body = """
        <section class="authority-section">
          <h2>Pourquoi PayPal coûte jusqu'à 7% sur les virements internationaux ?</h2>
          <p>Le modèle tarifaire de PayPal combine deux couches distinctes de prélèvements :</p>
          <ul>
            <li><strong>La commission de transaction :</strong> de 2,90% à 3,40% + frais fixes par transaction.</li>
            <li><strong>La marge sur le taux de change :</strong> PayPal majore systématiquement le taux de conversion de 3,50% à 4,00% par rapport au cours interbancaire de la BCE.</li>
          </ul>
          <p>En comparaison, un compte FinTech multi-devises (tel que Wise) permet d'encaisser directement dans la devise de votre client sans subir aucune conversion forcée.</p>
        </section>
        """
        pp_html = build_page_html(
            base_template=base_tmpl,
            calc_template=calc_tmpl,
            lang=lang,
            page_slug=pp_slug,
            page_title=pp_title,
            page_desc=pp_desc,
            hero_title="PayPal vs Wise : Le Comparateur Mathématique",
            hero_sub="Voyez combien PayPal vous coûte réellement sur les encaissements en devises.",
            body_content=pp_body,
            rates_payload=rates_payload,
            partners_config=partners_config,
            currencies_config=currencies_config,
            default_src="USD",
            default_tgt="EUR"
        )
        with open(lang_dir / pp_slug, "w", encoding="utf-8") as f:
            f.write(pp_html)
        generated_urls.append(f"{SITE_BASE_URL}/{lang}/{pp_slug}")

        # Stripe Multi-Currency
        stripe_slug = "stripe-multi-currency.html"
        stripe_title = "Montant Net Après Frais Stripe Multi-Devises" if lang == "fr" else "Stripe Multi-Currency Net Payout Calculator"
        stripe_desc = "Simulateur de reversement net des paiements Stripe transfrontaliers avec double commission carte et change."
        stripe_body = """
        <section class="authority-section">
          <h2>Anatomie des Frais Stripe Cross-Border et Conversion</h2>
          <p>Lorsqu'un client étranger paie sur votre compte Stripe avec une carte émise hors de votre zone monétaire :</p>
          <ul>
            <li>Stripe applique des frais cartes internationales supplémentaires de +1,50%.</li>
            <li>Si Stripe doit convertir les fonds vers votre devise de reversement par défaut, une majoration de 2,00% sur le taux de change s'ajoute.</li>
          </ul>
          <p>Astuce d'arbitrage : Vous pouvez connecter des comptes bancaires virtuels en devises (Wise / Revolut Business) directement dans vos paramètres de reversement Stripe pour éliminer les 2,00% de frais de change !</p>
        </section>
        """
        stripe_html = build_page_html(
            base_template=base_tmpl,
            calc_template=calc_tmpl,
            lang=lang,
            page_slug=stripe_slug,
            page_title=stripe_title,
            page_desc=stripe_desc,
            hero_title="Calculateur Net Stripe Multi-Devises",
            hero_sub="Éliminez les 2% de frais de conversion Stripe en configurant un IBAN multi-devises.",
            body_content=stripe_body,
            rates_payload=rates_payload,
            partners_config=partners_config,
            currencies_config=currencies_config,
            default_src="EUR",
            default_tgt="USD"
        )
        with open(lang_dir / stripe_slug, "w", encoding="utf-8") as f:
            f.write(stripe_html)
        generated_urls.append(f"{SITE_BASE_URL}/{lang}/{stripe_slug}")

    # 5. Générer sitemap.xml et robots.txt
    build_sitemap_and_robots(docs_dir, generated_urls)
    logger.info("Génération terminée : %d pages HTML créées dans %s", len(generated_urls), docs_dir)
    return generated_urls


def build_sitemap_and_robots(docs_dir: Path, urls: List[str]):
    """Génère le sitemap XML aux normes Google et le robots.txt."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for u in sorted(set(urls)):
        sitemap_lines.append(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>0.9</priority>\n  </url>")
    sitemap_lines.append("</urlset>")

    with open(docs_dir / "sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap_lines))

    robots_content = f"""User-agent: *
Allow: /

Sitemap: {SITE_BASE_URL}/sitemap.xml
"""
    with open(docs_dir / "robots.txt", "w", encoding="utf-8") as f:
        f.write(robots_content)


def main():
    base_dir = Path(__file__).resolve().parent.parent
    urls = generate_all_pages(base_dir)
    print(f"SUCCÈS: {len(urls)} pages multilingues générées.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
