# User scenarios

_PHA2-13 · Last updated: 2026-10-17 · Author: Birkhanym Kazhymukhamet_

This document describes how the target users of **PharmaStock** are expected to work with the system, written as narrative scenarios. The scenarios are derived from the problem statement in the [project proposal](../proposal.md) and from the stakeholder map in [evidence-of-relevance/stakeholders.md](../evidence-of-relevance/stakeholders.md). They are the team's current understanding of pharmacy work and remain **assumptions** until they are checked in the planned discussions D-1 to D-5 (see the [interview log](../evidence-of-relevance/interview-log.md)); each scenario ends with the questions that the discussions must answer. The use cases derived from these scenarios will be documented in [use-cases.md](./use-cases.md) (planned under the same task).

## 1. Purpose and conventions

The scenarios have three uses in the project:

1. they justify and explain the functional requirements `FR-01`...`FR-18` in [requirements.md](../requirements.md) by showing where each requirement is needed in real work;
2. they are the basis of the UX mockups in `prototype/` and of the screen list of the web interface;
3. they become the scripts of the user testing planned in the [verification and evaluation plan](../verification-and-evaluation-plan.md).

Conventions used below:

- **Actor** is a stakeholder from the stakeholder map (`S1`...`S5`) together with the system role that the person has in PharmaStock: `pharmacist`, `viewer` or `administrator` (`FR-14`).
- **Trigger** is the event or moment that starts the scenario.
- **Steps** alternate between what the user does and how PharmaStock responds. A step that depends on an open design decision says so.
- **Expected result** states what the user has achieved at the end and how it differs from today's spreadsheet-based work.
- **Requirements** lists the IDs exercised by the scenario, using the wording of `requirements.md`.
- Item names, quantities and dates in the scenarios are illustrative. They follow the structure of the documented synthetic dataset and do not describe any real organization.
- All scenarios assume the initial decisions of the project: weekly time step, 12-week forecast horizon, data imported from CSV/XLSX exports of the accounting system, no patient data of any kind (`NFR-04`).

## 2. Actors

| Actor | Stakeholder | System role | What the actor wants from PharmaStock |
|---|---|---|---|
| Head of hospital pharmacy | S1 | `pharmacist` | See early which items will run out and when; justify orders; set the rules (thresholds, safety stock) the pharmacy works by |
| Pharmacist | S2 | `pharmacist` | Load the monthly exports without manual rework; check data quality; review stock and forecasts per item |
| Procurement and supply specialist | S3 | `pharmacist` (access to planned receipts; a narrower role is an open question) | Know which items are at risk before the ordering deadline; record confirmed deliveries and see whether they close the gap |
| Head of clinical department | S4 | `viewer` | See whether the medicines the department uses will be available in the coming weeks |
| IT administrator of the organization | S5 | `administrator` | Create and deactivate users, assign roles, review who did what |

## 3. Scenario overview

| ID | Scenario | Primary actor | Frequency | Requirements |
|---|---|---|---|---|
| S-01 | Weekly stock review | Head of pharmacy / pharmacist | Weekly | FR-05, FR-06, FR-07, FR-09, FR-16, FR-17 |
| S-02 | Importing the monthly export | Pharmacist | Monthly (or after each export) | FR-01, FR-02, FR-03, FR-15, FR-17, FR-18 |
| S-03 | Reacting to a high-risk alert | Pharmacist; procurement specialist; department head | When a forecast run produces high-risk items | FR-07, FR-08, FR-09, FR-12, FR-13, FR-14 |
| S-04 | Planning a delivery | Procurement specialist | When a delivery date is confirmed | FR-04, FR-08, FR-09, FR-10, FR-15 |
| S-05 | Configuring thresholds | Head of pharmacy | At set-up and at periodic reviews | FR-08, FR-11, FR-15 |
| S-06 | Administrator onboarding a user | IT administrator | When staff join or leave | FR-14, FR-15 |

## 4. Scenarios

### S-01 Weekly stock review

**Actor.** Head of hospital pharmacy (S1) or pharmacist (S2), role `pharmacist`.

**Trigger.** The start of the working week. Before the next ordering decision the pharmacist wants to know which items need attention in the coming weeks, instead of going through the stock sheet item by item.

**Preconditions.** Consumption and stock data have been imported up to the previous week (S-02). At least one forecast run has completed.

**Steps.**

1. The pharmacist logs in and opens the dashboard. PharmaStock shows the date of the latest import, the date and model of the latest forecast run, the number of items by risk level (High, Medium, Low) and the number of unread notifications.
2. The pharmacist opens the risk list (`FR-09`). PharmaStock lists items sorted by risk level and then by expected stock-out date, with current stock, lead time, planned receipts within the horizon and the forecast run that produced the assessment.
3. The pharmacist filters the list to High risk and opens an item page (`FR-05`, `FR-07`). The page shows the consumption history and stock level as a table and a chart, with stock-out weeks marked so that it is visible where zero consumption means "nothing to dispense" rather than "no demand" (`FR-17`); below the history, the point forecast with its interval for the next 12 weeks, the projected stock, the model used and its hold-out MAE and WAPE compared with the baselines (`FR-16`).
4. If the latest forecast run is older than the latest import, the pharmacist starts a new forecast run for all active items (`FR-06`). PharmaStock runs it in the background, shows the progress and refreshes the risk list when the run completes.
5. The pharmacist notes the items that need action and hands them over to the procurement specialist (S-04); for items where the forecast looks implausible (for example a single large issue to a department), the pharmacist records the item for the next review of data quality (S-02).

**Expected result.** Within a few minutes the pharmacist knows which items are projected to run out within their lead time, when, and on what evidence (history versus forecast). No manual spreadsheet is built, and the same list can be opened by the procurement specialist.

**Requirements.** `FR-05`, `FR-06`, `FR-07`, `FR-09`, `FR-16`, `FR-17`; `NFR-02` (page response time with up to 5,000 items).

**To verify in discussions.** How often stock decisions are actually taken and whether a weekly rhythm matches the ordering cycle (D-1, D-2); which columns of the risk list are needed first.

### S-02 Importing the monthly export

**Actor.** Pharmacist (S2), role `pharmacist`.

**Trigger.** At the beginning of the month the export of the previous month is available from the accounting system: a consumption file, a stock file and a receipts file in the formats described in the [data specification](../data/data-specification.md) (`consumption.csv`, `stock.csv`, `receipts.csv`; `period_start` is the Monday of the week).

**Preconditions.** The pharmacist has the files on the workstation. The medicine catalogue contains the items used so far.

**Steps.**

1. The pharmacist opens the Imports page, chooses the source type (consumption) and uploads the file (`FR-01`).
2. PharmaStock validates the file before saving anything (`FR-02`): required columns, date format, Monday-aligned periods, negative quantities, unknown item codes, duplicate periods for the same item. It shows a validation report: rows read, rows accepted, and every rejected row with its line number and reason.
3. If the report lists unknown item codes, the pharmacist chooses between adding them to the catalogue from the `item_name` and `unit` columns of the file (`FR-03`) and correcting the file and uploading it again. New items are created as active and can be edited later on the catalogue page.
4. If the report contains blocking errors (missing columns, negative quantities, duplicate periods), PharmaStock rejects the file as a whole and nothing is saved; the pharmacist corrects the export and repeats from step 1. Warnings (for example an unusually large weekly quantity) do not block the import.
5. When the report has no blocking errors, the pharmacist confirms. PharmaStock records the import batch (file name, source type, time, user, status, summary) and writes an audit entry (`FR-15`).
6. PharmaStock shows the data-quality summary of the batch (`FR-18`): coverage per item (weeks with data), gaps, outliers, and the weeks that will be treated as stock-out.
7. The pharmacist repeats steps 1–6 for the stock file and the receipts file. For the stock file, weeks with `quantity_on_hand` equal to zero are flagged as stock-out weeks; zero consumption in those weeks is treated as censored demand in forecasting rather than as "no demand" (`FR-17`).
8. The pharmacist starts a forecast run so that the risk list reflects the new month (S-01, step 4).

**Expected result.** The new month of data is in the database, every rejected row is explained before anything is saved, and stock-out weeks are flagged automatically. The pharmacist does not edit the files by hand to make them "fit".

**Requirements.** `FR-01`, `FR-02`, `FR-03`, `FR-15`, `FR-17`, `FR-18`; `NFR-06` (malformed input is rejected with a clear error).

**To verify in discussions.** Whether the accounting system exports per item and period or per transaction, and whether stock-out periods are recorded explicitly anywhere (D-2, D-4). If exports are per transaction, aggregation to weeks becomes part of the import.

### S-03 Reacting to a high-risk alert

**Actors.** Pharmacist (S2, role `pharmacist`) as primary actor; procurement and supply specialist (S3) and head of clinical department (S4, role `viewer`) as secondary actors.

**Trigger.** A forecast run has completed and found items whose projected stock falls to or below the safety stock within their lead time. PharmaStock has created an in-app notification for each high-risk item (`FR-12`).

**Preconditions.** The forecast run of S-01 (or S-02, step 8) has completed; current stock and planned receipts are up to date.

**Steps.**

1. On the next login the pharmacist sees the notification counter and opens the notification list. Each notification names the item, the risk level, the expected stock-out date and links to the item page.
2. The pharmacist opens the item page (`FR-07`) and checks that the alert is plausible: recent consumption, the forecast and its interval, current stock, planned receipts and the projected stock curve with the week in which it falls to or below the safety stock (`FR-08`).
3. The pharmacist decides what to do. Typical options are an own purchase outside the centralised schedule, a request to the distributor about the delivery date, or a substitution agreed with the clinical department. The decision itself is taken and executed outside PharmaStock (procurement execution is out of scope); the pharmacist marks the notification as read.
4. The pharmacist opens the risk list filtered to High (`FR-09`) and exports it to CSV or XLSX (`FR-13`) to attach to the request sent to procurement or management.
5. The procurement specialist receives the same notification, agrees a delivery date with the supplier and records the planned delivery in PharmaStock (S-04).
6. The head of the clinical department, who has the `viewer` role, opens the risk list and the item page to see when the item is expected to be short, and discusses substitution with the pharmacy. The viewer cannot import data, run forecasts, change thresholds or record deliveries (`FR-14`).

**Expected result.** The risk is known weeks before the stock-out, with an expected date and a quantity that can be put into a request. Pharmacy, procurement and the clinical department look at the same numbers instead of each keeping their own list.

**Requirements.** `FR-07`, `FR-08`, `FR-09`, `FR-12`, `FR-13`, `FR-14`.

**To verify in discussions.** Who should receive notifications and for which risk levels; whether in-app notifications are sufficient for the first version (e-mail notifications are not planned) (D-1, D-3, D-5).

### S-04 Planning a delivery

**Actor.** Procurement and supply specialist (S3), role `pharmacist` (see the open question in section 2).

**Trigger.** A delivery date and quantity have been confirmed, either by the single distributor for the centralised supply or by a supplier for an own purchase.

**Preconditions.** The item and the supplier exist in PharmaStock; the item has a recorded lead time (`FR-04`). A forecast run has completed.

**Steps.**

1. The specialist opens the item page (or the Planned deliveries page) and chooses "Add planned delivery". The form asks for the expected date, the quantity and the supplier; the item's primary supplier is preselected (`FR-10`).
2. PharmaStock validates the entry: the item is active, the quantity is positive, the supplier exists; a date in the past produces a warning. The planned receipt is saved with status `planned` and an audit entry is written (`FR-15`).
3. PharmaStock recalculates the projected stock of the item from the latest completed forecast run (`FR-08`): current stock plus planned receipts due by each week minus the cumulative forecast up to that week. The expected stock-out date and the risk level are updated on the item page and in the risk list (`FR-09`). No new forecast run is needed.
4. If the item is still at High risk because the delivery arrives after the projected stock-out, PharmaStock shows the gap: the first week in which the projected stock falls to or below the safety stock and the quantity missing until the delivery. The specialist uses this to ask for an earlier or partial delivery.
5. If the confirmed lead time of the supplier differs from the recorded one, the specialist updates the lead time on the supplier card (`FR-04`); this change is also written to the audit log.
6. When the delivery arrives, it appears in the next receipts import (S-02). The specialist marks the planned receipt as `received`; a delivery that will not come is marked `cancelled`, and the risk is recalculated.

**Expected result.** Confirmed deliveries are reflected in the risk assessment the moment they are recorded, and a remaining gap is visible as a date and a quantity rather than discovered when the shelf is empty.

**Requirements.** `FR-04`, `FR-08`, `FR-09`, `FR-10`, `FR-15`.

**To verify in discussions.** Whether delivery dates and quantities are known in advance for the centralised supply, how partial and late deliveries are handled, and whether the procurement specialist needs a role narrower than `pharmacist` (D-3).

### S-05 Configuring thresholds

**Actor.** Head of hospital pharmacy (S1), role `pharmacist`.

**Trigger.** Initial set-up after deployment, or a periodic review because the risk list produces too many or too few alerts.

**Preconditions.** The head of pharmacy is logged in. At least one forecast run has completed (to see the effect of a change).

**Steps.**

1. The head of pharmacy opens Settings, section Thresholds (`FR-11`). PharmaStock shows the current configuration: the safety-stock rule (a number of weeks of forecast consumption, or a fixed quantity per item as an override), the default lead time in days for items without a supplier record, the forecast horizon (12 weeks by default) and the risk level from which notifications are generated. The definition of the risk levels themselves (High: stock-out expected within the item's lead time; Medium: within the forecast horizon; Low: otherwise) is fixed and shown for reference.
2. The head of pharmacy changes the safety stock from one to two weeks of forecast consumption and sets the default lead time to the value agreed with procurement.
3. PharmaStock validates the values (positive numbers, horizon within the supported range), saves them in the threshold configuration and writes an audit entry with the old and the new values (`FR-15`).
4. PharmaStock recalculates the risk assessment of all items from the latest completed forecast run with the new parameters (`FR-08`) and shows the updated counts by risk level, so that the effect of the change is visible without a new forecast run.
5. For individual items with special handling (for example a cold-chain item that cannot be kept in large quantity), the head of pharmacy sets a per-item safety stock on the item page.

**Expected result.** The rules the pharmacy works by are recorded in the system rather than in the head of each person, every change is traceable to a user and a date, and the effect of a change is visible immediately.

**Requirements.** `FR-08`, `FR-11`, `FR-15`.

**To verify in discussions.** Whether a notion of safety stock or minimum stock is used today and how it is expressed (weeks of consumption, packs, a percentage) (D-1); whether per-group defaults are needed in addition to global and per-item values.

### S-06 Administrator onboarding a user

**Actor.** IT administrator of the organization (S5), role `administrator`.

**Trigger.** A new procurement specialist joins the organization and the head of pharmacy asks for access; later, a member of staff leaves.

**Preconditions.** PharmaStock is deployed and the administrator account exists.

**Steps.**

1. The administrator logs in and opens the Users page (`FR-14`). The page lists existing users with e-mail, full name, role and active flag.
2. The administrator creates the user with e-mail, full name and the role `pharmacist`, and sets a temporary password that is communicated to the user outside the system. PharmaStock stores only the password hash (`NFR-03`) and writes an audit entry (`FR-15`).
3. The new user logs in and changes the temporary password. From now on the user sees the functions of the `pharmacist` role: imports, forecasts, risk list, planned deliveries, thresholds and exports. A `viewer` would see the dashboard, item pages, forecasts and the risk list only; an `administrator` sees user management and the audit log.
4. When a member of staff leaves, the administrator deactivates the account instead of deleting it, so that audit entries and import batches keep referring to the user who created them.
5. Once a week the administrator reviews the audit log: imports, forecast runs and configuration changes with user and time, and filters by user or by action when a question comes up.

**Expected result.** Access is granted within minutes without shared accounts, each user sees only what the role allows, and every import, forecast run and configuration change can be traced to a person.

**Requirements.** `FR-14`, `FR-15`; `NFR-03`, `NFR-04`.

**To verify in discussions.** Who manages user accounts in the organization and whether an existing directory (for example a domain login) must be used instead of local passwords (D-4).

## 5. Coverage of the functional requirements

| Requirement | Priority | Scenarios |
|---|---|---|
| FR-01 Import consumption, stock and receipt data from CSV/XLSX files | Must | S-02 |
| FR-02 Validate imported data and report errors: missing columns, negative quantities, unknown items, duplicate periods | Must | S-02 |
| FR-03 Maintain the medicine catalogue: code, name, unit, group, active flag | Must | S-02 |
| FR-04 Maintain suppliers and lead times per item | Should | S-04 |
| FR-05 View current stock and consumption history per item as table and chart | Must | S-01 |
| FR-06 Run a forecast for all or selected items for a configurable horizon | Must | S-01, S-02 |
| FR-07 View the forecast per item together with history, point forecast, interval and model information | Must | S-01, S-03 |
| FR-08 Calculate shortage risk per item from forecast, current stock, planned receipts and lead time | Must | S-03, S-04, S-05 |
| FR-09 Show a prioritised list of items at risk with risk level and expected stock-out date | Must | S-01, S-03, S-04 |
| FR-10 Record planned deliveries (expected receipts) | Should | S-04 |
| FR-11 Configure risk thresholds and safety-stock parameters | Should | S-05 |
| FR-12 Generate in-app notifications for high-risk items | Should | S-03 |
| FR-13 Export forecast and risk reports to CSV/XLSX | Should | S-03 |
| FR-14 Authenticate users and manage roles: administrator, pharmacist, viewer | Must | S-03, S-06 |
| FR-15 Keep an audit log of imports, forecast runs and configuration changes | Should | S-02, S-04, S-05, S-06 |
| FR-16 Compare forecasting models against baselines on a hold-out period and show MAE and WAPE | Should | S-01 (model information on the item page); the comparison itself is run by the team, see the [verification and evaluation plan](../verification-and-evaluation-plan.md) |
| FR-17 Flag stock-out periods so that zero consumption during a stock-out is treated as censored demand | Must | S-01, S-02 |
| FR-18 Show a data-quality summary per import: coverage, gaps, outliers | Should | S-02 |

All Must requirements appear in at least one scenario.

## 6. Outside the scenarios

The following are deliberately not described, because they are out of scope of the project (see the proposal): placing or executing orders, e-prescriptions, real-time integration with national systems or with the accounting system, a mobile application, any patient-level data, and use by several organizations in one installation.

## 7. Next steps

- Derive the use cases and the use case diagram from these scenarios ([use-cases.md](./use-cases.md), `docs/diagrams/src/use-case-diagram.mmd`).
- Produce static mockups of the screens named in the scenarios (dashboard, imports, item page, risk list, planned deliveries, thresholds, users) in `prototype/`.
- After discussions D-1 to D-5, revise the scenarios and record the verified findings in the interview log.

Related tasks: this document is produced under task PHA2-13 of the [Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b).
