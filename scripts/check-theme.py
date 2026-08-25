#!/usr/bin/env python3
"""Validate the Shopify theme before it is pushed to a store.

Shopify rejects a theme upload for things that are easy to miss by eye: a
section schema that isn't valid JSON, a section name over the 25 character
limit, a `url` setting carrying a default. It will also happily accept a
JSON template that references a setting no schema declares, and then render
the section blank.

This checks all of that. Vendor sections that shipped with the theme are
parsed (so templates can be validated against them) but not linted, since
their pre-existing warts are not ours to fix and would drown out real
findings. Sections we wrote are linted in full.

Usage:
    python3 scripts/check-theme.py [--theme-root theme] [--lint-prefix thessvane-]
"""

import argparse
import glob
import json
import os
import re
import sys

SECTION_NAME_MAX = 25
SCHEMA_RE = re.compile(r'\{%\s*schema\s*%\}(.*?)\{%\s*endschema\s*%\}', re.S)


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def setting_ids(settings):
    return {s['id'] for s in settings if 'id' in s}


def check_section(path, report, lint):
    """Parse a section's schema. Returns the schema, or None if it has none."""
    src = open(path, encoding='utf-8').read()
    match = SCHEMA_RE.search(src)
    if not match:
        return None

    try:
        schema = json.loads(match.group(1))
    except ValueError as exc:
        if lint:
            report.error(f"{path}: schema is not valid JSON: {exc}")
        return None

    name = schema.get('name', '')
    # Translation keys are resolved at runtime, so the limit only binds literals.
    if not name.startswith('t:') and len(name) > SECTION_NAME_MAX:
        report.error(
            f"{path}: section name {name!r} is {len(name)} characters; "
            f"Shopify allows {SECTION_NAME_MAX}"
        )

    section_ids = setting_ids(schema.get('settings', []))
    block_ids = {
        b['type']: setting_ids(b.get('settings', []))
        for b in schema.get('blocks', [])
    }

    if not lint:
        return schema

    every_setting = schema.get('settings', []) + [
        s for b in schema.get('blocks', []) for s in b.get('settings', [])
    ]
    for setting in every_setting:
        if setting.get('type') == 'url' and 'default' in setting:
            report.error(
                f"{path}: url setting {setting.get('id')!r} has a default, "
                "which Shopify rejects on upload"
            )
        default = setting.get('default')
        if setting.get('type') in ('text', 'textarea') and isinstance(default, str):
            if default.startswith('<'):
                report.warn(
                    f"{path}: {setting.get('id')!r} is a text setting but its "
                    "default looks like HTML; use richtext instead"
                )

    body = src[: match.start()]
    for ref in sorted(set(re.findall(r'section\.settings\.([a-zA-Z0-9_]+)', body))):
        if ref not in section_ids:
            report.error(f"{path}: renders section.settings.{ref}, undeclared in schema")
    for ref in sorted(set(re.findall(r'block\.settings\.([a-zA-Z0-9_]+)', body))):
        if not any(ref in ids for ids in block_ids.values()):
            report.error(f"{path}: renders block.settings.{ref}, declared by no block")

    for preset in schema.get('presets', []):
        for block in preset.get('blocks', []):
            if block.get('type') not in block_ids:
                report.error(
                    f"{path}: preset uses block type {block.get('type')!r}, "
                    "which the schema does not define"
                )

    return schema


def check_template(path, schemas, report):
    try:
        data = json.load(open(path, encoding='utf-8'))
    except ValueError as exc:
        report.error(f"{path}: not valid JSON: {exc}")
        return

    sections = data.get('sections', {})
    for key, section in sections.items():
        schema = schemas.get(section.get('type'))
        if schema is None:
            # An app block, or a section Shopify provides rather than the repo.
            continue

        section_ids = setting_ids(schema.get('settings', []))
        block_ids = {
            b['type']: setting_ids(b.get('settings', []))
            for b in schema.get('blocks', [])
        }

        for name in section.get('settings', {}):
            if name not in section_ids:
                report.error(
                    f"{path} [{key}]: sets {name!r}, not a setting of "
                    f"{section['type']}"
                )

        for block_key, block in section.get('blocks', {}).items():
            block_type = block.get('type')
            if block_type not in block_ids:
                report.error(
                    f"{path} [{key}]: block type {block_type!r} is not defined "
                    f"by {section['type']}"
                )
                continue
            for name in block.get('settings', {}):
                if name not in block_ids[block_type]:
                    report.error(
                        f"{path} [{key}/{block_key}]: sets {name!r}, not a "
                        f"setting of {section['type']}.{block_type}"
                    )

        for block_key in section.get('block_order', []):
            if block_key not in section.get('blocks', {}):
                report.error(
                    f"{path} [{key}]: block_order lists {block_key!r}, "
                    "which has no block"
                )

    for key in data.get('order', []):
        if key not in sections:
            report.error(f"{path}: order lists {key!r}, which has no section")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--theme-root', default='theme',
                        help="directory holding sections/, templates/, etc.")
    parser.add_argument('--lint-prefix', default='thessvane-',
                        help="only fully lint sections whose filename starts with this")
    args = parser.parse_args()

    root = args.theme_root
    if not os.path.isdir(os.path.join(root, 'sections')):
        print(f"error: {root!r} does not look like a theme directory", file=sys.stderr)
        return 2

    report = Report()
    schemas = {}
    for path in sorted(glob.glob(os.path.join(root, 'sections', '*.liquid'))):
        lint = os.path.basename(path).startswith(args.lint_prefix)
        schema = check_section(path, report, lint)
        if schema is not None:
            schemas[os.path.basename(path)[: -len('.liquid')]] = schema

    templates = sorted(glob.glob(os.path.join(root, 'templates', '*.json')))
    templates += sorted(glob.glob(os.path.join(root, 'templates', '*', '*.json')))
    templates += sorted(glob.glob(os.path.join(root, 'sections', '*.json')))
    for path in templates:
        check_template(path, schemas, report)

    for warning in report.warnings:
        print(f"warning: {warning}")
    for error in report.errors:
        print(f"error: {error}")

    print(
        f"\n{len(schemas)} section schemas, {len(templates)} templates checked "
        f"— {len(report.errors)} errors, {len(report.warnings)} warnings"
    )
    return 1 if report.errors else 0


if __name__ == '__main__':
    sys.exit(main())
