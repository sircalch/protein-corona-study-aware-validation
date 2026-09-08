# Visual style guide

## System

Figures use Arial or a compatible sans-serif fallback, 8-12 pt final lettering, panel labels in bold uppercase, 0.8-1.35 pt axes and data lines, and 4-5 pt markers. Artwork is white-background, flat, and free of gradients, shadows, decorative icons, and generated imagery. Captions, not artwork titles, provide the complete interpretation.

| Element | Specification | Meaning |
| --- | --- | --- |
| LR | `#0072B2` | Logistic regression |
| RF | `#D55E00` | Random forest |
| Prevalence | `#6E6E6E` | Training-prevalence baseline |
| RANDOM | Open circle; when needed, same-study colored blocks | Sample-random validation |
| GROUP_STUDY | Diamond; whole conceptual study blocks on one side | Matched-size primary comparison |
| LOSO | Filled square; one conceptual study in test | Complementary unseen-study comparison |
| Conditional interval | Horizontal capped bar | 95% conditional study-bootstrap percentile interval |
| Zero reference | Charcoal line | No BSS advantage or no Brier-loss difference |
| Supplement | Same palette and typography, with restrained neutral fills | Diagnostic or feasibility content |

Color carries model identity only when paired with marker shape and open/filled treatment, preserving interpretation after grayscale conversion. Every diagram that depicts allocations is explicitly conceptual and does not encode observations.

## Production

Each figure is generated only by `scripts/generate_final_figures.py` from copied frozen source files. Every final figure is exported as editable SVG, vector PDF, 600 dpi PNG, and 600 dpi LZW-compressed TIFF. `FIGURE_PROVENANCE.csv` records the displayed source, transformation, script, output and QC status.
