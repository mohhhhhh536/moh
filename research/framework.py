"""Dropshipping product validation framework.

Implements the six-gate screen and the exact profit formula used to decide
whether a product is worth testing.

Profit formula (per sale):
    gross      = sell - cost
    ad spend   = 20% of sell
    processing =  5% of sell   (payment processing + Shopify)
    returns    =  5% of sell   (refunds + customer service)
    net        = sell - cost - 0.30 * sell
               = 0.70 * sell - cost

A product must clear BOTH margin gates: at least a 3x markup AND at least
$20 net profit per sale.
"""

from dataclasses import dataclass, field

AD_SPEND_RATE = 0.20
PROCESSING_RATE = 0.05
RETURNS_RATE = 0.05

VARIABLE_RATE = AD_SPEND_RATE + PROCESSING_RATE + RETURNS_RATE  # 0.30

MIN_MARKUP = 3.0
MIN_NET_PROFIT = 20.0
MAX_SHIPPING = 5.0


def net_profit(cost, sell):
    """Net profit per sale after ad spend, processing and returns."""
    return (1 - VARIABLE_RATE) * sell - cost


def breakdown(cost, sell):
    """Itemised profit breakdown for one sale."""
    return {
        "supplier_cost": cost,
        "sell_price": sell,
        "markup": sell / cost if cost else float("inf"),
        "gross_profit": sell - cost,
        "ad_spend": -AD_SPEND_RATE * sell,
        "processing": -PROCESSING_RATE * sell,
        "returns": -RETURNS_RATE * sell,
        "net_profit": net_profit(cost, sell),
    }


def min_sell_for_net(cost, target_net=MIN_NET_PROFIT):
    """Cheapest sell price that still nets `target_net`."""
    return (cost + target_net) / (1 - VARIABLE_RATE)


def min_viable_sell(cost):
    """Cheapest sell price clearing BOTH the 3x markup and $20 net gates."""
    return max(MIN_MARKUP * cost, min_sell_for_net(cost))


def binding_gate(cost):
    """Which margin gate sets the floor price at this supplier cost.

    Below the crossover the $20 net rule binds and you must mark up by more
    than 3x; above it the 3x rule binds and 3x clears $20 net on its own.
    """
    if abs(MIN_MARKUP * cost - min_sell_for_net(cost)) < 1e-9:
        return "both"
    return "net_profit" if min_sell_for_net(cost) > MIN_MARKUP * cost else "markup"


def markup_crossover():
    """Supplier cost where a bare 3x markup exactly yields $20 net profit."""
    return MIN_NET_PROFIT / (MIN_MARKUP * (1 - VARIABLE_RATE) - 1)


@dataclass
class Product:
    name: str
    supplier_cost: float
    sell_price: float
    shipping_cost: float
    weight_grams: int
    dimensions_in: str
    pain: str
    pain_type: str
    evergreen_evidence: str
    upsells: list = field(default_factory=list)
    competitor_keywords: list = field(default_factory=list)
    saturation_note: str = ""
    verdict_notes: str = ""


def evaluate(p: Product):
    """Score a product against all six gates. Returns (gates, passed)."""
    b = breakdown(p.supplier_cost, p.sell_price)
    gates = []

    gates.append((
        "1. Deep problem",
        bool(p.pain) and p.pain_type in ("physical", "emotional", "both"),
        p.pain,
    ))

    margin_ok = b["markup"] >= MIN_MARKUP and b["net_profit"] >= MIN_NET_PROFIT
    gates.append((
        "2. Margin greenzone",
        margin_ok,
        f"{b['markup']:.2f}x markup, ${b['net_profit']:.2f} net "
        f"(need >={MIN_MARKUP:.0f}x and >=${MIN_NET_PROFIT:.0f})",
    ))

    gates.append((
        "3. Lightweight",
        p.shipping_cost <= MAX_SHIPPING,
        f"{p.weight_grams}g, {p.dimensions_in}, ${p.shipping_cost:.2f} shipping",
    ))

    gates.append((
        "4. Evergreen",
        bool(p.evergreen_evidence),
        p.evergreen_evidence,
    ))

    gates.append((
        "5. Upsell potential",
        len(p.upsells) >= 2,
        "; ".join(u["name"] for u in p.upsells),
    ))

    gates.append((
        "6. Validated, not saturated",
        len(p.competitor_keywords) >= 3 and bool(p.saturation_note),
        p.saturation_note,
    ))

    return gates, all(ok for _, ok, _ in gates)


def upsell_economics(upsells):
    """Net profit contribution of the attached upsells."""
    rows = []
    for u in upsells:
        rows.append({
            "name": u["name"],
            "cost": u["cost"],
            "sell": u["sell"],
            "net": net_profit(u["cost"], u["sell"]),
            "recurring": u.get("recurring", False),
        })
    return rows
