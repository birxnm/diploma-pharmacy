# PharmaStock — Existing Systems Comparison

Task: PHA2-10 · Last updated: 2026-10-16 · Status: complete for pre-defense 1 (team review before pre-defense 1 pending) · Author: Birkhanym Kazhymukhamet

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

Ten systems were screened. A system is compared in depth when (1) it is documented on official vendor or project pages (third-party reviews are not used), (2) it manages hospital pharmacy stock or implements forecasting or shortage logic for medicines, and (3) its official documentation is sufficient to score most criteria in section 5; criteria it does not document are marked "?". Where two candidates in one category qualify, the one with the more complete stock and requisition data model is kept (OpenLMIS over DHIS2, whose Real-Time Stock app keeps only current stock on hand). Three of the four categories are represented in depth; the enterprise demand-planning category is represented by Oracle in section 4 as the methodological reference. Five systems qualify (section 3); the other five are listed in section 4 with the reason. All sources are official pages accessed in October 2026; every ✔, ◐ or ✖ cell is traceable to a URL in section 7, and claims about the systems in section 4 to section 7.1.

## 3. Systems compared in depth

| # | System | Vendor | Category | Deployment | Target users | Source |
|---|---|---|---|---|---|---|
| S1 | Omnicell Inventory Optimization Service (incl. Point of Care) | Omnicell, Inc. | Healthcare-specific | Cloud (per brochures); on-premise not documented | Hospital and health-system pharmacies using Omnicell automation | https://www.omnicell.com/inventory-optimization-service |
| S2 | Bluesight platform: KitCheck (RFID inventory) and ShortageCheck (shortage management) | Bluesight, Inc. | Healthcare-specific | Not documented (hosted web logins only) | Hospital central pharmacy, OR (operating room)/anaesthesia, crash carts, clinics | https://bluesight.com/products/ |
| S3 | Tecsys Elite Healthcare SCM (demand planning) and Elite Pharmacy Inventory Management (PIMS) | Tecsys Inc. | Healthcare-specific | SaaS / cloud; on-premise not documented | Hospitals and health systems (supply chain and pharmacy) | https://www.tecsys.com/eu/elite-healthcare-solutions/supply-chain-management |
| S4 | OpenLMIS v3 | OpenLMIS community (partners VillageReach, JSI, Chemonics) | Open-source | Self-hosted; Docker Compose reference distribution | Public-health supply chains in low-resource settings | https://openlmis.org/ |
| S5 | 1C:Medicine. Hospital Pharmacy (1С:Медицина. Больничная аптека), editions 2.0/2.1 | Firm 1C; resold in Kazakhstan by 1C partners | Regional RU/KZ | On-premises 1C:Enterprise 8.3; internet version offered by a Kazakhstan partner | Hospital pharmacy, departments and cabinets, in-hospital retail points | https://solutions.1c.ru/catalog/hospital-pharmacy/features |

## 4. Considered but not compared in depth

| System | Vendor | Category | Reason | Source |
|---|---|---|---|---|
| Oracle Fusion Cloud Demand Management | Oracle Corporation | Enterprise demand planning | Generic enterprise planner without hospital-pharmacy features; kept as the methodological reference for intermittent-demand forecasting (section 8, C3) | https://www.oracle.com/scm/supply-chain-planning/ |
| DHIS2 for Logistics / Real-Time Stock (RTS) | HISP Centre, University of Oslo | Open-source | Public-health stock reporting; forecasting limited to user-defined predictor formulas; replenishment deferred to an external eLMIS (electronic logistics management information system) | https://dhis2.org/logistics/ |
| DamuMed (КМИС Damumed, comprehensive medical information system) | ЦИТ «Даму» (Damu Centre for Information Technologies) | Regional RU/KZ | Clinical information system; hospital pharmacy modules not publicly documented; stock accounting delegated to 1C via an integration module | https://damumed.kz/ |
| 1C:MadiMed | Pervyi Bit (1cbit.kz), 1C partner | Regional RU/KZ | Only partner marketing pages available; forecasting claimed without method, horizon or evaluation | https://www.1cbit.kz/blog/1c-madimed-effektivnoe-reshenie-dlya-sovremennogo-zdravookhraneniya-v-kazakhstane/ |
| 1C-Rating: Healthcare organisation accounting for Kazakhstan | ТОО «1С-Рейтинг» (1C-Rating LLP) | Regional RU/KZ | Accounting configuration; no forecasting, alerts or analytics beyond write-off reports | https://1c-rating.kz/ |

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

C8 note: ✖ means the product is proprietary and its documentation gives no explanation of how forecasts or recommendations are derived; a missing explanation alone would score ?.

## 6. Comparison matrix

Each cell gives the score and a short evidence note; the source URL for every cell scored ✔, ◐ or ✖ is in section 7. Cells scored "?" are not sourced individually; their notes summarise the pages listed for that system.

| Criterion | S1 Omnicell | S2 Bluesight | S3 Tecsys | S4 OpenLMIS | S5 1C Hospital Pharmacy |
|---|---|---|---|---|---|
| C1 Forecasting per item | ◐ predictive analytics; no method or horizon | ◐ PAR (periodic automatic replenishment) levels from consumption trends; shortage forecast only | ◐ inventory forecasting claimed; no method | ✖ national forecast entered externally; reorder formulas | ✖ minimum-stock reordering only |
| C2 Early warning | ◐ shortage monitoring; stock-out-rate KPIs | ✔ 90-day shortage window; urgency ranking | ◐ safety-stock dips; stock-out insights | ? no shortage alerting documented | ◐ minimum-stock orders; expiry control |
| C3 Intermittent demand | ? not documented | ? not documented | ? not documented | ◐ stock-out-day scaling of consumption only | ✖ no forecasting (C1); no stock-out correction described |
| C4 Hospital pharmacy | ✔ central pharmacy and dispensing cabinets | ✔ central pharmacy, OR, crash carts | ✔ Elite PIMS: lot, expiry, cabinets | ✖ facility-to-national public-health chains | ✔ pharmacy, departments, per-patient write-off |
| C5 Integration / import | ◐ Omnicell devices; API and file import not documented | ◐ wholesaler/EHR/cabinet data; no API docs | ◐ ERP APIs, EDI (electronic data interchange); no public reference | ◐ REST API per service; file upload planned | ◐ 1C exchanges, e-documents; no REST API mentioned |
| C6 Deployment and cost | ◐ cloud; no prices | ? hosted logins; no prices | ◐ SaaS; no prices | ✔ Docker Compose; AGPL-3.0 (GNU Affero General Public License), free | ✔ on-premises; 66 100 ₽ listed |
| C7 KZ localisation | ? US benchmarks only | ? US-centric content | ? English NA/EU sites only | ? not documented | ◐ Russian regulation; sold in KZ, KZ rules not documented |
| C8 Transparency / open source | ✖ proprietary; logic not described | ✖ proprietary; model not explained | ✖ proprietary; outputs not described | ✔ AGPL-3.0; closed-form formulas | ✖ proprietary configuration |

## 7. Evidence table

One source per claim. Cells scored "?" have no supporting claim and are not listed.

| System | Criterion | Claim as documented | Source |
|---|---|---|---|
| S1 | C1 | "Predictive and prescriptive analytics"; no algorithm, horizon or accuracy | https://omnicell.com/link/c7015f80759c4027b26a2196501d4021.aspx |
| S1 | C2 | Enterprise insights "support shortage monitoring"; workflows to reduce stock-outs | https://www.omnicell.com/inventory-optimization-service |
| S1 | C4 | Built for hospital and health-system pharmacies and points of care; 282-bed hospital pharmacy case study | https://www.omnicell.com/link/7f3749ed5fa446ca8d273871aad44d28.aspx |
| S1 | C5 | Collects data "from all Omnicell-based automation technology"; "Enterprise-wide interoperability" claimed; public API and file import not documented | https://www.omnicell.com/link/3d4c636ec4b0450d8e600ba6fb45b6b7.aspx |
| S1 | C6 | "This cloud-based intelligence solution"; no prices published | https://omnicell.com/link/40037f214ffa4c8a920b5c94356f032e.aspx |
| S1 | C8 | Proprietary; prioritised actions, derivation not described | https://www.omnicell.com/inventory-optimization-service |
| S2 | C1 | Per-item PAR levels from "consumption trends"; forecasting not mentioned | https://bluesight.com/rfid-medication-management/ |
| S2 | C2 | "90 Day shortage forecast window"; "52 Day" average prediction lead time | https://bluesight.com/products/ |
| S2 | C4 | Hospital central pharmacy, OR/anaesthesia, crash carts; "Bluesight reaches 3,000+ hospital customers" (2025, vendor-reported) | https://bluesight.com/about/ |
| S2 | C5 | Integrates wholesaler, health-record, cabinet and HR data; public API not documented | https://bluesight.com/products/ |
| S2 | C8 | Proprietary; urgency ranking shown, model not explained | https://bluesight.com/drug-shortage-software/ |
| S3 | C1 | "Accurate inventory forecasting"; no algorithms, horizon or accuracy | https://www.tecsys.com/eu/elite-healthcare-solutions/supply-chain-management |
| S3 | C2 | Addresses "dips below safety stock thresholds"; insights on stock-outs | https://www.tecsys.com/eu/elite-healthcare-solutions/supply-chain-management |
| S3 | C4 | Lot/expiry tracking, DSCSA (Drug Supply Chain Security Act) compliance, carousel and cabinet visibility | https://www.tecsys.com/eu/elite-healthcare-solutions/pharmacy-inventory-management |
| S3 | C5 | "Built-in APIs that simplify connectivity with ERP"; no public API reference | https://www.tecsys.com/eu/platform |
| S3 | C6 | "A true SaaS supply chain platform"; no prices ("Speak to an expert") | https://www.tecsys.com/eu/platform |
| S3 | C8 | Proprietary; TecsysIQ mentioned without outputs or explanations | https://tecsys.com/elite-healthcare-solutions |
| S4 | C1 | "Annual national forecast needs to be entered into OpenLMIS rather than building in the various forecasting logic required" | https://openlmis.atlassian.net/wiki/rest/api/content/113323265?expand=body.storage |
| S4 | C3 | Adjusted consumption N = RoundUp(C × (M×30) / ((M×30) − X)), X = stock-out days | https://raw.githubusercontent.com/OpenLMIS/openlmis-requisition/master/src/main/java/org/openlmis/requisition/domain/requisition/LineItemFieldsCalculator.java |
| S4 | C4 | National and district public-health supply chains, not hospital dispensing | https://openlmis.org/ |
| S4 | C5 | Every service exposes "RESTful API endpoints"; HAPI FHIR service syncs facility data | https://openlmis.readthedocs.io/en/latest/components/index.html |
| S4 | C6 | Docker Compose reference distribution; AGPL-3.0 licence | https://github.com/OpenLMIS/openlmis-ref-distro |
| S4 | C8 | AGPL-3.0 source; reorder quantities are closed-form formulas | https://github.com/OpenLMIS/openlmis-requisition |
| S5 | C1 | No forecasting terms in the functional description; supplier orders by minimum stock | https://solutions.1c.ru/upload/reestr/720/udcuymrw7br1kcuufp7u8bbnju437wg8/Bolnichnaya-apteka-Funktsionalnye-vozmozhnosti.pdf |
| S5 | C2 | Processing "Supplier order generation" (3.3.3); report "Stock by expiry dates" (4.5.4) | https://its.1c.ru/db/hosppharmacydoc21 |
| S5 | C3 | No forecasting function (see C1), hence no intermittent-demand method; no stock-out correction in the functional description | https://solutions.1c.ru/upload/reestr/720/udcuymrw7br1kcuufp7u8bbnju437wg8/Bolnichnaya-apteka-Funktsionalnye-vozmozhnosti.pdf |
| S5 | C4 | Hospital pharmacy, departments and cabinets, in-hospital retail points; personified write-off to the patient record by physician orders | https://solutions.1c.ru/upload/reestr/720/udcuymrw7br1kcuufp7u8bbnju437wg8/Bolnichnaya-apteka-Funktsionalnye-vozmozhnosti.pdf |
| S5 | C5 | 1C-to-1C and regulatory data exchange; no REST/OData API mentioned | https://solutions.1c.ru/upload/reestr/720/udcuymrw7br1kcuufp7u8bbnju437wg8/Bolnichnaya-apteka-Funktsionalnye-vozmozhnosti.pdf |
| S5 | C6 | Electronic delivery 66 100 ₽ (recommended retail) | https://solutions.1c.ru/catalog/hospital-pharmacy/buy |
| S5 | C7 | Sold in Kazakhstan by a 1C partner; no Kazakhstan-specific regulatory localisation documented | https://www.1cbit.kz/1csoft/1c-meditsina-bolnichnaya-apteka/ |
| S5 | C8 | Proprietary 1C configuration; accounting-register reports only | https://solutions.1c.ru/catalog/hospital-pharmacy/features |

### 7.1 Evidence for systems considered but not compared in depth

| System | Criterion | Claim as documented | Source |
|---|---|---|---|
| Oracle | C1 | "15 forecasting methods ... based on Bayesian machine learning" | https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/25d/fasdm/forecasting-methods.html |
| Oracle | C1 | KPIs "mean absolute deviation (MAD), mean and absolute percentage error (MAPE), and bias calculations" | https://www.oracle.com/a/ocom/docs/applications/supply-chain-management/oracle-demand-management-cloud-ds.pdf |
| Oracle | C3 | "Croston for Intermittent (F)", "Regression for Intermittent (J)", "Multiplicative Monte Carlo Intermittent (K)" | https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/25d/fasdm/forecasting-methods.html |
| Oracle | C5 | Integration "using Oracle file-based data import (FBDI) and the REST API" | https://www.oracle.com/a/ocom/docs/applications/supply-chain-management/oracle-demand-management-cloud-ds.pdf |
| Oracle | C8 | Method weights shown; "No decomposed values are generated" for intermittent and naive methods | https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26a/fasdm/forecast-decomposition.html |
| DHIS2 | C1 | Predictors sample previous periods ("Sequential sample count"); no statistical model | https://docs.dhis2.org/en/use/user-guides/dhis-core-version-241/configuring-the-system/metadata.html |
| DHIS2 | C2 | Real-Time Stock "alerting managers of low stocks, over stock" | https://dhis2.org/logistics/features/ |
| DHIS2 | C8 | BSD 3-Clause licence | https://github.com/dhis2/dhis2-core |
| 1C:MadiMed | C1 | Claims "прогнозирование потребностей" and risk metric "прогноз исчерпания запасов ЛС"; no method | https://www.1cbit.kz/blog/1c-madimed-effektivnoe-reshenie-dlya-sovremennogo-zdravookhraneniya-v-kazakhstane/ |
| 1C:MadiMed | C6 | "1С:MadiMed на 12 месяцев" listed at 225 000 ₸ | https://www.1cbit.kz/1s-otrasli/avtomatizaciya-medicinskikh-i-veterinarnykh-klinik/ |
| DamuMed / 1C-Rating | C5 | 1C HTTP service "kmis": stock balances to КМИС Damumed, write-offs and their cancellation back to 1C | https://pro1c.kz/articles/uchet-v-bolnitsakh/kak-podklyuchit-modul-integratsii-kmis-damumed-v-1c-rating-bukhgalteriya-organizatsii-zdravookhrane/ |

## 8. Analysis per criterion

**C1 Demand forecasting per item.** None of the five in-depth systems documents a per-item consumption forecast with a stated method, horizon or accuracy. The commercial platforms describe forecasting at marketing level: predictive analytics (S1), PAR levels from consumption trends (S2), "accurate inventory forecasting" (S3). OpenLMIS expects national forecasts to be produced outside the system; 1C generates supplier orders from a minimum stock level. In the wider set, only Oracle documents a forecasting engine (15 methods combined by Bayesian weighting, reported with MAD (mean absolute deviation), MAPE (mean absolute percentage error) and bias); 1C:MadiMed claims forecasting without a method.

**C2 Shortage or stock-out early warning.** Among the in-depth systems, Bluesight ShortageCheck is the only documented predictive shortage warning (90-day window, urgency ranking, days on hand per site), but it is driven by market-wide supply signals from a US customer data set, not by a forecast of the hospital's own consumption. S1 and S3 offer shortage monitoring and stock-out or safety-stock KPIs; S5 relies on minimum-stock rules and expiry control, and S4 documents no shortage alerting. No system documents a risk score combining forecast, stock on hand, planned receipts and lead time.

**C3 Intermittent-demand handling.** Not documented by Omnicell, Bluesight or Tecsys; 1C Hospital Pharmacy has no forecasting at all. OpenLMIS is the only in-depth system with a stock-out correction: consumption is scaled up by manually reported stock-out days. Oracle lists Croston, intermittent regression and Monte Carlo intermittent methods, but its forecast decomposition is unavailable for them and it documents no distinction between stock-out-censored zeros and true zero demand.

**C4 Hospital-pharmacy focus.** Four of five are hospital-pharmacy products; OpenLMIS serves public-health distribution. Omnicell and KitCheck depend on their own hardware (Omnicell automation, RFID tags); Tecsys is a large health-system supply chain suite rather than a focused forecasting tool. 1C Hospital Pharmacy records the source data of PharmaStock's domain (series and expiry, department requisitions, per-patient write-offs), which PharmaStock receives only as aggregated per-item consumption (NFR-04).

**C5 Integration/API and import of accounting exports.** None of the in-depth commercial systems publishes an API reference or a file-import specification; in the wider set, Oracle documents a REST endpoint catalogue and file-based data import (FBDI) within its own cloud suite. OpenLMIS exposes REST APIs per service; 1C uses 1C-to-1C synchronisation and regulatory exchanges. Import of CSV/XLSX exports from a hospital accounting system such as 1C, the entry point PharmaStock assumes, is documented by none of the in-depth systems.

**C6 Deployment and cost model.** Prices are published only for 1C Hospital Pharmacy (66 100 ₽ electronic delivery) and, in the wider set, 1C:MadiMed (225 000 ₸ per 12 months). Omnicell and Tecsys are cloud or SaaS services and Bluesight documents only hosted web logins; none of the three publishes prices or documents an on-premise option. OpenLMIS is free (AGPL-3.0) and self-hosted with Docker Compose; PharmaStock adopts the same self-hosted Docker Compose deployment (NFR-07).

**C7 Localisation for Kazakhstan.** No Western system documents Russian or Kazakh language or local procurement rules. 1C Hospital Pharmacy is Russian-language but built around Russian regulation; its resale in Kazakhstan adds no documented localisation. The Kazakhstan-native systems (DamuMed, 1C:MadiMed, 1C-Rating) are localised; DamuMed and 1C-Rating document no forecasting, and 1C:MadiMed claims forecasting without a method. None of the ten systems documents support for the centralised procurement cycle described in `docs/proposal.md`.

**C8 Transparency/explainability and open source.** Among the in-depth systems only OpenLMIS is open source, with transparent closed-form reorder formulas; in the wider set DHIS2 is also open source (BSD 3-Clause) with user-written predictor formulas. All commercial systems are proprietary. Omnicell, Bluesight and Tecsys do not document how recommendations or forecasts are derived; Oracle documents forecast decomposition with per-method weights and causal drivers, but not for its intermittent and naive methods.

## 9. Limitations of the comparison

| Limitation | Effect |
|---|---|
| Vendor marketing | Claims come from product pages and brochures; outcome figures (65% fewer stock-outs, 52-day lead time) are vendor-reported |
| No hands-on access | No demo, trial or installation; scores reflect documentation, not tested behaviour |
| Documentation gaps | "?" cells may hide undocumented capabilities; Oracle's formulas sit behind its support portal; DamuMed's hospital modules are not public |
| Point in time | Pages accessed in October 2026; vendors change products and pages |
| Language | Russian-language sources summarised in English by the team |

## 10. Gap analysis and why PharmaStock is needed

PharmaStock targets small and medium healthcare organisations in Kazakhstan. According to the project context and assumptions in `docs/proposal.md` (to be verified in interviews), these organisations keep pharmacy stock in accounting systems, often 1C, and spreadsheets, and receive most medicines through centralised procurement with long lead times. The gaps below follow from the comparison.

| Gap | Evidence from the comparison | PharmaStock response |
|---|---|---|
| 1C-centred accounting without forecasting | The documented Kazakhstan chain is clinical write-offs in a КМИС (DamuMed) synchronised to 1C balances through the 1C-Rating integration module; 1C Hospital Pharmacy and 1C-Rating are accounting systems; no forecasting is documented in this chain, and 1C:MadiMed claims forecasting without a method | Imports CSV/XLSX exports of consumption, stock and receipts on top of the existing chain instead of replacing it |
| No open tool combining intermittent-demand forecasting with shortage risk | Intermittent methods are documented only by Oracle (enterprise SaaS, no pharmacy scope, no documented censoring); the only in-depth predictive shortage warning (Bluesight) relies on US market-wide signals plus inventory data from pharmacy automation and RFID; open-source systems use moving averages (OpenLMIS, DHIS2) and threshold alerts (DHIS2) | Weekly per-item forecast for a configurable horizon (initially 12 weeks), intermittent-demand models, stock-outs as censored demand, risk score from forecast, stock, planned receipts and lead time |
| Cost, deployment and localisation barriers of commercial suites | Omnicell, Bluesight, Tecsys and Oracle: undisclosed prices; Omnicell, Tecsys and Oracle are cloud/SaaS and Bluesight documents only hosted logins; Omnicell and KitCheck depend on their own hardware; none documents RU/KZ localisation | Self-hosted deployment with Docker Compose (NFR-07); English interface first with a localisation structure for Russian (NFR-10) |
| No transparency or published accuracy | No commercial system publishes forecast accuracy figures; Omnicell, Bluesight and Tecsys do not document how recommendations are derived, and Oracle's forecast decomposition excludes its intermittent methods | Baseline comparison with MAE and WAPE (weighted absolute percentage error) on hold-out periods; forecast shown with interval and model information |

## 11. Implications for requirements

| Finding | Requirement(s) | Implication |
|---|---|---|
| Stock data is kept in accounting systems such as 1C and in spreadsheets (`docs/proposal.md`); no in-depth system documents import of accounting exports | FR-01, FR-02, FR-18 | CSV/XLSX import with validation and data-quality summary as the primary integration path |
| No in-depth system documents a per-item forecast with method, horizon or interval | FR-06, FR-07 | Per-item forecast for a configurable horizon with history, interval and model information |
| No system combines forecast, stock, receipts and lead time into a risk list | FR-04, FR-08, FR-09, FR-10 | Lead times and planned receipts feed the risk calculation; output is a prioritised list with expected stock-out date |
| Commercial systems document neither configurable alert thresholds nor alert delivery channels; Tecsys and Oracle react to safety-stock or minimum-stock thresholds | FR-11, FR-12 | Configurable thresholds and in-app notifications for high-risk items |
| Only OpenLMIS corrects for stock-out days; none documents treating stock-outs as censored demand | FR-17 | Stock-out periods flagged so zero consumption is not learned as zero demand |
| No commercial system publishes accuracy; open-source systems provide moving-average baselines | FR-16, NFR-05 | Baselines (naive, seasonal naive, moving average, Croston-type) compared with MAE and WAPE on reproducible hold-out windows |
| Free, self-hosted deployment (OpenLMIS, DHIS2) is the only documented model without licence fees | NFR-07 | Docker Compose deployment on Linux with documented setup |
| No Western system documents RU/KZ localisation; the regional systems are Russian-language (DamuMed also Kazakh) | NFR-10 | English first with a localisation structure for Russian |

## 12. Conclusion

Commercial hospital-pharmacy platforms (Omnicell, Bluesight, Tecsys) offer shortage monitoring but document neither forecasting methods nor accuracy, publish no prices and document no localisation for Kazakhstan. Oracle documents intermittent-demand methods but has no hospital-pharmacy scope and no documented stock-out censoring. OpenLMIS and DHIS2 are free and transparent but rely on moving-average reorder or predictor formulas, with threshold alerts only in DHIS2. The Kazakhstan systems reviewed are accounting and clinical systems with no documented forecasting, except 1C:MadiMed, which claims forecasting without a disclosed method. None of the ten systems documents per-item intermittent-demand forecasting, censored stock-out handling, a risk list that accounts for planned receipts and lead time, open evaluation with MAE and WAPE, and low-cost self-hosted deployment together. PharmaStock is designed to fill this gap.
