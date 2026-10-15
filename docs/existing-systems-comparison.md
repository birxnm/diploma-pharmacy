# PharmaStock — Existing Systems Comparison

Task: PHA2-10 · Last updated: 2026-10-15 · Status: draft v0.1 (comparison matrix: evidence being collected) · Author: Birkhanym Kazhymukhamet

---

## 1. Purpose

This document compares existing systems that manage pharmaceutical inventory or forecast demand against the goals of PharmaStock, the system developed in the diploma project "Development of smart supply chain analytics system for forecasting pharmaceutical inventory and preventing medicine shortages in healthcare organizations" (Astana IT University, School of Software Engineering, group SE-2414, 2026–2027). It establishes which systems already solve parts of the problem, what they document and leave undocumented, and where the gap is that justifies PharmaStock for healthcare organisations in Kazakhstan. The findings feed `docs/proposal.md`, `docs/requirements.md` (FR-01..FR-18, NFR-01..NFR-10) and `docs/literature-review.md`.

## 2. Selection method

Candidates were collected in four categories that cover the ways a healthcare organisation in Kazakhstan could obtain forecasting or shortage-prevention functionality today.

| Category | Why it is relevant | Candidates screened |
|---|---|---|
| Healthcare-specific inventory platforms | Built for hospital pharmacies; closest functional analogues | Omnicell Inventory Optimization Service; Bluesight (KitCheck / ShortageCheck); Tecsys Elite Healthcare |
| Enterprise demand planning | Mature statistical forecasting, including intermittent demand | Oracle Fusion Cloud Demand Management |
| Open-source public-health logistics | Free, self-hosted systems for medicine supply chains | OpenLMIS v3; DHIS2 for Logistics (Real-Time Stock) |
| Regional RU/KZ systems | Systems sold or deployed in Kazakhstan for hospital stock accounting | 1C:Medicine. Hospital Pharmacy; DamuMed; 1C:MadiMed; 1C-Rating healthcare accounting |

Ten systems were screened. A system is compared in depth when (1) it is documented on official vendor or project pages (third-party reviews are not used), (2) it manages hospital pharmacy stock or implements forecasting or shortage logic for medicines, and (3) its official documentation is sufficient to score most criteria in section 5; criteria it does not document are marked "?". Where two candidates in one category qualify, the one with the more complete stock and requisition data model is kept (OpenLMIS over DHIS2, whose Real-Time Stock app keeps only current stock on hand). Three of the four categories are represented in depth; the enterprise demand-planning category is represented by Oracle in section 4 as the methodological reference. Five systems qualify (section 3); the other five are listed in section 4 with the reason. All sources are official pages accessed in October 2026; every scored claim will be traceable to a source URL once the matrix is filled.

## 3. Systems compared in depth

| # | System | Vendor | Category | Deployment | Target users | Source |
|---|---|---|---|---|---|---|
| S1 | Omnicell Inventory Optimization Service (incl. Point of Care) | Omnicell, Inc. | Healthcare-specific | Cloud (per brochures); on-premise not documented | Hospital and health-system pharmacies using Omnicell automation | https://www.omnicell.com/inventory-optimization-service |
| S2 | Bluesight platform: KitCheck (RFID inventory) and ShortageCheck (shortage management) | Bluesight, Inc. | Healthcare-specific | Not documented (hosted web logins only) | Hospital central pharmacy, OR/anaesthesia, crash carts, clinics | https://bluesight.com/products/ |
| S3 | Tecsys Elite Healthcare SCM (demand planning) and Elite Pharmacy Inventory Management (PIMS) | Tecsys Inc. | Healthcare-specific | SaaS / cloud; on-premise not documented | Hospitals and health systems (supply chain and pharmacy) | https://www.tecsys.com/eu/elite-healthcare-solutions/supply-chain-management |
| S4 | OpenLMIS v3 | OpenLMIS community (partners VillageReach, JSI, Chemonics) | Open-source | Self-hosted; Docker Compose reference distribution | Public-health supply chains in low-resource settings | https://openlmis.org/ |
| S5 | 1C:Medicine. Hospital Pharmacy (1С:Медицина. Больничная аптека), editions 2.0/2.1 | Firm 1C; resold in Kazakhstan by 1C partners | Regional RU/KZ | On-premises 1C:Enterprise 8.3; internet version offered by a Kazakhstan partner | Hospital pharmacy, departments and cabinets, in-hospital retail points | https://solutions.1c.ru/catalog/hospital-pharmacy/features |

## 4. Considered but not compared in depth

| System | Vendor | Category | Reason | Source |
|---|---|---|---|---|
| Oracle Fusion Cloud Demand Management | Oracle Corporation | Enterprise demand planning | Generic enterprise planner without hospital-pharmacy features; kept as the methodological reference for intermittent-demand forecasting | https://www.oracle.com/scm/supply-chain-planning/ |
| DHIS2 for Logistics / Real-Time Stock (RTS) | HISP Centre, University of Oslo | Open-source | Public-health stock reporting; forecasting limited to user-defined predictor formulas; replenishment deferred to an external eLMIS | https://dhis2.org/logistics/ |
| DamuMed (КМИС Damumed) | ЦИТ «Даму» | Regional RU/KZ | Clinical information system; hospital pharmacy modules not publicly documented; stock accounting delegated to 1C via an integration module | https://damumed.kz/ |
| 1C:MadiMed | Pervyi Bit (1cbit.kz), 1C partner | Regional RU/KZ | Only partner marketing pages available; forecasting claimed without method, horizon or evaluation | https://www.1cbit.kz/blog/1c-madimed-effektivnoe-reshenie-dlya-sovremennogo-zdravookhraneniya-v-kazakhstane/ |
| 1C-Rating: Healthcare organisation accounting for Kazakhstan | ТОО «1С-Рейтинг» | Regional RU/KZ | Accounting configuration; no forecasting, alerts or analytics beyond write-off reports | https://1c-rating.kz/ |

## 5. Comparison criteria

| ID | Criterion | Definition | ✔ requires |
|---|---|---|---|
| C1 | Demand forecasting per item | Forward-looking consumption forecast for each stock item | Documented method or item-level forecast output |
| C2 | Shortage or stock-out early warning | Warns before an item runs out, using stock and expected consumption | Documented risk score, alert or ranked list of items at risk |
| C3 | Intermittent-demand handling | Methods for sporadic demand and treatment of stock-out periods as censored demand | Documented intermittent-demand method (e.g., Croston-type) and documented treatment of stock-out periods; one of the two, or a heuristic stock-out correction, scores ◐ |
| C4 | Hospital-pharmacy focus | Designed for the pharmacy warehouse, department requisitions and dispensing inside a hospital | Explicit hospital-pharmacy scope |
| C5 | Integration/API and import of accounting exports | Receives data from external systems through an API and file import (e.g., CSV/XLSX exports from 1C) | Documented public API and documented file import; one of the two, or integration claimed only at marketing level, scores ◐ |
| C6 | Deployment and cost model | How the system is hosted and what it costs | Documented deployment option and published price or licence |
| C7 | Localisation for Kazakhstan | Russian/Kazakh language and support for local procurement rules | Documented RU/KZ language and Kazakhstan regulatory scope |
| C8 | Transparency/explainability and open source | Source code is open and/or the forecasting logic is explained to the user | Open licence or documented explanation of forecasts |

Scoring scale:

| Score | Meaning |
|---|---|
| ✔ documented | The capability is described on an official page |
| ◐ partial | Described in part, or only at marketing level without method or detail |
| ✖ absent | Official documentation confirms the capability is missing |
| ? not documented | No official evidence either way; treated as absent but not asserted |

## 6. Comparison matrix

Status: evidence being collected. Scores and supporting evidence (one URL per claim) will be added in the next revision.

| Criterion | S1 Omnicell | S2 Bluesight | S3 Tecsys | S4 OpenLMIS | S5 1C Hospital Pharmacy |
|---|---|---|---|---|---|
| C1 Forecasting per item | pending | pending | pending | pending | pending |
| C2 Early warning | pending | pending | pending | pending | pending |
| C3 Intermittent demand | pending | pending | pending | pending | pending |
| C4 Hospital pharmacy | pending | pending | pending | pending | pending |
| C5 Integration / import | pending | pending | pending | pending | pending |
| C6 Deployment and cost | pending | pending | pending | pending | pending |
| C7 KZ localisation | pending | pending | pending | pending | pending |
| C8 Transparency / open source | pending | pending | pending | pending | pending |

## 7. Next steps

| Step | Target date |
|---|---|
| Fill the matrix with scores and 3–8 word evidence per cell | 2026-10-16 |
| Add the evidence table (one source URL per claim) | 2026-10-16 |
| Add analysis per criterion, limitations, gap analysis and implications for requirements | 2026-10-16 |
| Review with the team before pre-defense 1 | 2026-10-20 |
