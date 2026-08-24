"""Run the candidate shortlist through the six-gate framework."""

import json
import os
import sys

from framework import (
    Product, evaluate, breakdown, min_viable_sell, markup_crossover,
    binding_gate, upsell_economics, net_profit, MIN_MARKUP, MIN_NET_PROFIT,
)

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path=None):
    with open(path or os.path.join(HERE, "candidates.json")) as fh:
        return json.load(fh)


def to_product(d):
    return Product(
        name=d["name"],
        supplier_cost=d["supplier_cost"],
        sell_price=d["sell_price"],
        shipping_cost=d["shipping_cost"],
        weight_grams=d["weight_grams"],
        dimensions_in=d["dimensions_in"],
        pain=d["pain"],
        pain_type=d["pain_type"],
        evergreen_evidence=d["evergreen_evidence"],
        upsells=d.get("upsells", []),
        competitor_keywords=d.get("competitor_keywords", []),
        saturation_note=d.get("saturation_note", ""),
        verdict_notes=d.get("verdict_notes", ""),
    )


def report(product: Product):
    gates, passed = evaluate(product)
    b = breakdown(product.supplier_cost, product.sell_price)

    print(f"\n{'=' * 72}\n{product.name}\n{'=' * 72}")
    for label, ok, detail in gates:
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {label}")
        print(f"         {detail[:200]}")
    print(f"\n  VERDICT: {'ALL SIX GATES PASS' if passed else 'REJECTED'}")

    print(f"\n  Profit breakdown per sale")
    print(f"    Supplier cost         ${b['supplier_cost']:>8.2f}")
    print(f"    Sell price            ${b['sell_price']:>8.2f}   ({b['markup']:.2f}x markup)")
    print(f"    Gross profit          ${b['gross_profit']:>8.2f}")
    print(f"    Ad spend (20%)        ${b['ad_spend']:>8.2f}")
    print(f"    Processing (5%)       ${b['processing']:>8.2f}")
    print(f"    Returns/CS (5%)       ${b['returns']:>8.2f}")
    print(f"    {'-' * 32}")
    print(f"    NET PROFIT            ${b['net_profit']:>8.2f}   "
          f"({'PASS' if b['net_profit'] >= MIN_NET_PROFIT else 'FAIL'})")

    floor = min_viable_sell(product.supplier_cost)
    print(f"\n    Minimum viable sell price at this cost: ${floor:.2f} "
          f"(binding gate: {binding_gate(product.supplier_cost)})")
    print(f"    Headroom above floor:                   ${product.sell_price - floor:.2f}")

    if product.upsells:
        rows = upsell_economics(product.upsells)
        print(f"\n  Upsell economics")
        for r in rows:
            tag = " [recurring]" if r["recurring"] else ""
            print(f"    {r['name'][:38]:<38} ${r['cost']:>5.2f} -> ${r['sell']:>6.2f}"
                  f"  net ${r['net']:>6.2f}{tag}")
        aov_net = b["net_profit"] + sum(r["net"] for r in rows)
        print(f"    {'-' * 60}")
        print(f"    Net profit if all upsells attach:        ${aov_net:.2f}")


def sensitivity(cost_range, sell):
    lo, hi = cost_range
    print(f"\n  Supplier cost sensitivity at a ${sell:.0f} sell price")
    print(f"    {'cost':>8} {'markup':>8} {'net':>9}  gates")
    c = lo
    while c <= hi + 1e-9:
        n = net_profit(c, sell)
        m = sell / c
        ok = m >= MIN_MARKUP and n >= MIN_NET_PROFIT
        print(f"    ${c:>7.2f} {m:>7.2f}x ${n:>8.2f}  {'pass' if ok else 'FAIL'}")
        c += (hi - lo) / 7


def main():
    data = load(sys.argv[1] if len(sys.argv) > 1 else None)

    print(f"Margin greenzone structure")
    print(f"  Net profit = 0.70 x sell - cost")
    print(f"  Crossover supplier cost = ${markup_crossover():.2f}")
    print(f"    below it, the ${MIN_NET_PROFIT:.0f} net rule binds "
          f"(you must exceed {MIN_MARKUP:.0f}x)")
    print(f"    above it, the {MIN_MARKUP:.0f}x markup rule binds "
          f"({MIN_MARKUP:.0f}x clears ${MIN_NET_PROFIT:.0f} on its own)")

    rec = to_product(data["recommended"])
    report(rec)
    sensitivity(data["recommended"]["supplier_cost_range"], rec.sell_price)
    print(f"\n  Note: {data['recommended']['verdict_notes']}")

    report(to_product(data["runner_up"]))

    print(f"\n{'=' * 72}\nRejected on the gates\n{'=' * 72}")
    for r in data["rejected"]:
        print(f"  {r['name']}\n    {r['reason']}\n")


if __name__ == "__main__":
    main()
