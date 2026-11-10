"""Fail clearly when the pinned WebKit browser or its OS libraries are absent."""
import sys
from playwright.sync_api import sync_playwright


def launch_webkit(pw):
    try:
        return pw.webkit.launch()
    except Exception as exc:
        raise RuntimeError(
            'WebKit is required (no Chromium fallback). Run bash scripts/cloud/setup.sh; '
            'or python -m playwright install --with-deps webkit with OS-package privileges. '
            f'Original launch error: {exc}'
        ) from exc


if __name__ == '__main__':
    try:
        with sync_playwright() as pw:
            with launch_webkit(pw) as browser:
                page = browser.new_page(**pw.devices['iPad (gen 7)'])
                page.set_content('<title>webkit-ready</title>')
                assert page.title() == 'webkit-ready'
                print(f'WebKit launch OK: {browser.version}, iPad (gen 7)')
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
