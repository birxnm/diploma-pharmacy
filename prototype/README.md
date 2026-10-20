# prototype

_PHA2-18 · Last updated: 2026-10-20 · Author: Birkhanym Kazhymukhamet_

Static HTML/CSS mockups of the key **PharmaStock** screens. The mockups are used to agree the layout, the vocabulary and the information on each screen with the team and, later, with pharmacy users before the Vue 3 implementation in [`../frontend/`](../frontend/README.md) starts. They open directly in a browser, need no build step, contain no JavaScript and are not part of the deployed system.

The screens follow the [user scenarios](../docs/ux/user-scenarios.md) and [use cases](../docs/ux/use-cases.md) and use the requirement IDs, entity names and model names of [`docs/requirements.md`](../docs/requirements.md) and [`docs/architecture/`](../docs/architecture/) verbatim.

## How to open

1. Clone the repository (or download the `prototype/` folder).
2. Open `prototype/index.html` in a current desktop browser (Chrome, Firefox or Edge, see NFR-09). Double-clicking the file is enough; the pages are linked to each other through the left navigation, and every internal link resolves to a file in this folder.
3. Optionally serve the folder instead, for example `python -m http.server 8080` from `prototype/`, and open `http://localhost:8080/`.

The layout is designed for desktop widths and remains usable down to 1280 px (NFR-09). There is no dark theme.

## Files

| File | Content |
|---|---|
| `styles.css` | Shared stylesheet: colour and spacing tokens as CSS custom properties, sidebar + content layout, cards, tables, risk badges (High / Medium / Low), status pills, buttons, filter and form controls, inline-SVG chart styles. No external CSS framework and no fonts are loaded. |
| `index.html` | Dashboard |
| `risks.html` | Shortage risks (prioritised risk list) and the "Record delivery" form |
| `items.html` | Catalogue |
| `item.html` | Item page (sample item `MED-0001` Amoxicillin 500 mg capsules) |
| `forecast.html` | Forecast runs |
| `imports.html` | Imports |
| `settings.html` | Settings: thresholds, suppliers and lead times, users and roles, audit log |

## Screens

| Screen | File | What it shows |
|---|---|---|
| Dashboard | `index.html` | KPI cards (items tracked, items at high risk, last forecast run, data coverage); table "Top items at risk" with item, current stock, weekly forecast, expected stock-out date and risk badge; notifications for high-risk items; projected-stock chart of one high-risk item as inline SVG; summary of the latest import |
| Risks | `risks.html` | Prioritised risk list of run #12 with filters by level (All / High / Medium / Low), group, expected stock-out date and text; columns for expected stock-out date, current stock, weekly forecast, lead time, planned receipts and the gap before the next delivery; "Record delivery" action that opens the planned-receipt form at the bottom of the page; export buttons |
| Catalogue | `items.html` | Medicine catalogue with search, group, risk, supplier and status filters; table with code, name, unit, group, primary supplier, lead time, current stock, risk and active flag; an inactive item as example |
| Item page | `item.html` | Item card (supplier, lead time, safety stock, current stock, last receipt, planned receipts); shortage-risk card with the projected stock of the next weeks; inline-SVG line chart of 26 weeks of consumption with the forecast dashed, the 80% interval shaded and stock-out weeks hatched; model information box with hold-out MAE / WAPE against the baselines; history table (consumption, closing stock, receipts, stock-out flag); forecast table for the whole horizon |
| Forecast runs | `forecast.html` | Form to start a run (item scope, horizon, model, interval, handling of stock-out weeks, data cut-off, fixed seed); summary of the latest run; table of previous runs with status, including a failed run with the validation message; model comparison on the hold-out period |
| Imports | `imports.html` | Upload form for the four file types (`consumption.csv`, `stock.csv`, `receipts.csv`, `planned_receipts.csv`) with the expected columns; validation report of a rejected batch (missing column, negative quantity, unknown item, duplicate period, outlier warning); data-quality summary of a completed batch (coverage, gaps, outliers, stock-out weeks); import history |
| Settings | `settings.html` | Thresholds and safety-stock form with the fixed risk-level definitions; suppliers and lead times per item; users and roles with the permission summary; audit-log excerpt |

## Screens and functional requirements

Which requirement of [`docs/requirements.md`](../docs/requirements.md) each screen illustrates. "Primary" means the screen is where the requirement is mainly exercised; "shown" means the screen displays its result.

| Requirement | Primary screen | Also shown on |
|---|---|---|
| FR-01 Import consumption, stock and receipt data from CSV/XLSX files | `imports.html` (upload form, four file types) | `index.html` (latest import) |
| FR-02 Validate imported data and report errors: missing columns, negative quantities, unknown items, duplicate periods | `imports.html` (validation report of batch #26) | — |
| FR-03 Maintain the medicine catalogue: code, name, unit, group, active flag | `items.html` | `imports.html` ("create missing items" option) |
| FR-04 Maintain suppliers and lead times per item | `settings.html` (suppliers, lead times per item) | `items.html`, `item.html`, `risks.html` (lead time columns) |
| FR-05 View current stock and consumption history per item as table and chart | `item.html` (history table and chart) | `items.html`, `index.html` (current stock) |
| FR-06 Run a forecast for all or selected items for a configurable horizon | `forecast.html` (new run form) | `index.html`, `risks.html` ("Run forecast" buttons) |
| FR-07 View the forecast per item together with history, point forecast, interval and model information | `item.html` (chart, forecast table, model box) | — |
| FR-08 Calculate shortage risk per item from forecast, current stock, planned receipts and lead time | `risks.html` | `item.html` (projected stock), `index.html` (chart), `settings.html` (risk-level definitions) |
| FR-09 Show a prioritised list of items at risk with risk level and expected stock-out date | `risks.html` | `index.html` (top items at risk) |
| FR-10 Record planned deliveries (expected receipts) | `risks.html` ("Record delivery" form) | `item.html` (planned receipts), `imports.html` (`planned_receipts.csv`) |
| FR-11 Configure risk thresholds and safety-stock parameters | `settings.html` (thresholds form) | `risks.html` (link to thresholds) |
| FR-12 Generate in-app notifications for high-risk items | `index.html` (notifications card, counter in the navigation) | `forecast.html` (notification option), `settings.html` (notification level) |
| FR-13 Export forecast and risk reports to CSV/XLSX | `risks.html` (Export CSV / XLSX) | `item.html`, `forecast.html`, `items.html` (export buttons) |
| FR-14 Authenticate users and manage roles: administrator, pharmacist, viewer | `settings.html` (users, permissions by role) | every page (signed-in user and role in the sidebar) |
| FR-15 Keep an audit log of imports, forecast runs and configuration changes | `settings.html` (audit log excerpt) | `imports.html`, `forecast.html`, `risks.html` (audit notes) |
| FR-16 Compare forecasting models against baselines on a hold-out period and show MAE and WAPE | `forecast.html` (model comparison) | `item.html` (per-item comparison in the model box) |
| FR-17 Flag stock-out periods so that zero consumption during a stock-out is treated as censored demand | `item.html` (flagged week in the history table and the hatched band in the chart) | `imports.html` (stock-out weeks in the summary), `forecast.html` (handling option), `index.html` (data coverage) |
| FR-18 Show a data-quality summary per import: coverage, gaps, outliers | `imports.html` (data-quality summary) | `index.html` (latest import card) |

Non-functional requirements visible in the mockups: NFR-03 (users table: hashed passwords, role-based access), NFR-04 (notes on the import form), NFR-05 (fixed seed and configuration hash on the forecast pages), NFR-06 (failed run with a validation message), NFR-09 (layout checked at 1440 px and 1280 px in Chrome).

Not mocked: the login screen (FR-14), the separate notification list (FR-12, only the counter and the dashboard card are shown), the `viewer` and `administrator` variants of the pages, and the Russian localisation (NFR-10).

## Sample scenario

All screens show the same fictional situation so that numbers can be followed from one page to another:

- Today is Monday, 19 October 2026. Consumption, stock and receipt exports up to the week of 12 October 2026 were imported on 19 October (batches #27–#29, after batch #26 was rejected); the history covers 156 weeks (23 Oct 2023 – 12 Oct 2026).
- The catalogue has 31 items, 30 of them active; item codes and names follow the synthetic dataset of `forecasting/data/` (for example `MED-0001` Amoxicillin 500 mg capsules, `MED-0012` Insulin glargine 100 IU/ml 3 ml, `MED-0015` Sodium chloride 0.9% 500 ml). Suppliers are SK-Pharmacy (centralised supply) and two distributors for own purchases.
- Forecast run #12 (19 Oct 2026 10:55, model `sba`, horizon 12 weeks, seed 42) produced 4 High, 7 Medium and 19 Low risk assessments. Safety stock is one week of forecast consumption; risk levels follow `FR-08`: High if the stock-out is expected within the item's lead time, Medium if within the horizon, Low otherwise.
- Stock levels are the closing quantity on hand of the week; a week with a closing quantity of zero is flagged as a stock-out week (`FR-17`). The sample item Amoxicillin 500 mg capsules has two flagged weeks in July 2026.
- Two high-risk items have a planned delivery that arrives after the expected stock-out (Salbutamol 100 mcg/dose inhaler, Insulin glargine 100 IU/ml 3 ml); the risk list shows the gap before the delivery.
- The users on the settings page are fictional sample accounts on an example domain.

The values are **not** results of the forecasting module and must not be quoted as such; they only illustrate the layout. The hold-out metrics on the item page and on the forecast page are placeholders.

## What is mocked

- **No backend, no data.** Every number, date and name is written into the HTML. Buttons and forms do not do anything; links between pages, the level chips, the section links on the settings page and the "Record delivery" buttons (which scroll to the planned-receipt form) work.
- **No authentication.** Every page shows the same signed-in user (head of pharmacy, role `pharmacist`); on the settings page the administrator-only parts are shown read-only. A login screen and the `viewer` / `administrator` views (`FR-14`) are not mocked.
- **Charts** are hand-drawn inline SVG, not rendered from data. The Vue implementation will use Chart.js.
- **Notifications** (`FR-12`) are shown as a card on the dashboard and as a counter in the navigation; there is no separate notification page.
- **One sample item page.** Every item link opens the same page, `item.html`, which shows Amoxicillin 500 mg capsules.
- **Risk levels are always labelled with text** (High / Medium / Low) next to the colour, so that the level is readable without colour vision.

## Next steps

- Walk through the mockups with the team at the weekly meeting and collect remarks per screen as Linear sub-tasks of PHA2-18.
- When the discussions D-1 to D-5 take place, use the mockups as the basis of the questions on the risk list and the item page; record findings in [`docs/evidence-of-relevance/interview-log.md`](../docs/evidence-of-relevance/interview-log.md).
- Start the Vue 3 scaffold in `../frontend/` from the agreed screens (dashboard, risk list and item page first).

Related tasks: this folder is produced under Linear issue PHA2-18 ([Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b), link will be added when the instance is confirmed).
