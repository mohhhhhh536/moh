#!/usr/bin/env bash
# Push the product page onto the LIVE published theme.
#
# Uploads only the files the product-page and bundle-pricing work touches.
# config/settings_data.json is deliberately not among them, so theme-editor
# settings — colours, fonts, logo, the homepage rebuild — are left exactly
# as they are.
#
# sections/main-product.liquid and snippets/ds-quantity-breaks.liquid are
# theme-vendor files this repo has modified in place (new schema settings
# and bundle-card markup), not new files — pushing them overwrites
# whatever version is currently live for those two paths specifically.
#
# Usage:  ./scripts/push-live.sh [store-domain]

set -euo pipefail

STORE="${1:-bys-user-store-358852-skpnrnec.myshopify.com}"
THEME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../theme" && pwd)"

if ! command -v shopify >/dev/null 2>&1; then
  echo "Shopify CLI not found. Install it with:" >&2
  echo "  npm install -g @shopify/cli@latest" >&2
  exit 1
fi

echo "Store:  $STORE"
echo "Target: the LIVE published theme"
echo

shopify theme push \
  --path "$THEME_DIR" \
  --store "$STORE" \
  --live \
  --allow-live \
  --nodelete \
  --only sections/thessvane-product-story.liquid \
  --only sections/thessvane-how-to-use.liquid \
  --only sections/thessvane-product-reviews.liquid \
  --only snippets/thessvane-stars.liquid \
  --only assets/thessvane-stars.css \
  --only sections/main-product.liquid \
  --only snippets/ds-quantity-breaks.liquid \
  --only snippets/thessvane-bundle-thumb.liquid \
  --only snippets/thessvane-bundle-gift.liquid \
  --only assets/thessvane-bundle-pricing.css \
  --only templates/product.json \
  --only templates/product.general_template.json
