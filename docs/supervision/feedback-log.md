# PharmaStock — Supervisor Feedback Log

_PHA2-21 · Last updated: 2026-10-20 · Status: v0.1 · Author: Birkhanym Kazhymukhamet · Reviewer: Evelina Penkova_

This log records the feedback of the supervisor, Kuralay Makhmetova (Senior Lecturer, School of Software Engineering, Astana IT University), and the decisions the team took in response. Its purpose is traceability: a team member, a reviewer or a pre-defense committee member can see which supervisor point led to which change in the repository, and which points are still open. It complements [plan-and-milestones.md](../project-management/plan-and-milestones.md) section 5 (supervision cadence and review checkpoints), [task-register.md](../project-management/task-register.md) (status of the follow-up tasks) and [risks.md](../project-management/risks.md) (risks reviewed at the meetings).

## 1. Purpose and format

### 1.1 What is recorded

| Recorded | Not recorded |
|---|---|
| Written approvals and comments from the supervisor (letters, review comments on documents or pull requests) | Comments the supervisor has not made: nothing is anticipated or paraphrased beyond what was said or written |
| Weekly supervisor meetings: what was shown, the feedback, the decisions and the follow-up tasks | Meetings that have not taken place; a coming meeting appears only in section 4 as an agenda |
| Review checkpoints listed in `plan-and-milestones.md` section 5 (requirements and architecture, experiment plan, real data decision, first model comparison, integration demo, final experiments, thesis draft) | Internal team synchronisations; they are tracked through tasks and pull requests |
| Changes to deadlines, scope or responsibilities agreed with the supervisor (`plan-and-milestones.md` section 7, `task-register.md` section 4) | Names of interview participants or partner organizations; the consent rules of [interview-guide.md](../evidence-of-relevance/interview-guide.md) apply here too |

### 1.2 Rules

1. Birkhanym Kazhymukhamet writes the entry in the week of the meeting or of the written feedback and opens a pull request under a DIP task; another team member reviews it before merge.
2. Every supervisor point is numbered inside its entry (P1, P2, ...) and mapped in the "Decisions and actions taken" table to the document section or task where the team's response lives. A point without a mapping is marked **Open** and carried to section 4 until it has one.
3. Follow-up work is a task in the [Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b), mirrored in `task-register.md`; this log refers to it by its `PHA2-<n>` ID and does not repeat the task description.
4. Requirement IDs (`FR-01` ... `FR-18`, `NFR-01` ... `NFR-10`, `FQ-01` ... `FQ-15`), entity names, API paths, model and metric names are used verbatim, as in all other documents.
5. The supervisor's words are summarised, not quoted; letters and comments are not stored in the repository.
6. An entry is not rewritten after the next meeting; only the status columns are updated, with the date of the check. A correction is added as a dated line in the change log (section 5).

### 1.3 Entry fields

| Field | Content |
|---|---|
| ID | `FB-<n>`, sequential across the project |
| Date | ISO date of the meeting or of the written feedback |
| Format | Meeting; written feedback; or review comments on a document or pull request |
| Participants | Supervisor and the team members present (or addressed, for written feedback) |
| Topic | One line |
| Shown | Code, data or results demonstrated at the meeting (the supervisor expects code, data and results every week, see FB-01 P6); "—" for written feedback |
| Feedback | Numbered supervisor points P1, P2, ... |
| Decisions and actions taken | Table: point → decision or action → where it is recorded → task → status |
| Follow-up tasks | `PHA2-<n>` with the responsible member and the due date |
| Status | **Open** (at least one point without an action), **In progress** (actions exist, at least one not finished), **Done** (every action closed); the date of the last check is given |

Status values of a single action: **Done**, **In progress**, **Planned** (task created, not started), **Open** (no task yet).

## 2. Entries

### 2.1 Index

| ID | Date | Format | Topic | Follow-up tasks | Status (checked 2026-10-20) |
|---|---|---|---|---|---|
| FB-01 | 2026-10-09 | Written feedback (justification letter) | Approval of the team composition, roles, work plan and evaluation methodology; conditions for experiments and supervision | PHA2-20, PHA2-21, PHA2-26 | In progress (P5 waits for the data access decision; P4 closed at design level, module-side censoring planned) |

No weekly meeting entries are recorded in this version of the log. Entries are added in the week of each meeting using the template of section 3.

### 2.2 FB-01 — 2026-10-09 — Justification letter

| Field | Content |
|---|---|
| Date | 2026-10-09 |
| Format | Written feedback: justification letter approving the project set-up. No meeting minutes belong to this entry |
| Participants | Kuralay Makhmetova (supervisor); addressed to the team: Birkhanym Kazhymukhamet, Abzal Bakhytov, Evelina Penkova |
| Topic | Approval of the team composition, roles, work plan (September 2026 – June 2027) and evaluation methodology; conditions for running experiments and for supervision |
| Shown | — |
| Status | In progress (checked 2026-10-20): P1, P2, P3 and P6 are closed in the repository; P4 is closed at design level (P4a–P4c implemented in the forecasting module; P4d per-class results and P4e module-side censoring planned, see the table below); P5 waits for the data access decision (PHA2-26, due 2026-10-31) |

**Feedback (points of the letter).** The letter is summarised here; it is not reproduced in the repository.

- **P1 Team composition approved.** A team of three students: Birkhanym Kazhymukhamet, Abzal Bakhytov, Evelina Penkova.
- **P2 Roles approved.** Birkhanym: requirements analysis and user scenarios, web interface (frontend), UX mockups, visualisation of forecasts and shortage alerts, user testing. Abzal: backend (Python), database, REST API, data import and validation, integration of the forecasting module, shortage-risk calculation, access control and audit log, deployment and API documentation. Evelina: data preparation and analysis, forecasting models (baselines and ML), hyperparameter tuning, evaluation on a hold-out period, error analysis, reproducible experiments, serving forecasts through the API together with Abzal.
- **P3 Work plan approved.** The monthly plan for September 2026 – June 2027: October — requirements, roles, literature and system review, architecture, database schema, UI mockups, data availability check, repository, experiment plan, pre-defense-1 materials; November–December — data preparation, baselines, first models, API and main screens, literature review draft; January — integration demo end to end; February — tuning, notifications, replenishment calculations, component tests; March — final experiments, comparison, error analysis, integration testing; April — thesis draft, technical documentation, article manuscript, deployed prototype; May–June — revisions, presentation, pre-defense and defense.
- **P4 Evaluation methodology approved.** (a) Forecasting models are compared against baselines; (b) accuracy is measured with MAE and WAPE; (c) the split between training and evaluation data is time-based; (d) rarely consumed items are analysed separately; (e) zero consumption is distinguished from a stock-out.
- **P5 Data access.** Access to data must be confirmed before the experiments are run.
- **P6 Supervision.** Weekly meetings at which the team shows code, data and results.

**Decisions and actions taken.** Statuses as of 2026-10-20, checked against `task-register.md`.

| Point | Subject | Decision or action of the team | Where it is recorded | Task | Status |
|---|---|---|---|---|---|
| P1 | Team composition | The three members are recorded with their roles and, where available, GitHub accounts; the supervisor is named in the same documents | `README.md` (team); `docs/proposal.md` section 2; `docs/project-management/responsibilities.md` section 1 | PHA2-1, PHA2-5, PHA2-20 | Done |
| P2 | Roles | The approved roles are turned into a RACI table per work area, repository ownership with default reviewers and an initial allocation of thesis chapters; the same split is stated in the contribution guide so that reviewers are chosen by area | `responsibilities.md` sections 3–5; `CONTRIBUTING.md` section 1; `docs/proposal.md` section 2 | PHA2-4, PHA2-20 | Done |
| P3 | Work plan | The monthly plan is converted into a timeline with milestones M1–M9, exit criteria and the Git tags `pre-defense-1`, `pre-defense-2`, `final-pre-defense`; the October work is registered as tasks PHA2-2 to PHA2-24 with deadlines; the monthly structure of the letter is kept unchanged | `plan-and-milestones.md` sections 1–4 and 7; `task-register.md` | PHA2-20 | Done; milestone M1 (pre-defense-1 package) due 2026-10-24 |
| P4a | Comparison against baselines | Five baselines fixed and implemented: `naive`, `seasonal_naive` (season 52), `moving_average(window)`, `croston`, `sba`; every candidate model is compared against all five on the same evaluation windows; success criterion S-01 | `docs/requirements.md` FR-16 and FQ-05; `docs/verification-and-evaluation-plan.md` section 4.5.1; `docs/proposal.md` section 10; `forecasting/forecasting/models/baselines.py` | PHA2-11, PHA2-16, PHA2-19 | Done |
| P4b | MAE and WAPE | `mae`, `wape` (returns None when the sum of actuals in the window is 0) and `bias` defined and implemented; overall and per-group WAPE are pooled over weeks and items, not averaged per item; metrics reported per item, per medicine group and overall | `docs/requirements.md` FQ-08; `docs/verification-and-evaluation-plan.md` section 4.5.3; `forecasting/forecasting/evaluation/metrics.py` | PHA2-11, PHA2-16, PHA2-19 | Done |
| P4c | Time-based split | Rolling-origin evaluation with at least three origins, a 12-week test window after each origin and a 12-week validation window before it; no shuffling; all features and fits use only data before the origin; the last origin's test window is the hold-out reported in the thesis | `docs/requirements.md` FQ-09; `docs/verification-and-evaluation-plan.md` section 4.4; `forecasting/forecasting/evaluation/split.py` | PHA2-11, PHA2-16, PHA2-19 | Done |
| P4d | Separate analysis of rarely consumed items | Items are classified on the training window by demand pattern (smooth, intermittent, erratic, lumpy); metrics are reported separately for the intermittent and lumpy classes ("rarely consumed") and per medicine group; acceptance target E-02 (rarely consumed items not worse than `sba`); the synthetic dataset contains all four classes so the reporting can be exercised now | `docs/verification-and-evaluation-plan.md` sections 4.5.3 and 4.8; `docs/data/data-specification.md` section 10 | PHA2-15, PHA2-19 | Done (design); first per-class results planned in PHA2-27 (due 2026-11-27) |
| P4e | Zero consumption vs stock-out | Design decided and recorded in the requirements: a week is a stock-out when the `stock_snapshot` of that week has `quantity_on_hand = 0` (`is_stock_out`); such weeks are censored demand and are not learned as zero. Implemented in the forecasting module so far: `is_stock_out` is accepted as an optional column of the consumption frame, the module validates its values (only True/False, otherwise the error `invalid_boolean`) and reports the number of censored weeks per item (`n_censored_weeks`). Planned on the module side (FQ-10, FQ-12): exclusion of censored weeks from fitting and from the evaluation set by default, imputation evaluated as an experiment, rejection of input without the `is_stock_out` column, and the chosen handling saved as a configuration value with every run; tracked as risk R-07 | `docs/requirements.md` FR-17 (section 6.14), FQ-02, FQ-10, FQ-12; `docs/data/data-specification.md` section 7; `docs/verification-and-evaluation-plan.md` sections 4.3 and 4.5.4; `forecasting/forecasting/data/schema.py` and `forecasting/forecasting/data/validation.py` (optional `is_stock_out` column, boolean check); `forecasting/forecasting/api.py` (`n_censored_weeks`); `risks.md` R-07 | PHA2-11, PHA2-15, PHA2-16, PHA2-19 | Done (design); module-side censoring and rejection of input without `is_stock_out` (FQ-10, FQ-12) planned, to be implemented before PHA2-27; censoring experiment (requirements open question Q8) planned with PHA2-27 |
| P5 | Data access confirmed before experiments | Access to anonymised, aggregated per-item weekly consumption, stock and receipt history has been requested from a partner healthcare organization through the supervisor and the team's contacts; the request is pending with a decision date of 2026-10-31; until access is confirmed, development and the first experiments run on the documented synthetic dataset and every result is labelled "synthetic"; experiments on real data start only after the conditions of use are recorded, and real data are kept outside Git | `docs/data/data-specification.md` section 11; `risks.md` R-01 and dependency D-01; `docs/evidence-of-relevance/interview-log.md` section 4.1; `docs/verification-and-evaluation-plan.md` section 4.2 | PHA2-15 (Done), PHA2-26 (Planned, due 2026-10-31) | In progress |
| P6 | Weekly meetings with code, data and results | One supervisor meeting per week with a standing agenda: task board by status, demo of finished work, open questions, risks, tasks for the next week; every member updates the task register before the meeting; this log records the feedback in the same week; individual contribution is tracked by tasks, commits and demos | `plan-and-milestones.md` section 5; `task-register.md` section 4; `responsibilities.md` section 7; this document | PHA2-20, PHA2-21 | Done (cadence agreed); meeting entries are added as meetings take place |

**Follow-up tasks.**

| Task | Action | Responsible | Due | Status (2026-10-20) |
|---|---|---|---|---|
| PHA2-20 | Plan, milestones, responsibilities, risk register and task register derived from the approved plan and roles | Evelina with Birkhanym | 2026-10-20 | Done |
| PHA2-21 | This log, with the mapping of the letter to documents and tasks | Birkhanym | 2026-10-20 | Done |
| PHA2-26 | Real data access agreement: outcome (granted, refused or pending) and conditions of use recorded in this log, `risks.md` and `data-specification.md` | Evelina with the supervisor | 2026-10-31 | Planned |

## 3. Template for weekly entries

Copy the block below under section 2.2 as `### 2.<n> FB-<n> — <date> — <topic>`, add a row to the index in section 2.1 and move the items it resolves out of section 4. Fields that do not apply get "—"; nothing is left to be filled in later without being marked "to be completed".

```markdown
### 2.<n> FB-<n> — YYYY-MM-DD — <topic>

| Field | Content |
|---|---|
| Date | YYYY-MM-DD |
| Format | Meeting / written feedback / review comments |
| Participants | <supervisor>; <team members present> |
| Topic | <one line> |
| Shown | <code, data or results demonstrated, with the task IDs and who presented> |
| Status | Open / In progress / Done (checked YYYY-MM-DD) |

**Feedback.**

- **P1** <supervisor point, summarised>
- **P2** <supervisor point, summarised>

**Decisions and actions taken.**

| Point | Subject | Decision or action of the team | Where it is recorded | Task | Status |
|---|---|---|---|---|---|
| P1 | <subject> | <decision> | `<document>` section <n> | PHA2-<n> | Planned / In progress / Done / Open |
| P2 | <subject> | <decision> | `<document>` section <n> | PHA2-<n> | Planned / In progress / Done / Open |

**Follow-up tasks.**

| Task | Action | Responsible | Due | Status (YYYY-MM-DD) |
|---|---|---|---|---|
| PHA2-<n> | <action> | <member> | YYYY-MM-DD | Planned |
```

Compact form for the index row (section 2.1): `| FB-<n> | YYYY-MM-DD | <format> | <topic> | PHA2-<n>, PHA2-<m> | <status> (checked YYYY-MM-DD) |`.

Checklist before the entry is merged:

1. Every supervisor point has a row in the decisions table, or is marked Open and listed in section 4.
2. Every follow-up task exists in Linear and in `task-register.md` with the same ID, responsible member and due date.
3. Changed deadlines, scope or responsibilities are also applied to `plan-and-milestones.md`, `task-register.md` and, where a risk changes, `risks.md`.
4. No personal data of interview participants and no names of partner organizations.

## 4. Pending items for the next meeting

Items the team intends to raise at the next weekly meeting, as of 2026-10-20. They are agenda points, not decisions; the outcome will be recorded as an FB entry.

| # | Item | Why it is on the agenda | Prepared by | Related documents and tasks | Decision needed from the meeting |
|---|---|---|---|---|---|
| 1 | Data access confirmation | FB-01 P5: experiments on real data wait for confirmed access; the request to a partner healthcare organization is pending; the decision date is 2026-10-31, which is also the trigger of risk R-01 | Evelina | PHA2-26; `data-specification.md` section 11; `risks.md` R-01, D-01 | Whether an answer can be expected by 2026-10-31; which conditions of use the team can accept (aggregated per item and week, no personal data, data kept outside Git, item names replaceable by codes); if access is not granted in time, confirmation of the synthetic-only path for the first model comparison (milestone M3, 2026-11-27) |
| 2 | Interview schedule | Discussions D-1 to D-5 of the interview log are not scheduled; D-1 and D-2 are to be scheduled by 2026-10-24; PHA2-25 is due 2026-11-07; the trigger of risk R-09 is "no interview scheduled by 2026-10-31" | Birkhanym | PHA2-25; `interview-log.md` sections 1–2; `interview-guide.md`; `risks.md` R-09 | Introductions to pharmacy and procurement staff through the supervisor's contacts; whether remote interviews are acceptable; which assumptions (A-01 to A-16) the supervisor considers the most important to verify first |
| 3 | Forecast horizon confirmation | The weekly step and the 12-week default horizon are initial decisions open for revision (FQ-01, FQ-03; assumptions A-06, A-07; requirements open question Q4); the evaluation windows (12-week test window) and the Medium risk level depend on the horizon | Evelina | `requirements.md` FQ-03 and section 8 (Q4); `interview-log.md` A-06, A-07; `verification-and-evaluation-plan.md` section 4.4; `requirements.md` FR-08 | Confirm 12 weeks with a weekly step as the default for the pre-defense-1 materials and the first experiments (the horizon stays configurable per run, 1–52 weeks); agree that it is re-checked after discussions D-1 and D-3 |
| 4 | Pre-defense-1 materials review | Milestone M1 is due 2026-10-24; the documents listed in `proposal.md` section 11 are merged; PHA2-22 (CI), PHA2-23 (frontend scaffold) and PHA2-24 (experiment runner) are in review with deadline 2026-10-23; the tag `pre-defense-1` is created from `main` after the whole team has checked the package | Birkhanym (package), all members (own areas) | `plan-and-milestones.md` section 3 (M1); `task-register.md`; `proposal.md` section 11 | Supervisor's comments on the package before the tag is created; which documents and demos to present at pre-defense 1; confirmation of the submission format (repository link, tag, summary of completed work, known limitations, outstanding tasks) |

Other open points that can be raised when time allows: the numeric acceptance targets E-01 to E-04 and E-07 of `verification-and-evaluation-plan.md` section 4.8 (marked "to be confirmed" until the first baseline run); open questions Q1–Q8 of `requirements.md` section 8 and Q-1 to Q-5 of `data-specification.md` section 12, most of which wait for the interviews.

## 5. Change log

| Date | Version | Author | Change |
|---|---|---|---|
| 2026-10-20 | 0.1 | Birkhanym Kazhymukhamet | Log created: purpose and format, entry FB-01 (justification letter of 2026-10-09) with the mapping of each point to documents and tasks, template for weekly entries, pending items for the next meeting. No meeting entries yet |
