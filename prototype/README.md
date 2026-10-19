# prototype

_PHA2-18 · Last updated: 2026-10-19 · Author: Birkhanym Kazhymukhamet_

Static HTML/CSS mockups of the key **PharmaStock** screens. The mockups are used to agree the layout, the vocabulary and the information on each screen with the team and, later, with pharmacy users before the Vue 3 implementation in [`../frontend/`](../frontend/README.md) starts. They open directly in a browser, need no build step, contain no JavaScript and are not part of the deployed system.

The screens follow the [user scenarios](../docs/ux/user-scenarios.md) and [use cases](../docs/ux/use-cases.md) and use the requirement IDs, entity names and model names of [`docs/requirements.md`](../docs/requirements.md) and [`docs/architecture/`](../docs/architecture/) verbatim.

## How to open

1. Clone the repository (or download the `prototype/` folder).
2. Open `prototype/index.html` in a current desktop browser (Chrome, Firefox or Edge, see NFR-09). Double-clicking the file is enough; the pages are linked to each other through the left navigation.
3. Optionally serve the folder instead, for example `python -m http.server 8080` from `prototype/`, and open `http://localhost:8080/`.

The layout is designed for desktop widths and remains usable down to 1280 px (NFR-09). There is no dark theme.

## Files

| File | Content |
|---|---|
| `styles.css` | Shared stylesheet: colour and spacing tokens as CSS custom properties, sidebar + content layout, cards, tables, risk badges (High / Medium / Low), status pills, buttons, filter and form controls, inline-SVG chart styles. No external CSS framework and no fonts are loaded. |
| `index.html` | Dashboard |
| `risks.html` | Shortage risks (prioritised risk list) |
| `items.html` | Catalogue |
| `item.html` | Item page (sample item `MED-0001` Amoxicillin 500 mg capsules) |

## Screens

| Screen | File | Status | What it shows |
|---|---|---|---|
| Dashboard | `index.html` | available | KPI cards (items tracked, items at high risk, last forecast run, data coverage); table "Top items at risk" with item, current stock, weekly forecast, expected stock-out date and risk badge; notifications for high-risk items; projected-stock chart of one high-risk item as inline SVG; summary of the latest import |
| Risks | `risks.html` | available | Prioritised risk list of run #12 with filters by level (All / High / Medium / Low), group, expected stock-out date and text; columns for expected stock-out date, current stock, weekly forecast, lead time, planned receipts and the gap before the next delivery; "Record delivery" action that opens the planned-receipt form at the bottom of the page; export buttons |
| Catalogue | `items.html` | available | Medicine catalogue with search, group, risk, supplier and status filters; table with code, name, unit, group, primary supplier, lead time, current stock, risk and active flag; an inactive item as example |
| Item page | `item.html` | available | Item card (supplier, lead time, safety stock, current stock, last receipt, planned receipts); shortage-risk card with the projected stock of the next weeks; inline-SVG line chart of 26 weeks of consumption with the forecast dashed, the 80% interval shaded and stock-out weeks hatched; model information box with hold-out MAE / WAPE against the baselines; history table (consumption, closing stock, receipts, stock-out flag); forecast table for the whole horizon |
| Forecast runs | `forecast.html` | planned | Form to start a forecast run; list of previous runs with status |
| Imports | `imports.html` | planned | Upload form for the four import file types; import history with data-quality summary |
| Settings | `settings.html` | planned | Thresholds and safety stock, lead times, users and roles |

The navigation sidebar links all seven screens so that the structure of the interface can be discussed as a whole; links to screens marked *planned* do not resolve yet.

## Sample scenario

All screens show the same fictional situation so that numbers can be followed from one page to another:

- Today is Monday, 19 October 2026. Consumption, stock and receipt exports up to the week of 12 October 2026 were imported on 19 October (batches #27–#29); the history covers 156 weeks (23 Oct 2023 – 12 Oct 2026).
- The catalogue has 31 items, 30 of them active; item codes and names follow the synthetic dataset of `forecasting/data/` (for example `MED-0001` Amoxicillin 500 mg capsules, `MED-0012` Insulin glargine 100 IU/ml 3 ml, `MED-0015` Sodium chloride 0.9% 500 ml). Suppliers are SK-Pharmacy (centralised supply) and two distributors for own purchases.
- Forecast run #12 (19 Oct 2026 10:55, model `sba`, horizon 12 weeks) produced 4 High, 7 Medium and 19 Low risk assessments. Safety stock is one week of forecast consumption; risk levels follow `FR-08`: High if the stock-out is expected within the item's lead time, Medium if within the horizon, Low otherwise.
- Stock levels are the closing quantity on hand of the week; a week with a closing quantity of zero is flagged as a stock-out week (`FR-17`). The sample item Amoxicillin 500 mg capsules has two flagged weeks in July 2026.
- Two high-risk items have a planned delivery that arrives after the expected stock-out (Salbutamol 100 mcg/dose inhaler, Insulin glargine 100 IU/ml 3 ml); the risk list shows the gap before the delivery.

The values are **not** results of the forecasting module and must not be quoted as such; they only illustrate the layout. The hold-out metrics in the model box of the item page are placeholders.

## What is mocked

- **No backend, no data.** Every number, date and name is written into the HTML. Buttons and forms do not do anything; links between pages, the level chips and the "Record delivery" buttons (which scroll to the planned-receipt form) work.
- **No authentication.** Every page shows the same signed-in user (head of pharmacy, role `pharmacist`). A login screen and the `viewer` / `administrator` views (`FR-14`) are not mocked yet.
- **Charts** are hand-drawn inline SVG, not rendered from data. The Vue implementation will use Chart.js.
- **Notifications** (`FR-12`) are shown as a card on the dashboard and as a counter in the navigation; there is no separate notification page.
- **One sample item page.** Every item link opens the same page, `item.html`, which shows Amoxicillin 500 mg capsules.
- **Risk levels are always labelled with text** (High / Medium / Low) next to the colour, so that the level is readable without colour vision.

## Next steps

- Add the remaining screens listed above (PHA2-18, next snapshot): forecast runs, imports, settings.
- Map every screen to the functional requirements it covers and record it in this file.
- Walk through the mockups with the team and, when the discussions D-1 to D-5 take place, with pharmacy staff; record findings in [`docs/evidence-of-relevance/interview-log.md`](../docs/evidence-of-relevance/interview-log.md).

Related tasks: this folder is produced under Linear issue PHA2-18 ([Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b), link will be added when the instance is confirmed).
