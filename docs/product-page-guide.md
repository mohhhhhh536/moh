# Product page guide

The product page is built from three custom sections plus the theme's own
blocks. Everything below is editable in **Shopify admin → Online Store →
Themes → Customise → Products**. Nothing here is hard-coded.

## Page order

| # | Section | What it's for |
|---|---------|---------------|
| 1 | Product (main) | Gallery, title, price, the product's own description, benefits, bundle pricing, buy buttons, sticky add-to-cart |
| 2 | Product Story Rows | Long-form description as alternating photo/text rows, each with a side note |
| 3 | How To Use Steps | The four-step application routine |
| 4 | Before & After Reviews | Customer photo reviews, before and after side by side |
| 5 | Collapsible content | Ingredients, suitability, bottle life, shipping & returns |
| 6 | Why Thessvane | Trust row |
| 7 | In Their Words | Written testimonials |
| 8 | Pairs Well With | Related products |

`product.general_template.json` is the same page with a **How It Compares**
table inserted after the story rows. Assign it per product in admin.

## Photo slots

Every slot below currently shows a grey placeholder graphic. The page lays out
correctly without any of them, so you can publish the copy first and drop
photos in as you shoot them.

### Product Story Rows — 3 photos, 4:3 landscape
Upload at 1400 × 1050 or larger.

| Row | Shot | Caption already written |
|-----|------|-------------------------|
| The Formula | Flat-lay of the bottle with a few raw ingredients | "Every formula starts as a short ingredient list." |
| The Feel | Texture on skin — a swatch on the back of a hand, mid-absorb | "Sinks in fast — no residue, no waiting around." |
| The Results | Two dated photos of the same area, same lighting | "Same light, same angle, four weeks apart." |

Each row also has a **side note** — the boxed aside under the copy. Use it for
the caveat that doesn't belong in the main paragraph: a patch-test warning, an
application tip, a "this layers under SPF" note.

### How To Use Steps — 4 photos, 3:4 portrait
Upload at 900 × 1200 or larger. Video stills work well here; shoot them as one
continuous sequence so the four frames match.

1. **Cleanse** — hands under running water / product in the shower
2. **Apply** — pea-sized amount being massaged in
3. **Let It Settle** — the finished skin, close up
4. **Repeat Daily** — the bottle in situ on a shelf or counter

Each step has an optional one-line side note under it.

### Before & After Reviews — 2 photos per card, 3:4 portrait each
Upload each half at 800 × 1067 or larger. The two photos sit flush side by
side, so shoot both from the same distance and angle or the join looks off.

Per card you set: the before photo and its label ("Untreated"), the after photo
and its label ("After 4 Weeks"), a star rating, the review text, the reviewer's
name, and the verified-buyer badge.

## Before you publish — copy that needs your real numbers

The copy on the page is written and ready, but these specific claims are
placeholders and are yours to confirm or change:

- **The star rating (4.9) under the product title** and every rating in the
  review sections. Publishing invented ratings or review counts is a legal
  problem in most markets — swap these for figures from a real review app, or
  turn the rating block off until you have them.
- **All review text and reviewer names**, in Before & After Reviews, In Their
  Words, and the reviews block in the product column. These are written as
  models of the right length and tone. Replace them with real reviews you have
  permission to publish, along with the customers' own photos.
- **Shipping estimate: 3–7 days**, set on the Estimated shipping block, and
  the "packed within one to two business days" line in the Shipping & Returns
  row. Set these to your actual fulfilment times.
- **Returns**: the Shipping & Returns row points at the policy linked in the
  footer rather than stating a window. Make sure that policy page exists.
- **Bundle discounts: 10% / 15% / 20%** on the quantity selector. These need
  matching automatic discounts in Shopify admin, or the prices shown won't be
  what the customer is charged.
- **"Dermatologist-tested", "cruelty-free", "non-comedogenic"** appear in the
  benefits, the FAQ and the comparison table. Keep them only where they're
  true of the formula.

The results disclaimer under the before/after cards ("Results shown are
individual experiences and are not guaranteed") should stay whatever else
changes.
