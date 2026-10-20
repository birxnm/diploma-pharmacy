# Experiment results

Task: PHA2-24 · Last updated: 2026-10-20 · Author: Evelina Penkova

Run directories (`<run-id>/config.yaml`, `metrics.json`, `predictions.csv`) are produced locally by the runner scripts in the parent directory and are **not committed**. Only summary tables are committed, as part of the experiment reports (`forecasting/experiments/reports/EXP-<nn>.md`, planned) and of the thesis; each table names the run id and the configuration file it was copied from, so that the run can be repeated with the same command.

Reasons:

- `predictions.csv` grows with the number of items, origins and models (the committed sample already gives 3,600 rows per run; the development set and real data give far more).
- A run is reproducible from its configuration and dataset identifier (NFR-05); the files add nothing that the command cannot regenerate.
- Real data, once available, must not enter the repository (`docs/data/data-specification.md`, section 11), and predictions derived from it belong with the data.

Keep this file and `.gitkeep` tracked so that the directory exists on a fresh clone; the root `.gitignore` ignores `forecasting/experiments/results/*/` (rule added with this task), so local run directories never appear in `git status`.
