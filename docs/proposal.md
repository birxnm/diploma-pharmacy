# PharmaStock — Project Proposal

Task: PHA2-5 | Last updated: 2026-10-14 | Status: draft (sections 8 and 9 to be completed) | Maintainer: Birkhanym Kazhymukhamet

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

## 8. Project scope (draft)

> Status: draft. The scope table, assumptions and constraints will be completed in the next revision of this document.

Preliminary boundaries, to be confirmed with the supervisor:

- **In scope (preliminary):** import of consumption, stock and receipt data from CSV/XLSX exports; medicine catalogue; weekly consumption forecast per item; shortage-risk calculation and a prioritised risk list; dashboards and item pages; users and roles; comparison of models on hold-out data.
- **Out of scope (preliminary):** execution of orders and procurement, e-prescriptions, real-time integration with national systems and 1C, mobile application, patient data, multi-organization SaaS.

## 9. Engineering complexity (draft)

> Status: draft. To be completed in the next revision of this document.

Preliminary list of the sources of complexity: integration of data import, forecasting, risk logic and the user interface into one system; forecasting of intermittent demand; handling of censored demand during stock-outs; reproducible experiments and evaluation on a hold-out period.

## 10. Related documents

| Document | Path |
|---|---|
| Documentation index | [README.md](README.md) |
| Evidence of relevance | [evidence-of-relevance/](evidence-of-relevance/) |
| Literature review | [literature-review.md](literature-review.md) |
| Existing systems comparison | [existing-systems-comparison.md](existing-systems-comparison.md) |
| Technology comparison | [technology-comparison.md](technology-comparison.md) |
| Requirements | [requirements.md](requirements.md) |
| Architecture | [architecture/architecture.md](architecture/architecture.md) |
| Verification and evaluation plan | [verification-and-evaluation-plan.md](verification-and-evaluation-plan.md) |
| Plan and milestones | [project-management/plan-and-milestones.md](project-management/plan-and-milestones.md) |
| Risks | [project-management/risks.md](project-management/risks.md) |
