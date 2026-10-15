# PharmaStock — Project Proposal

Task: PHA2-5 | Last updated: 2026-10-15 | Status: complete for pre-defense-1 (open for revision during requirements analysis) | Maintainer: Birkhanym Kazhymukhamet

## 1. Project title

| Language | Title |
|---|---|
| English | Development of smart supply chain analytics system for forecasting pharmaceutical inventory and preventing medicine shortages in healthcare organizations |
| Kazakh | Медициналық ұйымдардағы фармацевтикалық қорларды болжау және дәрі-дәрмек тапшылығының алдын алуға арналған жеткізілімдер тізбегінің смарт-аналитикалық жүйесін әзірлеу |
| Russian | Разработка смарт-системы аналитики цепочек поставок для прогнозирования фармацевтических запасов и предотвращения дефицита медикаментов в медицинских организациях |

Short system name used in documents and code: **PharmaStock**.

Astana IT University, School of Software Engineering, educational program Software Engineering, group SE-2414, academic year 2026–2027 (September 2026 – June 2027). Team diploma project of three students. First pre-defense materials are due 24 October 2026.

## 2. Team and supervisor

| Team member | Area of responsibility |
|---|---|
| Birkhanym Kazhymukhamet (GitHub: @birxnm) | Requirements analysis and user scenarios, web interface (frontend), UX mockups, visualisation of forecasts and shortage alerts, user testing |
| Abzal Bakhytov | Backend (Python), database, REST API, data import and validation, integration of the forecasting module, shortage-risk calculation, access control and audit log, deployment and API documentation |
| Evelina Penkova (GitHub: @etoevelina) | Data preparation and analysis, forecasting models (baselines and ML), hyperparameter tuning, evaluation on a hold-out period, error analysis, reproducible experiments, serving forecasts through the API together with Abzal |

**Supervisor:** Kuralay Makhmetova, Senior Lecturer, School of Software Engineering, Astana IT University.

Working mode: weekly meetings with the supervisor; individual contribution is tracked by tasks in the [Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b), by commits in the GitHub repository and by demos at checkpoints. The detailed allocation of responsibilities is kept in [project-management/responsibilities.md](project-management/responsibilities.md).

## 3. Problem statement

### 3.1 Context: medicine supply in healthcare organizations in Kazakhstan

Hospitals and polyclinics in Kazakhstan obtain medicines through two channels:

- **Centralised procurement.** Medicines for the guaranteed volume of free medical care (and compulsory social health insurance) are procured centrally through the single distributor SK-Pharmacy. Organizations submit their needs in advance, and deliveries arrive in batches according to the distributor's schedule rather than on demand.
- **The organization's own purchases.** The remaining items are bought by the organization itself through its own tenders and contracts, which also take weeks from request to receipt.

As a result, the lead time between recognising a need and receiving the medicine is long and largely outside the pharmacy's control. Under these conditions, the only lever the pharmacy has is to notice an upcoming shortage early enough to act.

Pharmacy stock in these organizations is managed mostly with accounting systems and spreadsheets. These tools record what was received and dispensed, but they do not forecast future consumption and do not relate stock, expected deliveries and lead time to each other.

### 3.2 The problem

- **Intermittent consumption.** At the level of a single item, consumption consists of long runs of zero demand with occasional spikes (for example, when a patient with a specific condition is admitted). Simple averages and intuition handle such series poorly.
- **Shortages are discovered late.** A shortage becomes visible when the item is already out of stock or close to it; by then the lead time makes a timely replenishment impossible, and clinical departments have to substitute or postpone treatment.
- **Overstock and expiry.** To avoid shortages, staff over-order some items; those items expire on the shelf, which wastes budget and storage.
- **Censored demand.** When an item is out of stock, the recorded consumption is zero even though demand existed. If such zeros are treated as real demand, any forecast underestimates future need. This effect must be flagged explicitly and not learned as "zero".
- **No early-warning tool.** Pharmacy staff lack a tool that forecasts consumption per item and turns forecasts, current stock, expected deliveries and lead time into an early shortage-risk signal with a prioritised list of items that need attention.

**Problem statement.** Healthcare organizations in Kazakhstan manage pharmacy stock with tools that record the past but do not anticipate the future; because procurement lead times are long and item-level consumption is intermittent, shortages are detected too late to prevent, while other items are overstocked and expire.

### 3.3 Evidence base

The problem description above is based on the team's analysis of the domain and will be verified with representatives of the target users. Interviews with pharmacy and procurement staff are planned; the stakeholder list, interview guide and interview log are kept in [evidence-of-relevance/](evidence-of-relevance/). The review of publications and of existing systems is kept in [literature-review.md](literature-review.md) and [existing-systems-comparison.md](existing-systems-comparison.md). Statements that have been confirmed by interviews will be distinguished from assumptions in the requirements document.

## 4. Target users

The system is intended for the staff of a single healthcare organization. No patients are users of the system, and no patient data is processed.

| User | What they need from the system | Role in the system |
|---|---|---|
| Head of hospital pharmacy / pharmacist (primary user) | Import consumption and stock data, run forecasts, see which items are at risk of shortage and when, configure thresholds, export reports | Pharmacist |
| Procurement and supply specialist | See the prioritised risk list and expected stock-out dates, record planned deliveries, export reports for procurement requests | Pharmacist |
| Heads of clinical departments | View forecasts and risk status for the medicines their department uses | Viewer (read only) |
| System administrator | Manage users and roles, review the audit log, maintain the deployment | Administrator |

## 5. Aim

Develop a prototype of a smart supply chain analytics system that forecasts pharmaceutical consumption and warns about shortage risk in healthcare organizations.

## 6. Objectives

| # | Objective | Main result | Lead |
|---|---|---|---|
| 1 | Analyse the domain, existing systems and literature | Literature review, comparison of existing systems, evidence of relevance | Birkhanym (with the team) |
| 2 | Define requirements and architecture | Requirements specification, architecture description and diagrams, database schema, API contract | Birkhanym, Abzal |
| 3 | Prepare data and build forecasting models compared with baselines | Data specification, synthetic dataset, baselines, ML models, experiment reports | Evelina |
| 4 | Implement backend, database, API and risk calculation | FastAPI service, PostgreSQL schema, REST API, shortage-risk logic, access control, audit log | Abzal |
| 5 | Implement the web interface | Vue 3 application: dashboards, item pages, risk list, notifications, configuration | Birkhanym |
| 6 | Evaluate the system on a hold-out period and with users | Model comparison (MAE, WAPE), alert precision/recall, user testing results | Evelina, Birkhanym |
| 7 | Document results and prepare a scientific article | Technical documentation, thesis text, article manuscript | Whole team |

## 7. Expected outcomes

1. A working prototype: backend (Python, FastAPI) with a PostgreSQL database, a forecasting module and a web user interface, deployable with Docker Compose.
2. A comparison of forecasting models against baselines (naive, seasonal-naive, moving-average, Croston/SBA) on a hold-out period using MAE and WAPE.
3. An error analysis per medicine group and a description of the limitations of the models and of the system.
4. Technical documentation: requirements, architecture, database schema, API contract, data specification, setup and testing instructions.
5. The thesis text and a scientific article based on the project results.

## 8. Project scope

### 8.1 In scope and out of scope

| Area | In scope | Out of scope (future work) |
|---|---|---|
| Data input | Import of consumption, stock and receipt data from CSV/XLSX exports of the organization's accounting system; validation and a data-quality summary per import | Real-time integration with national systems and with 1C; automatic extraction from accounting databases |
| Master data | Medicine catalogue (code, name, unit, group, active flag); suppliers and lead times per item | Procurement contracts, prices, budgets |
| Forecasting | Weekly consumption forecast per item for a configurable horizon (initial decision: weekly step, 12-week horizon); baselines and ML models; comparison on hold-out data with MAE and WAPE | Daily forecasts; forecasting of demand for new items without history |
| Shortage risk | Risk calculation from forecast, current stock, planned receipts and lead time; prioritised risk list with risk level and expected stock-out date; in-app notifications for high-risk items | Automatic order generation and ordering/procurement execution; e-prescriptions |
| Planning inputs | Recording of planned deliveries (expected receipts); configuration of risk thresholds and safety-stock parameters | Supplier portals, electronic exchange of orders |
| User interface | Web interface: dashboards, item pages with history and forecast, risk list, notifications, configuration, import pages; English first (NFR-10); Russian localisation is a Could-priority requirement, implemented only if time allows | Mobile application |
| Users and security | Authentication, roles (administrator, pharmacist, viewer), audit log of imports, forecast runs and configuration changes | Multi-organization SaaS; integration with external identity providers |
| Reporting | Export of forecast and risk reports to CSV/XLSX | Printed forms required by regulators |
| Data | Aggregated consumption, stock and receipt data per item and week; a documented synthetic dataset for development | Patient data of any kind (not stored, not processed) |

The functional and non-functional requirements that implement this scope, with priorities and acceptance criteria, are listed in [requirements.md](requirements.md).

### 8.2 Assumptions and constraints

| ID | Type | Statement | Consequence for the project |
|---|---|---|---|
| A-01 | Assumption | Consumption, stock and receipt history per item can be exported from the organization's accounting system as CSV/XLSX | Import by files is sufficient for the prototype; no live integration is built |
| A-02 | Assumption | Historical data covers at least two to three years so that yearly seasonality can be assessed | Shorter history reduces the usefulness of seasonal baselines; the evaluation plan allows for this |
| A-03 | Assumption | Lead time per item (or per supplier) can be estimated from past receipts or provided by procurement staff | Lead time is a configurable input, not a predicted value |
| C-01 | Constraint | Access to real data from a partner healthcare organization is being requested and is not guaranteed | A documented synthetic dataset is used for development and the first experiments until real data are available; results on synthetic data are reported as such |
| C-02 | Constraint | No patient personal data is stored or processed (NFR-04) | The import formats contain only aggregated per-item, per-week quantities (see data/data-specification.md) |
| C-03 | Constraint | Initial time step is weekly and the initial forecast horizon is 12 weeks | Both are configuration parameters and may be revised during requirements analysis; the data model stores periods by their start date so that the step can change |
| C-04 | Constraint | Team of three students, September 2026 – June 2027, with pre-defense deadlines set by the School | Scope is limited to a prototype for a single organization; features marked "Could" in the requirements are implemented only if time allows |
| C-05 | Constraint | The prototype must be deployable on a modest server (4 vCPU / 8 GB) with Docker Compose on Linux (NFR-01, NFR-07) | Models and the forecast run are designed for batch execution within the stated time limits |

### 8.3 Scope realism

The scope is limited to what three students can design, implement and evaluate within the academic year: one organization, file-based import, batch forecasting and a web interface. Items listed as out of scope are either operational functions that require integration with external systems (ordering, national systems, 1C) or product features that do not contribute to answering the research question (mobile application, multi-organization SaaS). The milestone plan in [project-management/plan-and-milestones.md](project-management/plan-and-milestones.md) allocates the work per month, and the risk register in [project-management/risks.md](project-management/risks.md) records the fallback for each major risk.

## 9. Engineering complexity

| Challenge | Why it is hard | How the project addresses it |
|---|---|---|
| Integration of four components | Data import and validation, the forecasting module, the shortage-risk logic and the web interface must share one data model and one API, and be developed in parallel by three people | A common data model (medicine_item, consumption_record, stock_snapshot, receipt, planned_receipt, forecast_run, forecast, risk_assessment, ...) and an API contract are fixed early; the forecasting module is an in-process Python package with a single interface, `forecast_items(history, horizon, config)`, called by the backend; CI runs tests on every pull request |
| Intermittent demand | Most item-level series contain long runs of zeros and occasional spikes; classical smoothing and generic regression underestimate the spikes or produce constant forecasts; standard percentage errors are undefined on zero actuals | Baselines designed for intermittent demand (Croston, SBA) are included alongside naive, seasonal-naive and moving-average; ML models (LightGBM with lag and calendar features) are compared against them; evaluation uses MAE and WAPE, with WAPE computed only where total actual consumption in the window is greater than zero |
| Censored demand | Zero consumption during a stock-out is not zero demand; learning from such periods biases every model downwards and hides exactly the shortages the system should prevent | Stock-out periods are flagged from stock snapshots (FR-17); flagged periods are excluded from training or treated as missing, and forecast quality is reported separately for items affected by stock-outs |
| Turning forecasts into decisions | A forecast alone does not tell the pharmacist what to do; the risk signal depends on the forecast, the current stock, planned receipts, lead time and safety stock, and must be explainable | Projected stock per week is computed as current stock plus receipts due minus cumulative forecast; the expected stock-out date is the first week where projected stock falls to or below safety stock; the risk level (High / Medium / Low) is derived from the stock-out date relative to the lead time and the horizon, and the projected-stock curve is shown to the user |
| Data quality | Exports from accounting systems contain missing columns, negative quantities, duplicate periods and unknown items; silent acceptance would produce wrong forecasts | Validation rules with clear error reporting (FR-02, NFR-06) and a data-quality summary per import (FR-18) |
| Reproducible evaluation | Model comparison must be fair and repeatable: the same time-based split, the same seeds and saved configurations for every run | Rolling-origin evaluation with a train/validation/test split by date, fixed seeds, versioned experiment configurations and saved results (NFR-05) |
| Performance and access control | A forecast run for 1,000 items with 3 years of weekly history must complete within 5 minutes (NFR-01); role-based access, hashed passwords and an audit log are required (NFR-03, FR-14, FR-15) | Batch forecast runs executed as background jobs with status tracking; roles enforced in the API layer; audit records written for imports, forecast runs and configuration changes |

## 10. Success criteria

| ID | Criterion | Measure | Measurement conditions |
|---|---|---|---|
| S-01 | Forecast accuracy exceeds the baselines | MAE and WAPE on the hold-out test period, per item and aggregated per medicine group | The selected model is compared with naive, seasonal-naive (season 52), moving-average and Croston/SBA baselines on the same time-based split; WAPE is reported only when total actual consumption in the window is greater than zero; the comparison table is produced by a reproducible experiment |
| S-02 | Shortage alerts are useful | Precision and recall of High/Medium alerts against actual stock-outs on the test period | Alerts are generated from forecasts made before the test period using the recorded stock and receipts; recall for High-risk items is prioritised, because a missed shortage costs more than a false alert |
| S-03 | The prototype works end to end | A complete scenario runs without manual intervention: import of files, forecast run, risk list, item page, notification, report export | Demonstrated on the synthetic dataset and, if available, on real data in the integration demo (January 2027) and at the final pre-defense |
| S-04 | Performance and deployment targets are met | Forecast run time (NFR-01), page response time (NFR-02), deployment with Docker Compose (NFR-07) | Measured on a 4 vCPU / 8 GB server with 1,000 items and 3 years of weekly history |
| S-05 | Experiments are reproducible | Re-running a saved experiment configuration reproduces the reported metrics | Fixed seeds, versioned configurations and saved results (NFR-05) |
| S-06 | Target users can complete their scenarios | User testing of the key scenarios with representatives of pharmacy and procurement staff; findings documented | Planned for the spring semester, after the main screens are available |

Numeric targets for S-01 and S-02 are not fixed in advance: they will be set after the first baseline run on the synthetic dataset and revised when real data become available, so that the evaluation is not tuned to a desired result. The initial working expectation is that the selected model has a lower WAPE than the best baseline for the majority of medicine groups and is not worse than the best baseline in aggregate. The full testing plan, metrics and measurement conditions are described in [verification-and-evaluation-plan.md](verification-and-evaluation-plan.md).

## 11. Deliverables per pre-defense

| Stage | Date | Deliverables | Git tag |
|---|---|---|---|
| Pre-defense 1 | 24 October 2026 | Repository with README; this proposal; evidence of relevance (stakeholders, interview guide, interview log); literature review; existing systems comparison; technology comparison; initial requirements with acceptance criteria; architecture description and diagrams (system context, use case, component draft) with editable sources; database schema and API contract (draft); UX mockups of key screens; verification and evaluation plan; project management materials (plan and milestones, risks, responsibilities, task register); supervisor feedback log; data specification and experiment plan | `pre-defense-1` |
| Pre-defense 2 | To be confirmed by the School (planned after the January 2027 integration demo) | Prepared data and synthetic dataset; baseline and first ML models with a comparison on hold-out data; backend with database, REST API and risk calculation; main screens of the web interface; end-to-end integration demo; literature review draft for the thesis; updated requirements and architecture | `pre-defense-2` |
| Final pre-defense | To be confirmed by the School (May–June 2027) | Final experiments, model comparison and error analysis per medicine group; notifications and threshold configuration; component and integration tests; deployed prototype; technical documentation; thesis draft; article manuscript; presentation | `final-pre-defense` |

For each submission the team provides the repository link, the tag, a summary of completed work, known limitations and outstanding tasks. Tags are never moved or replaced.

## 12. How the proposal was validated

- The team composition, allocation of roles, work plan and evaluation methodology were approved by the supervisor in a justification letter dated 9 October 2026. The proposal text was prepared on that basis and is reviewed with the supervisor at the weekly meetings; comments and the team's decisions are recorded in [supervision/feedback-log.md](supervision/feedback-log.md).
- Interviews with potential users (pharmacy and procurement staff of healthcare organizations) are planned and have not yet been conducted. The stakeholder list, the interview guide and the log of conducted interviews are kept in [evidence-of-relevance/](evidence-of-relevance/). The problem statement and the scope will be revised if the interviews contradict the current assumptions, and the requirements document will mark each statement as verified by interviews or as an assumption.
- Access to real data is being requested from a partner healthcare organization; until it is confirmed, the data-related assumptions above remain assumptions and are tracked as a project risk.

## 13. Related documents

| Document | Path |
|---|---|
| Documentation index | [README.md](README.md) |
| Evidence of relevance | [evidence-of-relevance/](evidence-of-relevance/) |
| Literature review | [literature-review.md](literature-review.md) |
| Existing systems comparison | [existing-systems-comparison.md](existing-systems-comparison.md) |
| Technology comparison | [technology-comparison.md](technology-comparison.md) |
| Requirements | [requirements.md](requirements.md) |
| Architecture | [architecture/architecture.md](architecture/architecture.md) |
| Data specification | [data/data-specification.md](data/data-specification.md) |
| Verification and evaluation plan | [verification-and-evaluation-plan.md](verification-and-evaluation-plan.md) |
| Plan and milestones | [project-management/plan-and-milestones.md](project-management/plan-and-milestones.md) |
| Risks | [project-management/risks.md](project-management/risks.md) |
| Responsibilities | [project-management/responsibilities.md](project-management/responsibilities.md) |
| Supervisor feedback log | [supervision/feedback-log.md](supervision/feedback-log.md) |
