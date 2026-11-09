# Branding and Assets

## Official logo files

The official user-supplied files are stored at:

- `static/assets/branding/CHORD_Logo.png`
- `static/assets/branding/CHORD Logo.svg`

They were not generated, redrawn, recolored, or edited.

## Verification

| Asset | Verified properties |
| --- | --- |
| PNG | 2106 × 954, 8-bit RGBA, alpha transparency present, 188,155 bytes |
| SVG | Valid SVG root, 2000 × 2000 with square viewBox, no scripts, no external HTTP image references, six embedded raster image layers |

Both assets were discovered by Django staticfiles and returned HTTP 200 from
the development server with the correct content types.

## Integration decision

The audited Figma sidebar referenced the horizontal PNG asset. Phase 7.2 uses
that exact file through Django's `{% static %}` tag in the reusable brand
partial for both the application sidebar and authentication layout. Explicit
intrinsic dimensions and CSS `height: auto` preserve its 2.21:1 proportions and
transparency.

The SVG is preserved as an official source asset but is not substituted into
the narrow shell slot. Its square export and embedded raster composition do not
match the audited horizontal slot as reliably as the PNG. A future cleaned,
true-vector horizontal export may replace the PNG only with design approval.

## Version-control status

- `static/` is not ignored; only collected `staticfiles/` is ignored.
- The official branding files, CHORD CSS, and shell JavaScript are intentional
  source assets and can be version-controlled.
- `static/` remains untracked in the current working tree because no `git add`
  or commit was performed. The user must review and authorize any commit.
- Secrets, uploads, collected assets, and generated browser screenshots are not
  included in `static/`.

See [[Design-System]], [[Design-Change-Log]], and [[Known-Issues]].
