#!/usr/bin/env bash
# Applies the bundle-pricing + cart-drawer changes to an existing Shopify theme.
#
# Run it from your THEME ROOT - the folder that directly contains assets/,
# config/, layout/, sections/, snippets/, templates/.
#
#   bash apply-claude-changes.sh
#
# It never overwrites a file wholesale. Conflicting hunks are written to .rej
# files and reported, so your own edits are preserved and you decide.

set -uo pipefail

PATCH="${1:-claude-theme-changes.patch}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="../theme-backup-$STAMP"

say()  { printf '%s\n' "$*"; }
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

# --- 1. make sure we are actually in a theme root --------------------------
for d in assets config layout sections snippets templates; do
  [ -d "$d" ] || fail "no ./$d here - run this from your theme root, not $(pwd)"
done
[ -f "$PATCH" ] || fail "patch file '$PATCH' not found. Put it next to this script."

say "Theme root : $(pwd)"
say "Patch      : $PATCH"
say ""

# --- 2. back up before touching anything -----------------------------------
say "Backing up to $BACKUP ..."
mkdir -p "$BACKUP" || fail "could not create backup dir"
cp -r assets config layout sections snippets templates "$BACKUP/" \
  || fail "backup failed - stopping before any changes"
say "Backup done. To undo everything:  rm -rf assets config layout sections snippets templates && cp -r $BACKUP/* ."
say ""

# --- 3. skip if already applied --------------------------------------------
if [ -f assets/ds-cart-skin.css ] && grep -q -e "quantity-break__gift" snippets/ds-quantity-breaks.liquid 2>/dev/null; then
  say "Already applied - nothing to do."
  exit 0
fi

# --- 4. apply ---------------------------------------------------------------
say "Applying..."
APPLIED=0

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if git apply --3way --whitespace=nowarn "$PATCH" 2>/dev/null; then
    say "Applied with git 3-way merge."
    APPLIED=1
  fi
fi

if [ "$APPLIED" -eq 0 ]; then
  if git apply --reject --whitespace=nowarn "$PATCH" 2>&1 | sed 's/^/  /'; then
    say "Applied with git apply."
    APPLIED=1
  elif command -v patch >/dev/null 2>&1; then
    say "Falling back to patch(1)..."
    patch -p1 --forward --no-backup-if-mismatch < "$PATCH" 2>&1 | sed 's/^/  /'
    APPLIED=1
  fi
fi

say ""

# --- 5. report --------------------------------------------------------------
REJ=$(find . -name '*.rej' 2>/dev/null)
if [ -n "$REJ" ]; then
  say "CONFLICTS - these hunks did NOT apply and need a manual look:"
  printf '%s\n' "$REJ" | sed 's/^/  /'
  say "Your originals are intact in $BACKUP"
else
  say "No conflicts."
fi

say ""
say "Verifying expected files:"
for f in assets/ds-cart-skin.css snippets/ds-cart-protection.liquid; do
  [ -f "$f" ] && say "  ok       $f" || say "  MISSING  $f"
done
for pair in "snippets/ds-quantity-breaks.liquid:quantity-break__gift" \
            "snippets/cart-drawer.liquid:cart-item__save-badge" \
            "assets/section-main-product.css:--qb-accent" \
            "sections/main-product.liquid:qb_card_bg" \
            "config/settings_schema.json:cart_protection_product"; do
  f="${pair%%:*}"; needle="${pair##*:}"
  grep -q -e "$needle" "$f" 2>/dev/null && say "  ok       $f" || say "  CHECK    $f (missing '$needle')"
done

say ""
say "Done. Next: preview the theme before publishing."
say "templates/product.json was deliberately NOT modified - configure the"
say "bundle tiers in the theme editor instead (Product page > Quantity selector)."
