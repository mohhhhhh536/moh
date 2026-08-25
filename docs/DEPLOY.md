# Putting the product page live

Store: `bys-user-store-358852-skpnrnec.myshopify.com`

There are four ways to do this. **Option D (GitHub Actions) is the one to use
if you want to click a button rather than copy files by hand.**

## First, the one rule

**Duplicate your live theme before you touch anything.** Online Store →
Themes → find the published theme → **⋯ → Duplicate**. That copy is your
undo button; it costs nothing and takes ten seconds. Make the changes on the
duplicate, preview it, and only publish once it looks right.

## What this change actually adds

Five of the seven files are brand new filenames. They cannot overwrite
anything:

| File | What it is |
|------|-----------|
| `sections/thessvane-product-story.liquid` | Product Story Rows section |
| `sections/thessvane-how-to-use.liquid` | How To Use Steps section |
| `sections/thessvane-before-after.liquid` | Before & After Reviews section |
| `snippets/thessvane-stars.liquid` | Shared star-rating markup |
| `assets/thessvane-stars.css` | Star styling |

Two files **replace** what's currently on the store:

| File | What it replaces |
|------|------------------|
| `templates/product.json` | Your whole product page layout and its copy |
| `templates/product.general_template.json` | The alternate product template |

Those two are the ones to think about. They carry all the written copy — the
story rows, the four steps, the review cards. If you skip them, you get the
three sections in the theme editor's "Add section" menu but you type the copy
in yourself.

**Has your product page been customised in the Shopify editor?** In this repo
it never was — `templates/product.json` was untouched from the original 17 Aug
export until this change, and it still held the demo theme's collagen-stick
content. If your live product page still looks like that demo, replacing these
two files loses nothing. If you have been editing the product page in the
admin since then, use Option A below and add the sections by hand instead.

## Option A — no tooling, safest (recommended)

Work on the duplicate: **⋯ → Edit code**.

1. **Sections** → *Add a new section* → name it `thessvane-product-story` →
   delete the boilerplate Shopify pre-fills → paste the whole file → Save.
   Repeat for `thessvane-how-to-use` and `thessvane-before-after`.
2. **Snippets** → *Add a new snippet* → name it `thessvane-stars` → paste →
   Save.
3. **Assets** → *Add a new asset* → *Create a blank file* → type `css`, name
   `thessvane-stars` → paste → Save.
4. Now the templates. **Do this last** — the templates reference the three
   sections, so those files have to exist first or the page errors.
   - Product page still on the demo content? Open `templates/product.json`,
     select all, paste the new version, Save. Same for
     `product.general_template.json`.
   - Want to keep what's there? Skip the templates. Go to **Customise →
     Products**, and use *Add section* — the three new ones appear near the
     bottom of the list with their copy pre-filled from the presets. Reorder
     by dragging.
5. Preview the duplicate, check a product page on desktop and phone, then
   **Publish**.

## Option B — Shopify CLI, precise

Only if you already have the CLI (`npm i -g @shopify/cli@latest`). Run from
inside the `theme/` folder of this repo:

```bash
shopify theme list --store bys-user-store-358852-skpnrnec.myshopify.com
```

Take the ID of the duplicate you made, then:

```bash
shopify theme push \
  --store bys-user-store-358852-skpnrnec.myshopify.com \
  --theme <THEME_ID> \
  --only sections/thessvane-product-story.liquid \
  --only sections/thessvane-how-to-use.liquid \
  --only sections/thessvane-before-after.liquid \
  --only snippets/thessvane-stars.liquid \
  --only assets/thessvane-stars.css \
  --only templates/product.json \
  --only templates/product.general_template.json
```

**Do not run a bare `shopify theme push`.** Without `--only` it uploads every
file in the folder, including `config/settings_data.json` — which holds every
theme-editor setting you have. Any colour, font, or layout tweak you made in
the admin that never came back into this repo would be reverted.

Drop the last two `--only` lines if you want to keep your current product page
and add the sections by hand.

## Option C — upload the whole theme as a new one

`thessvane-theme.zip` is the complete theme, ready for Online Store → Themes →
*Add theme → Upload zip*. This creates a **new, unpublished** theme and does
not touch your live one at all.

The catch: it carries this repo's `settings_data.json`, so it reflects the
brand colours and logo as committed here. Anything you changed in the Shopify
editor and never brought back into this repo won't be in it. Preview carefully
before publishing.

## After it's live

Read `docs/product-page-guide.md`. It lists what to shoot for each photo slot
and — more importantly — the placeholder claims that need your real numbers
before customers see them: the 4.9 rating, all the review text and names, the
3–7 day shipping estimate, and the 10/15/20% bundle discounts.


## Option D — deploy from GitHub Actions

`.github/workflows/deploy-theme.yml` pushes the theme to Shopify for you.
GitHub's runners can reach your store, so this needs nothing installed on your
machine.

### One-time setup

1. **Shopify admin → Apps → Shopify App Store** → install **Theme Access**
   (published by Shopify).
2. Open it → **Create password** → pick the theme → it emails you a token
   starting `shptka_`.
3. **GitHub → your repo → Settings → Secrets and variables → Actions → New
   repository secret.** Name: `SHOPIFY_CLI_THEME_TOKEN`. Value: the token.

The store domain is already set in the workflow. To point it elsewhere, add a
repository *variable* named `SHOPIFY_STORE`.

### Running it

**Actions → List Shopify themes → Run workflow** first. The log prints every
theme with its ID, including which one is live.

Then **Actions → Deploy theme to Shopify → Run workflow**:

| Input | What to put |
|-------|-------------|
| `theme_id` | The ID to push to. **Leave blank to target the live published theme.** |
| `scope` | `product-page` uploads only the seven files this change touches. `entire-theme` uploads everything. |
| `confirm_live` | Only needed when `theme_id` is blank. The run fails without it, so a blank field can't hit the live theme by accident. |

To add the product page to your published theme, leave `theme_id` blank, keep
`scope` as `product-page`, and tick `confirm_live`.

### What the workflow will not do

- It never runs on a push. Deploys are manual, from the Actions tab.
- It runs `scripts/check-theme.py` first and stops if a schema or template is
  broken, so a bad commit can't reach the storefront.
- It passes `--nodelete`, so it never removes a file from your store just
  because this repo doesn't have it.
- With `scope: product-page` it names all seven files explicitly rather than
  globbing, so it cannot widen to files it wasn't meant to touch —
  `config/settings_data.json` included.

`.github/workflows/validate-theme.yml` runs the same validator on every push
and pull request. It needs no secrets.
