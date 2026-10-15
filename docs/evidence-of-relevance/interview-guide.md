# Interview guide: pharmaceutical stock management in a healthcare organization

`PHA2-7` · Evidence of relevance · Last updated: 2026-10-15 · Author: Birkhanym Kazhymukhamet

Semi-structured guide for the discussions planned in [stakeholders.md](./stakeholders.md) (D-1 to D-5). The guide is a checklist, not a script: the interviewer follows the participant's own description of the work and uses the questions to make sure every topic is covered. Findings are recorded in the [interview log](./interview-log.md).

## 1. Format

| Item | Value |
|------|-------|
| Duration | 20–60 minutes depending on the role (see section 5) |
| Participants from the team | One interviewer (leads the conversation), one note-taker (records answers and open questions) |
| Mode | In person at the organization where possible; otherwise video call |
| Language | Kazakh or Russian, at the participant's choice; the log is written in English |
| Materials | This guide, a printed one-page summary of the project idea, paper for sketching the current process; the UX mockups from `prototype/` are shown only in block H, after the participant has described their own work, to avoid leading answers |
| Recording | Notes by default; audio only with explicit consent, deleted after the write-up |

## 2. Introduction (read to the participant)

> We are a team of three students of Astana IT University. For our diploma project we are developing a prototype of an analytics tool that forecasts the consumption of medicines in a hospital or polyclinic and warns in advance when an item is likely to run out. Before building it, we want to understand how stock is managed today and what would actually help. There are no right or wrong answers; we are interested in how things work in practice, including problems.
>
> Participation is voluntary. You can skip any question or stop at any time. We will take notes; we will record audio only if you agree, and the recording will be deleted once the notes are written. We will not write down your name or the name of your organization; our project log will say only your role (for example "head of pharmacy") and the type of organization (for example "hospital"). We are not asking about any patient, and we will not look at any patient data. If you can later share exports of consumption or stock data, we would need only item-level totals per period, with no patient information.
>
> Do you have any questions before we start? May we begin?

Record the participant's consent (yes / no) and whether audio recording was agreed in the log.

## 3. Question blocks

The expected answer type and the requirement or assumption each block tests are given so that the note-taker can tag findings immediately. Assumption IDs (A-xx) refer to the table in the [interview log](./interview-log.md#3-verified-findings-vs-assumptions).

### Block A. Role and context (5 min)

| # | Question | Tests |
|---|----------|-------|
| A1 | What is your role, and which part of medicine supply are you responsible for? | role model (FR-14) |
| A2 | Roughly how many different medicine items does your pharmacy handle? How many of them are used regularly? | NFR-01, NFR-02, A-02 |
| A3 | Who else is involved in deciding what and when to order? | S1–S5 stakeholder map |

### Block B. Current process of stock accounting (10 min)

| # | Question | Tests |
|---|----------|-------|
| B1 | Where is stock information kept today: an accounting system, spreadsheets, paper journals, several of these? | A-01 |
| B2 | Who enters consumption, receipts and current stock, and how often (daily, weekly, monthly)? | A-06, FR-01 |
| B3 | At what level is consumption recorded: per item, per batch, per department, per pack or per unit? | FR-03, data specification |
| B4 | How is the current stock level checked: continuous record, periodic inventory count, both? How often does the recorded stock differ from the physical stock? | FR-05, FR-18 |
| B5 | Could you walk us through what happens from the moment a medicine is received to the moment it is issued to a department? | process observation |

### Block C. How shortages are detected today (10 min)

| # | Question | Tests |
|---|----------|-------|
| C1 | How do you find out that an item is about to run out? Who notices first? | A-04 |
| C2 | How much time usually passes between the moment stock becomes critically low and the moment it is noticed? | A-04, risk-level definition |
| C3 | What happens when a shortage occurs: substitution, borrowing from another organization, urgent purchase, postponed treatment? | problem statement |
| C4 | How often does this happen: per month, per quarter? Which kinds of items are affected most? | problem statement, error analysis per group |
| C5 | Do you also have the opposite problem: items that are overstocked or expire before use? How are those identified? | A-05 |
| C6 | Is a period when an item was out of stock written down anywhere? Would it be possible to tell, from your records, that zero consumption in a week was due to absence of stock rather than absence of need? | A-08, FR-17 |

### Block D. Data available and formats (10 min)

| # | Question | Tests |
|---|----------|-------|
| D1 | Can the accounting system export data to a file (XLSX, CSV, other)? Who can do that, and how long does it take? | A-01, FR-01 |
| D2 | What does an export contain: columns, period granularity (per day, week, month), item identifiers? | data specification, import formats |
| D3 | How far back does the history go? Are earlier years still accessible? | A-13 |
| D4 | Do item codes and names stay the same over time, or are items renamed, merged or re-coded (for example when the supplier or packaging changes)? | A-14, FR-02, FR-03 |
| D5 | Are receipts recorded with the supplier and date? Are expected deliveries recorded before they arrive? | FR-04, FR-10, A-09 |
| D6 | What data quality problems do you know of: missing entries, late entries, negative or corrected quantities, duplicate records? | FR-02, FR-18 |

### Block E. Lead times and procurement (10 min)

| # | Question | Tests |
|---|----------|-------|
| E1 | Which items come through the single distributor (SK-Pharmacy) and which are bought by the organization itself? Roughly in what proportion? | A-03 |
| E2 | For centralised supply: when are needs submitted, how are they calculated, and when do deliveries arrive? Can the plan be adjusted during the year, and how long does that take? | A-03, lead-time model |
| E3 | For own purchases: how long from the decision to order to the delivery, in a typical and in a bad case? | `item_supplier.lead_time_days`, FR-04 |
| E4 | Are delivery dates and quantities known in advance? How often are deliveries partial or late? | FR-10, A-09, risk logic |
| E5 | Are there items with special constraints (cold chain, controlled substances, short shelf life) that change how far ahead you must plan? | limitations, FR-11 |

### Block F. Decision rules (5–10 min)

| # | Question | Tests |
|---|----------|-------|
| F1 | How do you decide how much of an item to order? Is there a rule such as "keep N weeks of stock" or a minimum quantity per item? | A-11, FR-11, safety-stock parameter |
| F2 | Do you take seasonality into account (for example respiratory infections in winter)? How? | seasonal_naive baseline, A-02 |
| F3 | How do you handle new items with no history, or items whose use changed because of a new protocol or a new department? | model limitations, FR-06 |
| F4 | How far ahead do you need to know about a likely shortage for the information to be useful? One week, one month, one quarter? | A-07 (12-week horizon), risk levels |
| F5 | Would you prefer to see the forecast as a number per week, as a date when stock runs out, or as a traffic-light risk level? | FR-07, FR-09 |

### Block G. Pain points (5 min)

| # | Question | Tests |
|---|----------|-------|
| G1 | What are the three most time-consuming or frustrating parts of stock management for you? | prioritisation of FR-xx |
| G2 | If one thing about the current process could be changed, what would it be? | scope check |
| G3 | How much of your week goes into checking stock, preparing orders and preparing reports? | expected outcomes |

### Block H. Acceptance of a forecasting tool (10 min)

Show the one-page summary and, if time allows, the UX mockups from `prototype/`.

| # | Question | Tests |
|---|----------|-------|
| H1 | Based on what we described, would such a tool be useful in your work? For which tasks? | relevance |
| H2 | What would make you trust or distrust an automated forecast? What would you want to see next to the number (history, confidence interval, the method used)? | FR-07, FR-16 |
| H3 | Who in your organization would use the tool, and how often: daily, weekly, before each procurement round? | roles, FR-12 |
| H4 | How should the tool notify you about high-risk items: a list in the application, an email, a printed report? | FR-12, FR-13 |
| H5 | Would you be allowed to install such a tool on a computer or server in the organization? Who would need to approve it? What about access to the internet from that machine? | NFR-07, S5 questions |
| H6 | What would be unacceptable (for example sending data outside the organization, extra manual data entry, English-only interface)? | NFR-04, NFR-10, barriers |
| H7 | Is a weekly update of the forecast sufficient, or would you need it more often? | A-06 |

### Block I. Closing (5 min)

| # | Question | Tests |
|---|----------|-------|
| I1 | Is there anything important about stock management that we did not ask? | coverage |
| I2 | Is there a colleague in a different role we should talk to? | D-3 to D-5 scheduling |
| I3 | May we contact you again with follow-up questions, and would you be willing to look at a prototype later in the project (around January 2027)? | user testing plan |

## 4. Role-specific additions

| Role | Additional questions |
|------|----------------------|
| IT administrator (D-4) | Which accounting system and version is in use; whether it can export on a schedule or only manually; whether a virtual machine or server with Linux is available; who manages user accounts and whether an organization-wide login (directory service) exists; requirements for HTTPS, backups and audit; whether Docker is allowed. Blocks B, D and H5–H6 are the core; blocks C, E, F can be skipped. |
| Head of clinical department (D-5) | How the department learns about shortages and substitutions today; which medicines are critical for the department; whether a read-only view of at-risk items would be used and how often; preferred notification channel. Blocks A, C, G, H are the core; blocks B, D, E are skipped. |
| Procurement and supply specialist (D-3) | Blocks E and D in full; F1 and F4; H3–H4. Ask specifically about the annual needs calculation for centralised supply and how adjustments during the year are requested. |

## 5. Time plan per discussion

| Discussion | Blocks | Planned duration |
|------------|--------|------------------|
| D-1 Head of hospital pharmacy | A–I (full guide) | 50–60 min |
| D-2 Pharmacist | A, B, C, D, G, H, I (+ observation of the workflow) | 40–45 min |
| D-3 Procurement specialist | A, D, E, F (F1, F4), H, I | 35–45 min |
| D-4 IT administrator | A, B (B1), D, H (H5, H6), I | 20–30 min |
| D-5 Head of clinical department | A, C, G, H, I | 20 min |

## 6. After the discussion

1. Within two working days the note-taker writes up the notes in English and the interviewer checks them.
2. Each statement that answers a question is entered in the [interview log](./interview-log.md) as a key finding, tagged with the discussion ID, the block and question number, and the affected requirement or assumption ID.
3. For each assumption in the log, decide: **confirmed** (the participant stated it or showed it), **contradicted** (the participant stated the opposite), or **still an assumption** (not discussed or unclear). A single confirmation moves the assumption to "verified finding" with its source; a contradiction opens a change proposal for the affected requirement.
4. New facts that were not in the assumptions list are added as verified findings with their source.
5. If the participant agreed to share data exports, the request is passed to Evelina Penkova and recorded in the "Analysis of available data" section of the log.

## 7. Consent and personal data

- The introduction in section 2 must be read in full before the first question.
- Consent and recording agreement are recorded as yes/no in the log; no name, contact detail or organization name is stored in the repository.
- No question in this guide asks about any patient, prescription or individual treatment, and the interviewer must not note such information even if it is mentioned. Data exports, if offered, must be limited to item-level totals per period (see [data specification](../data/data-specification.md)).
- Notes and any audio are kept by the interviewer outside the repository and are deleted at the end of the project.
