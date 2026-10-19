"""Schema and mapping tests for app.db.models on an in-memory SQLite database.

SQLite stands in for PostgreSQL here: the PostgreSQL-only types of the schema
document (bigint identity keys, jsonb) are declared as dialect variants, so the
schema can be created and exercised without a running database server. The
constraints that exist only on PostgreSQL (the Monday check on period_start,
NULLS NOT DISTINCT) are left to the migration tests planned in the
verification plan.
"""

from collections.abc import Iterator
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import Engine, create_engine, delete, event, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import (
    ConsumptionRecord,
    ImportBatch,
    ImportSourceType,
    ImportStatus,
    ItemSupplier,
    MedicineItem,
    PlannedReceipt,
    PlannedReceiptStatus,
    Receipt,
    StockSnapshot,
    Supplier,
)

ENTITY_TABLES = {
    "medicine_item",
    "supplier",
    "item_supplier",
    "import_batch",
    "consumption_record",
    "stock_snapshot",
    "receipt",
    "planned_receipt",
}

WEEK = date(2026, 10, 12)  # a Monday: period_start is always the first day of the ISO week


@pytest.fixture
def engine() -> Iterator[Engine]:
    engine = create_engine("sqlite+pysqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def _enforce_foreign_keys(dbapi_connection, _connection_record) -> None:  # noqa: ANN001
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    with Session(engine) as session:
        yield session


def _metformin() -> MedicineItem:
    return MedicineItem(
        code="A10BA02", name="Metformin 500 mg tablets", unit="tablet", group="A10 Drugs used in diabetes"
    )


def _batch(source_type: ImportSourceType = ImportSourceType.consumption) -> ImportBatch:
    return ImportBatch(
        file_name=f"{source_type.value}.csv", source_type=source_type, status=ImportStatus.completed
    )


def test_schema_contains_all_entity_tables(engine: Engine) -> None:
    assert ENTITY_TABLES <= set(inspect(engine).get_table_names())


def test_constraint_and_index_names_follow_the_schema_document(engine: Engine) -> None:
    inspector = inspect(engine)

    def names(rows: list[dict]) -> set[str]:
        return {row["name"] for row in rows}

    assert names(inspector.get_unique_constraints("medicine_item")) == {"uq_medicine_item_code"}
    assert names(inspector.get_check_constraints("medicine_item")) == {"ck_medicine_item_code_not_blank"}
    assert names(inspector.get_check_constraints("item_supplier")) == {
        "ck_item_supplier_lead_time_nonnegative"
    }
    assert names(inspector.get_check_constraints("import_batch")) == {
        "ck_import_batch_source_type_values",
        "ck_import_batch_status_values",
    }
    assert names(inspector.get_unique_constraints("consumption_record")) == {
        "uq_consumption_record_item_period"
    }
    assert names(inspector.get_check_constraints("consumption_record")) == {
        "ck_consumption_record_quantity_nonnegative"
    }
    assert names(inspector.get_unique_constraints("stock_snapshot")) == {"uq_stock_snapshot_item_period"}
    assert names(inspector.get_check_constraints("receipt")) == {"ck_receipt_quantity_positive"}
    assert names(inspector.get_unique_constraints("receipt")) == {"uq_receipt_item_date_supplier"}
    assert names(inspector.get_check_constraints("planned_receipt")) == {
        "ck_planned_receipt_quantity_positive",
        "ck_planned_receipt_status_values",
    }
    assert {"ix_receipt_item_id_received_on", "ix_receipt_import_batch_id"} <= names(
        inspector.get_indexes("receipt")
    )
    assert {"ix_stock_snapshot_stock_out", "ix_stock_snapshot_import_batch_id"} <= names(
        inspector.get_indexes("stock_snapshot")
    )
    assert {"ix_import_batch_imported_at", "ix_import_batch_user_id"} <= names(
        inspector.get_indexes("import_batch")
    )
    assert "uq_item_supplier_primary" in names(inspector.get_indexes("item_supplier"))


def test_insert_item_and_consumption_record(session: Session) -> None:
    item = _metformin()
    batch = _batch()
    record = ConsumptionRecord(item=item, import_batch=batch, period_start=WEEK, quantity=Decimal("120"))
    session.add_all([item, batch, record])
    session.commit()

    loaded = session.scalars(
        select(ConsumptionRecord).join(MedicineItem).where(MedicineItem.code == "A10BA02")
    ).one()

    assert loaded.item.name == "Metformin 500 mg tablets"
    assert loaded.item.is_active is True
    assert loaded.period_start == WEEK
    assert loaded.quantity == Decimal("120")
    assert loaded.import_batch_id == batch.id
    assert loaded.import_batch.summary_json == {}  # default: no summary yet


def test_one_consumption_row_per_item_and_week(session: Session) -> None:
    item = _metformin()
    batch = _batch()
    session.add(ConsumptionRecord(item=item, import_batch=batch, period_start=WEEK, quantity=Decimal("10")))
    session.commit()

    session.add(ConsumptionRecord(item=item, import_batch=batch, period_start=WEEK, quantity=Decimal("11")))
    with pytest.raises(IntegrityError):
        session.commit()


def test_negative_quantity_is_rejected(session: Session) -> None:
    session.add(
        ConsumptionRecord(item=_metformin(), import_batch=_batch(), period_start=WEEK, quantity=Decimal("-1"))
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_consumption_record_requires_an_import_batch(session: Session) -> None:
    session.add(ConsumptionRecord(item=_metformin(), period_start=WEEK, quantity=Decimal("1")))
    with pytest.raises(IntegrityError):
        session.commit()


def test_import_batch_links_records_and_keeps_summary(session: Session) -> None:
    item = _metformin()
    summary = {"rows_total": 1, "rows_imported": 1, "errors_total": 0, "errors": [], "items_affected": 1}
    batch = ImportBatch(
        file_name="consumption.csv",
        source_type=ImportSourceType.consumption,
        status=ImportStatus.completed,
        summary_json=summary,
    )
    session.add(ConsumptionRecord(item=item, import_batch=batch, period_start=WEEK, quantity=Decimal("5")))
    session.commit()

    loaded = session.scalars(select(ImportBatch)).one()

    assert loaded.imported_at is not None
    assert loaded.source_type is ImportSourceType.consumption
    assert loaded.status is ImportStatus.completed
    assert loaded.summary_json == summary
    assert [r.quantity for r in loaded.consumption_records] == [Decimal("5")]


def test_import_status_outside_the_enumeration_is_rejected(session: Session) -> None:
    # The values are checked by the database (varchar + CHECK), not only by Python.
    session.add(ImportBatch(file_name="stock.csv", source_type=ImportSourceType.stock, status="archived"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_import_batch_with_loaded_rows_cannot_be_deleted(session: Session) -> None:
    batch = _batch()
    session.add(ConsumptionRecord(item=_metformin(), import_batch=batch, period_start=WEEK, quantity=Decimal("1")))
    session.commit()

    # ON DELETE RESTRICT: corrections are made by re-importing, never by deleting a batch.
    with pytest.raises(IntegrityError):
        session.execute(delete(ImportBatch).where(ImportBatch.id == batch.id))


def test_supplier_lead_time_and_deliveries(session: Session) -> None:
    item = _metformin()
    supplier = Supplier(name="Central distributor")
    session.add_all(
        [
            ItemSupplier(item=item, supplier=supplier, lead_time_days=21, is_primary=True),
            Receipt(
                item=item,
                supplier=supplier,
                import_batch=_batch(ImportSourceType.receipts),
                received_on=date(2026, 10, 14),
                quantity=Decimal("500"),
            ),
            PlannedReceipt(item=item, supplier=supplier, expected_on=date(2026, 11, 4), quantity=Decimal("500")),
        ]
    )
    session.commit()

    loaded = session.scalars(select(MedicineItem)).one()

    assert [(s.supplier.name, s.lead_time_days, s.is_primary) for s in loaded.suppliers] == [
        ("Central distributor", 21, True)
    ]
    assert loaded.receipts[0].quantity == Decimal("500")
    assert loaded.planned_receipts[0].status is PlannedReceiptStatus.planned


def test_delivered_and_planned_quantities_must_be_positive(session: Session) -> None:
    item = _metformin()
    session.add(item)
    session.commit()

    session.add(
        Receipt(item=item, import_batch=_batch(ImportSourceType.receipts), received_on=WEEK, quantity=Decimal("0"))
    )
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

    session.add(PlannedReceipt(item=item, expected_on=date(2026, 11, 4), quantity=Decimal("0")))
    with pytest.raises(IntegrityError):
        session.commit()


def test_stock_snapshot_marks_stock_out_week(session: Session) -> None:
    item = _metformin()
    session.add_all(
        [
            StockSnapshot(
                item=item,
                import_batch=_batch(ImportSourceType.stock),
                period_start=WEEK,
                quantity_on_hand=Decimal("0"),
                is_stock_out=True,
            ),
            ConsumptionRecord(item=item, import_batch=_batch(), period_start=WEEK, quantity=Decimal("0")),
        ]
    )
    session.commit()

    snapshot = session.scalars(select(StockSnapshot)).one()

    # A zero closing balance marks the week as a stock-out (AC-17.1); zero
    # consumption in that week is censored demand (FR-17), not zero demand.
    assert snapshot.is_stock_out is True
    assert snapshot.quantity_on_hand == Decimal("0")


def test_consumption_record_requires_existing_item(session: Session) -> None:
    session.add(ConsumptionRecord(item_id=999, import_batch=_batch(), period_start=WEEK, quantity=Decimal("1")))
    with pytest.raises(IntegrityError):
        session.commit()
