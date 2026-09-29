# Reports and figures

The required submission files are `report_raytrace.txt` and `report_nbody.txt` at the repository root. The PDFs here contain the same reviewed narrative and tables, plus readable plots, flame-graph previews and a block diagram. Both follow the six required report sections.

- `raytrace_source.json` and `nbody_source.json`: reviewed report content.
- `report_raytrace.pdf` and `report_nbody.pdf`: 12 pages each.
- `assets/`: static overviews of the latest raw flame graphs. Frame coordinates and colors are preserved; SVG titles/UI are omitted because historical captions mislabel the sampling setting. Open original SVGs in `results/` to search and zoom.

From the repository root, regenerate after deliberately editing the reviewed content:

```bash
python3 -m pip install -r requirements-docs.txt
python3 tools/render_flame_previews.py
python3 tools/build_reports.py
```

These commands rebuild figures, PDFs and required TXT files. They do not run benchmarks, infer new findings, or replace the report content with a new measurement. View rendered PDF pages after any substantive edit. Hardware animation links in the PDFs target files relative to this folder; open the HTML files directly from `hardware/diagrams/` if a PDF viewer blocks local links.
