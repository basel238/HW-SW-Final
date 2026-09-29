# Publish this reviewed folder

Run the following on the Mac, from the new submission folder. These commands create a new repository and push it to the empty destination requested for this submission. The working project and its history remain separate. No Git commands were executed while preparing this folder.

```bash
cd "/Users/baselsalameh/Documents/Codex/2026-09-19/wha/outputs/HW-SW-Final"
git init -b main
git add .
git commit -m "Submit benchmark optimizations, latest evidence and hardware proposal"
git remote add origin git@github.com:basel238/HW-SW-Final.git
git push -u origin main
```

The `.gitignore` keeps the submitted results, including `perf.data`, and excludes local environments and caches. No included file exceeds GitHub's 100 MiB single-file limit. This is a fresh submission snapshot, not a reconstructed development history. The prompt record documents the work's progression.

To obtain it on the Ubuntu VM after the push:

```bash
cd ~
git clone git@github.com:basel238/HW-SW-Final.git
cd HW-SW-Final
./setup/04_make_venv.sh
./run_all.sh
```

Use an existing harness environment with `VENV_DIR=/path/to/environment` if preferred. New runs create their own timestamped results and do not overwrite the authored reports. See `README.md` for the individual commands that reproduce the saved batch sizes.
