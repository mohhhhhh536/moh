#!/usr/bin/env node
/*
 * Inserts the Thessvane Brand Quote and Questions Answered sections into a
 * homepage template, leaving every other section in that template untouched.
 *
 * Usage, from the theme directory after pulling the live homepage:
 *   shopify theme pull --store <store> --theme <id> --only templates/index.json
 *   node ../scripts/add-homepage-sections.js templates/index.json
 *   shopify theme push --store <store> --theme <id> --nodelete --only templates/index.json
 *
 * Running it twice is safe: sections already present are left alone.
 */

const fs = require('fs');
const path = require('path');

const target = process.argv[2];
if (!target) {
  console.error('Usage: node add-homepage-sections.js <path to templates/index.json>');
  process.exit(1);
}
if (!fs.existsSync(target)) {
  console.error(`Not found: ${target}`);
  process.exit(1);
}

const source = JSON.parse(
  fs.readFileSync(path.join(__dirname, 'homepage-sections.json'), 'utf8')
);
const template = JSON.parse(fs.readFileSync(target, 'utf8'));

if (!template.sections || !Array.isArray(template.order)) {
  console.error(`${target} does not look like a section template (no sections/order).`);
  process.exit(1);
}

// Where in template.order a new section should go, given its placement rules.
// Prefer sitting before a named section type; otherwise sit after one; otherwise
// fall back to the end of the page.
function placementIndex(rules) {
  const typeAt = (id) => (template.sections[id] || {}).type;

  for (const type of rules.before_type || []) {
    const at = template.order.findIndex((id) => typeAt(id) === type);
    if (at !== -1) return { index: at, reason: `before the ${type} section` };
  }
  for (const type of rules.after_type || []) {
    let at = -1;
    template.order.forEach((id, i) => {
      if (typeAt(id) === type) at = i;
    });
    if (at !== -1) return { index: at + 1, reason: `after the ${type} section` };
  }
  return { index: template.order.length, reason: 'at the end of the page' };
}

let added = 0;
for (const [key, definition] of Object.entries(source.sections)) {
  if (template.sections[key] || template.order.some((id) => (template.sections[id] || {}).type === definition.type)) {
    console.log(`- ${definition.type}: already on this homepage, left as is`);
    continue;
  }
  const { index, reason } = placementIndex(source.placement[key] || {});
  template.sections[key] = definition;
  template.order.splice(index, 0, key);
  console.log(`+ ${definition.type}: inserted ${reason} (position ${index + 1} of ${template.order.length})`);
  added += 1;
}

if (added === 0) {
  console.log('\nNothing to do — both sections are already on the homepage.');
  process.exit(0);
}

// Only taken once there is something to write, so a repeat run can't overwrite
// the backup holding the original homepage.
const backup = `${target}.bak`;
fs.copyFileSync(target, backup);
fs.writeFileSync(target, JSON.stringify(template));
console.log(`\nUpdated ${target} (previous version saved as ${path.basename(backup)}).`);
console.log('Every other section on the page was left untouched.');
