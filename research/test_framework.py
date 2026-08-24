"""Tests for the validation framework, anchored on the worked example."""

import json
import os
import unittest

from framework import (
    net_profit, breakdown, min_sell_for_net, min_viable_sell, binding_gate,
    markup_crossover, evaluate, MIN_MARKUP, MIN_NET_PROFIT,
)
from validate import load, to_product

HERE = os.path.dirname(os.path.abspath(__file__))


class TestProfitFormula(unittest.TestCase):
    def test_worked_example_is_reproduced_exactly(self):
        # $15 cost / $49 sell must land on $19.30 and be rejected.
        self.assertAlmostEqual(net_profit(15.0, 49.0), 19.30, places=2)
        self.assertLess(net_profit(15.0, 49.0), MIN_NET_PROFIT)

    def test_worked_example_line_items(self):
        b = breakdown(15.0, 49.0)
        self.assertAlmostEqual(b["gross_profit"], 34.00, places=2)
        self.assertAlmostEqual(b["ad_spend"], -9.80, places=2)
        self.assertAlmostEqual(b["processing"], -2.45, places=2)
        self.assertAlmostEqual(b["returns"], -2.45, places=2)
        self.assertAlmostEqual(b["net_profit"], 19.30, places=2)

    def test_line_items_sum_to_net(self):
        b = breakdown(24.0, 89.0)
        total = (b["gross_profit"] + b["ad_spend"] + b["processing"] + b["returns"])
        self.assertAlmostEqual(total, b["net_profit"], places=9)

    def test_fifty_dollars_is_the_fix_for_the_worked_example(self):
        # One dollar more than the rejected $49 clears the gate.
        self.assertAlmostEqual(min_sell_for_net(15.0), 50.00, places=2)
        self.assertGreaterEqual(net_profit(15.0, 50.0), MIN_NET_PROFIT)


class TestGreenzoneStructure(unittest.TestCase):
    def test_crossover_cost(self):
        self.assertAlmostEqual(markup_crossover(), 18.1818, places=3)

    def test_at_crossover_both_gates_bind_simultaneously(self):
        c = markup_crossover()
        self.assertAlmostEqual(min_viable_sell(c), MIN_MARKUP * c, places=6)
        self.assertAlmostEqual(net_profit(c, MIN_MARKUP * c), MIN_NET_PROFIT, places=6)
        self.assertEqual(binding_gate(c), "both")

    def test_cheap_products_need_more_than_three_x(self):
        self.assertEqual(binding_gate(10.0), "net_profit")
        self.assertGreater(min_viable_sell(10.0), MIN_MARKUP * 10.0)

    def test_expensive_products_are_bound_by_markup(self):
        self.assertEqual(binding_gate(25.0), "markup")
        self.assertAlmostEqual(min_viable_sell(25.0), 75.0, places=2)

    def test_min_viable_sell_always_clears_both_gates(self):
        for cost in [5, 8, 10, 12, 15, 18.18, 20, 25, 30, 35, 50]:
            sell = min_viable_sell(cost)
            self.assertGreaterEqual(sell / cost, MIN_MARKUP - 1e-9, f"markup at {cost}")
            self.assertGreaterEqual(net_profit(cost, sell), MIN_NET_PROFIT - 1e-9,
                                    f"net at {cost}")


class TestCandidates(unittest.TestCase):
    def setUp(self):
        self.data = load()

    def test_recommended_passes_all_six_gates(self):
        gates, passed = evaluate(to_product(self.data["recommended"]))
        failed = [label for label, ok, _ in gates if not ok]
        self.assertTrue(passed, f"failed gates: {failed}")
        self.assertEqual(len(gates), 6)

    def test_runner_up_passes_all_six_gates(self):
        _, passed = evaluate(to_product(self.data["runner_up"]))
        self.assertTrue(passed)

    def test_recommended_shipping_under_ceiling(self):
        self.assertLessEqual(self.data["recommended"]["shipping_cost"], 5.0)

    def test_recommended_has_a_recurring_upsell(self):
        ups = self.data["recommended"]["upsells"]
        self.assertTrue(any(u.get("recurring") for u in ups))
        self.assertGreaterEqual(len(ups), 2)

    def test_recommended_supplies_competitor_keywords(self):
        self.assertGreaterEqual(len(self.data["recommended"]["competitor_keywords"]), 3)

    def test_stated_supplier_cost_sits_inside_its_range(self):
        rec = self.data["recommended"]
        lo, hi = rec["supplier_cost_range"]
        self.assertGreaterEqual(rec["supplier_cost"], lo)
        self.assertLessEqual(rec["supplier_cost"], hi)

    def test_top_of_cost_range_breaks_the_markup_gate(self):
        # The documented risk: a $32 buy still nets well but fails 3x at $89.
        rec = self.data["recommended"]
        hi = rec["supplier_cost_range"][1]
        sell = rec["sell_price"]
        self.assertLess(sell / hi, MIN_MARKUP)
        self.assertGreater(net_profit(hi, sell), MIN_NET_PROFIT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
