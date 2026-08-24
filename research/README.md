# Product Validation Framework

A six-gate screen plus the profit formula, implemented so a product either
clears the bar or it does not.

```
python3 validate.py          # run the shortlist through all six gates
python3 -m unittest test_framework -v
```

## Files

| File | Purpose |
|---|---|
| `framework.py` | Profit formula and the six-gate scoring logic |
| `candidates.json` | Shortlist data: recommendation, runner-up, rejects |
| `validate.py` | Runs the shortlist, prints breakdowns and sensitivity |
| `test_framework.py` | 16 tests, anchored on the worked example |

## The formula

```
net = sell - cost - (0.20 + 0.05 + 0.05) x sell
    = 0.70 x sell - cost
```

The worked example is a regression test: $15 cost / $49 sell returns $19.30
and is rejected for missing $20.

## The greenzone has a crossover at $18.18

The 3x markup rule and the $20 net rule do not bind together. Setting
`0.70 x 3c - c = 20` gives `c = $18.18`:

- **Supplier cost below $18.18** — the $20 net rule binds. 3x is not enough
  and you must mark up by more. A $10 product needs 4.29x, a $5 product 7.14x.
- **Supplier cost above $18.18** — the 3x rule binds. Any 3x price clears $20
  net on its own.

Practical consequence: sourcing in the **$18-28** band is where both gates are
satisfied without straining perceived value. The worked example fails not
because $15 is a bad cost but because $49 is 3.27x when $15 needs 3.33x —
$50 would have passed.

## Recommendation

**RF + EMS + LED neck and jaw sculpting device**, sold on the below-the-chin
angle rather than as a face device.

| | |
|---|---|
| Supplier cost | $24 (buy at or under $26) |
| Sell price | $89 |
| Markup | 3.71x |
| Net profit | $38.30 |
| Net with all upsells | $79.20 |
| Shipping | ~$3.50, 260g, 7x3x2in |

Run `validate.py` for the gate-by-gate result, the itemised breakdown and the
supplier-cost sensitivity table.

### The one number to watch

Buy price. At $89 the markup gate breaks at a $30 supplier cost even though
net profit is still $32.30. Cost discipline, not pricing, is what fails first.

### Gate 6 is the user's to close

The framework supplies competitor keywords; verifying $100k+/mo competitors,
7+ day ad runs and untested angles is manual. Keywords are in
`candidates.json` under `competitor_keywords`.

## Inputs that need verification

Supplier costs are sourced from published wholesale ranges, not a confirmed
SKU quote. Pull the real AutoDS/AliExpress landed cost and re-run — the
sensitivity table shows exactly where the gates break.
