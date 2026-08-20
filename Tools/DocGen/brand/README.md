# OpenVVVF brand assets

Deterministic generators for the OpenVVVF wordmark and icon. The generated
assets used by the site/PDF pipeline live in `../src/docgen/templates/brand/`.

**Single source of truth:** the wordmark is typeset from the vendored Saira
fonts by `openvvvf_wordmark_gen.py`. Every logo asset (site header, footer,
PDF cover, stamped PDF footer) is generated from this one script; do not
add traced or hand-drawn variants.

Regenerate the wordmark variants (Pillow + numpy only):

    # Brand red (site header, footer, PDF cover)
    python openvvvf_wordmark_gen.py --png ../src/docgen/templates/brand/logo.png \
        --width 1600 --transparent

    # Black, for light backgrounds where red does not fit
    python openvvvf_wordmark_gen.py --png ../src/docgen/templates/brand/logo-bw.png \
        --width 1600 --color "#1a1a1a" --transparent

    # Light grey, used for the stamped PDF running footer
    python openvvvf_wordmark_gen.py --png ../src/docgen/templates/brand/logo-grey.png \
        --width 1600 --color "#9ca3af" --transparent

Use `--color "#FC0F27"` (default brand red) or another hex color for variants.
`openvvvf_icon_gen.py` produces the app-icon set (favicons, `icon.svg`); it
uses the same Saira fonts and wordmark geometry.

Fonts: Saira (SIL Open Font License), vendored under `openvvvf-brand-fonts/`
and `../src/docgen/templates/brand/fonts/`. Brand red: `#FC0F27`.
