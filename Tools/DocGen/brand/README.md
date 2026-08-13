# OpenVVVF brand assets

Deterministic generators for the OpenVVVF wordmark and icon. The generated
assets used by the site/PDF pipeline live in `../src/docgen/templates/brand/`.

Regenerate the wordmark (Pillow only, no other deps):

    python openvvvf_logo_gen.py --svg ../src/docgen/templates/brand/logo.svg \
        --png ../src/docgen/templates/brand/logo.png --width 1600

Use `--color "#FC0F27"` (default brand red) or another hex color for variants.
`openvvvf_icon_gen.py` produces the app-icon set (favicons, `icon.svg`).

Fonts: Saira (SIL Open Font License), vendored under
`templates/brand/fonts/`. Brand red: `#FC0F27`.
