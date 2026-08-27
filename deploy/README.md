# Applying the bundle-pricing + cart-drawer changes

`claude-theme-changes.patch` covers 7 files:

    assets/ds-cart-skin.css            (new)
    assets/section-main-product.css
    config/settings_schema.json
    sections/main-product.liquid
    snippets/cart-drawer.liquid
    snippets/ds-cart-protection.liquid (new)
    snippets/ds-quantity-breaks.liquid

`templates/product.json` is deliberately excluded. It is a single-line
minified file, so patching it replaces the whole line and would wipe the
product page configuration. Configure the bundle tiers in the theme editor
instead, under Product page > Quantity selector.

`apply-claude-changes.sh` must be run from a theme root (the folder that
directly contains assets/, config/, sections/, snippets/). It backs up
first, merges rather than overwrites, writes conflicts to .rej files, and
is safe to run twice.
