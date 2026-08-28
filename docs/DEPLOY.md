# Deploying to the "Thessvane rebuild" theme

Store: `bys-user-store-358852-skpnrnec.myshopify.com`

## First, the one rule

**Duplicate the theme before you touch it.** Online Store → Themes → find
**Thessvane rebuild** → **⋯ → Duplicate**. That copy is your undo button; it
costs nothing and takes ten seconds.

For this particular change the risk is low — all three files are new
filenames, so they cannot overwrite anything that is already there — but the
habit is worth keeping.

## About the GitHub connection

This repo does **not** use Shopify's native "Connect from GitHub" theme sync.
That feature requires the theme folders (`assets/`, `config/`, `layout/`,
`sections/`, `templates/`, …) to sit at the *root* of the branch, and this
repo keeps them one level down in `theme/`. What it uses instead is the
GitHub Actions workflow below, which runs the Shopify CLI on a GitHub runner
and points it at `theme/`. Same "click a button in GitHub" experience, and it
deploys only the files you name.

### The Actions tab needs the workflow on the default branch

GitHub only shows a **Run workflow** button for a workflow that exists on the
repository's **default branch** (currently `claude/mm-pa32at`). Once it is
there, the *Use workflow from* dropdown lets you run it against any branch —
so the file has to be merged to the default branch once, and after that you
can deploy from whichever branch has the work.

## What this change deploys

| File | What it is | Overwrites? |
|------|-----------|-------------|
| `templates/product.collagen.json` | The PDRN Collagen Stick product template | No — new file |
| `sections/thessvane-ingredient-callout.liquid` | Ingredient Callout section the template uses | No — new file |
| `assets/thessvane-ingredients-placeholder.jpg` | Placeholder image for that section | No — new file |

The other twelve section types the template uses (`multicolumn`, `multirow`,
`results`, `ds-comparison-table`, `collapsible-content`, `ds-*`, …) already
ship with this theme, so there is nothing else to upload.

`config/settings_data.json` is deliberately **not** in scope. Your
theme-editor settings — colours, fonts, logo, homepage — are left alone.

## Option A — GitHub Actions (recommended)

### One-time setup

1. **Shopify admin → Apps → Shopify App Store** → install **Theme Access**
   (published by Shopify).
2. Open it → **Create password** → pick the theme → it emails you a token
   starting `shptka_`.
3. **GitHub → repo → Settings → Secrets and variables → Actions → New
   repository secret.** Name: `SHOPIFY_CLI_THEME_TOKEN`. Value: the token.

The store domain is already set in the workflow. To point it elsewhere, add a
repository *variable* named `SHOPIFY_STORE`.

### Running it

**Actions → Deploy theme to Shopify → Run workflow**, and set:

| Input | What to put |
|-------|-------------|
| Use workflow from | the branch holding the change |
| `theme_id` | `Thessvane rebuild` — the field takes a theme **name or ID** |
| `scope` | `collagen-template` |
| `confirm_live` | leave unticked; it only matters when `theme_id` is blank |

Naming the theme means the live published theme is never the target, whichever
one is currently published. Leaving `theme_id` blank is what targets live, and
the workflow refuses to do that unless `confirm_live` is ticked.

**Actions → List Shopify themes → Run workflow** prints every theme with its
ID if you would rather pass an ID than a name.

### What the workflow will not do

- It never runs on a push. Deploys are manual, from the Actions tab.
- It runs `scripts/check-theme.py` first and stops if a schema or template is
  broken, so a bad commit cannot reach the storefront.
- It passes `--nodelete`, so it never removes a file from your store just
  because this repo does not have it.
- Each scope names its files one by one rather than globbing, so it cannot
  widen to files it was not meant to touch. If a scope names a file that is
  not on the branch you are deploying, it fails and tells you which — it will
  not push half a change.

`.github/workflows/validate-theme.yml` runs the same validator on every push
and pull request. It needs no secrets.

## Option B — Shopify CLI from your own machine

Needs `npm i -g @shopify/cli@latest`. From the repo root:

```bash
shopify theme list --store bys-user-store-358852-skpnrnec.myshopify.com

shopify theme push \
  --path theme \
  --store bys-user-store-358852-skpnrnec.myshopify.com \
  --theme "Thessvane rebuild" \
  --nodelete \
  --only templates/product.collagen.json \
  --only sections/thessvane-ingredient-callout.liquid \
  --only assets/thessvane-ingredients-placeholder.jpg
```

**Do not run a bare `shopify theme push`.** Without `--only` it uploads every
file in the folder, including `config/settings_data.json` — which holds every
theme-editor setting you have. Any colour, font, or layout tweak you made in
the admin that never came back into this repo would be reverted.

## Option C — no tooling, by hand

Themes → **Thessvane rebuild** → **⋯ → Edit code**. Order matters: the
template references the section, so the section has to exist first.

1. **Assets** → *Add a new asset* → upload
   `theme/assets/thessvane-ingredients-placeholder.jpg`.
2. **Sections** → *Add a new section* → name it
   `thessvane-ingredient-callout` → delete the boilerplate Shopify pre-fills
   → paste the whole file → Save.
3. **Templates** → *Add a new template* → for **product** → type **JSON** →
   name it `collagen` → replace the contents with
   `theme/templates/product.collagen.json` → Save.

## Last step, whichever option you used

An alternate template does nothing until a product points at it:

**Products → PDRN Collagen Stick → Online store → Theme template →
`collagen` → Save.**

Then open the product page and check it on desktop and phone.

## Before customers see it

Two things in the template are placeholder content:

- The **survey percentages** in the "Why People Keep Reordering" section
  (92 / 88 / 94) are illustrative. The section caption says so — swap in your
  own figures or remove the section.
- The **suitability copy** in the FAQ states the collagen is marine-derived
  (not vegan, not for a fish or shellfish allergy) and points pregnant,
  breastfeeding or medicated customers to their doctor. Check it matches your
  actual formula and your market's supplement labelling rules.
