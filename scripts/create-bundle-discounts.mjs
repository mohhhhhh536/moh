#!/usr/bin/env node
// Create the two automatic Buy X Get Y discounts that make the product page's
// bundle tiers real.
//
// The theme only *displays* a bundle price. Shopify calculates what a customer
// actually pays, so without these the page advertises a saving the checkout
// does not honour.
//
// Setup (one time):
//   Shopify admin -> Settings -> Apps and sales channels -> Develop apps
//     -> Create an app -> Configure Admin API scopes -> tick write_discounts
//        and read_products -> Save -> Install app -> reveal the Admin API
//        access token (starts shpat_)
//
// Usage:
//   export SHOPIFY_STORE=bys-user-store-358852-skpnrnec.myshopify.com
//   export SHOPIFY_ADMIN_TOKEN=shpat_xxxxxxxx
//   node scripts/create-bundle-discounts.mjs --dry-run
//   node scripts/create-bundle-discounts.mjs

const store = process.env.SHOPIFY_STORE;
const token = process.env.SHOPIFY_ADMIN_TOKEN;
const dryRun = process.argv.includes('--dry-run');
const titleArg = process.argv.find((a) => a.startsWith('--product='));
const productTitle = titleArg ? titleArg.slice(10) : 'PDRN Collagen Stick';

// Buy X get Y: the customer buys X and receives Y more free.
const TIERS = [
  { title: `Buy 2 Get 1 Free — ${productTitle}`, buy: 2, get: 1 },
  { title: `Buy 3 Get 2 Free — ${productTitle}`, buy: 3, get: 2 },
];

function die(msg) {
  console.error(`\n  ${msg}\n`);
  process.exit(1);
}

if (!store) die('SHOPIFY_STORE is not set.');
if (!token && !dryRun) die('SHOPIFY_ADMIN_TOKEN is not set. A theme token (shptka_) will not work here — this needs an Admin API token (shpat_).');

// Pin nothing: ask the store which API versions it supports and take the
// newest stable one, so this keeps working as versions roll forward.
async function latestApiVersion() {
  const res = await fetch(`https://${store}/admin/api/api_versions.json`, {
    headers: { 'X-Shopify-Access-Token': token },
  });
  if (!res.ok) die(`Could not read API versions (HTTP ${res.status}). Check the store domain and token.`);
  const { api_versions: versions } = await res.json();
  const stable = versions.filter((v) => v.handle !== 'unstable').map((v) => v.handle).sort();
  if (!stable.length) die('The store reported no stable API versions.');
  return stable[stable.length - 1];
}

async function graphql(version, query, variables) {
  const res = await fetch(`https://${store}/admin/api/${version}/graphql.json`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Shopify-Access-Token': token },
    body: JSON.stringify({ query, variables }),
  });
  const body = await res.json();
  if (body.errors) die(`GraphQL error: ${JSON.stringify(body.errors, null, 2)}`);
  return body.data;
}

const FIND_PRODUCT = `query($q: String!) {
  products(first: 10, query: $q) { edges { node { id title status } } }
}`;

const EXISTING = `query($q: String!) {
  automaticDiscountNodes(first: 50, query: $q) {
    edges { node { id automaticDiscount { ... on DiscountAutomaticBxgy { title } } } }
  }
}`;

const CREATE = `mutation($d: DiscountAutomaticBxgyInput!) {
  discountAutomaticBxgyCreate(automaticBxgyDiscount: $d) {
    automaticDiscountNode { id }
    userErrors { field message }
  }
}`;

function discountInput(tier, productId) {
  return {
    title: tier.title,
    startsAt: new Date().toISOString(),
    usesPerOrderLimit: '1', // stops one tier consuming the cart the other should win
    customerBuys: {
      value: { quantity: String(tier.buy) },
      items: { products: { productsToAdd: [productId] } },
    },
    customerGets: {
      value: {
        discountOnQuantity: {
          quantity: String(tier.get),
          effect: { percentage: 1.0 }, // 1.0 == 100% off == free
        },
      },
      items: { products: { productsToAdd: [productId] } },
    },
  };
}

const main = async () => {
  if (dryRun) {
    console.log(`\nDry run — nothing will be sent to ${store}.\n`);
    for (const tier of TIERS) {
      console.log(`${tier.title}`);
      console.log(JSON.stringify(discountInput(tier, 'gid://shopify/Product/<resolved at run time>'), null, 2));
      console.log();
    }
    return;
  }

  const version = await latestApiVersion();
  console.log(`Store        : ${store}`);
  console.log(`API version  : ${version}`);

  const found = await graphql(version, FIND_PRODUCT, { q: `title:'${productTitle}'` });
  const matches = found.products.edges.map((e) => e.node);
  if (!matches.length) die(`No product titled "${productTitle}". Pass --product="Exact Title".`);
  if (matches.length > 1) {
    die(`"${productTitle}" matched ${matches.length} products:\n` +
        matches.map((m) => `    ${m.title}  (${m.id})`).join('\n') +
        `\n  Re-run with --product="Exact Title".`);
  }
  const product = matches[0];
  console.log(`Product      : ${product.title}  (${product.id}, ${product.status})`);

  for (const tier of TIERS) {
    const existing = await graphql(version, EXISTING, { q: `title:'${tier.title}'` });
    const already = existing.automaticDiscountNodes.edges
      .some((e) => e.node.automaticDiscount?.title === tier.title);
    if (already) {
      console.log(`  skipped, already exists : ${tier.title}`);
      continue;
    }
    const out = await graphql(version, CREATE, { d: discountInput(tier, product.id) });
    const { automaticDiscountNode, userErrors } = out.discountAutomaticBxgyCreate;
    if (userErrors.length) {
      console.error(`  FAILED  : ${tier.title}`);
      for (const e of userErrors) console.error(`      ${e.field?.join('.') || ''} ${e.message}`);
      process.exitCode = 1;
      continue;
    }
    console.log(`  created : ${tier.title}  (${automaticDiscountNode.id})`);
  }

  console.log(`\nNow test before publishing:`);
  console.log(`  add 3 to the cart -> should charge 2x unit price`);
  console.log(`  add 5 to the cart -> should charge 3x unit price, not 4x\n`);
};

main().catch((e) => die(e.stack || String(e)));
