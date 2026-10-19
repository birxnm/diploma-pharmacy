"""SQLAlchemy 2.x declarative models of the PharmaStock data entities.

Table and column names follow the data entities of the project documentation
(docs/architecture/database-schema.md) verbatim; the same names are reused in
the REST API schemas and in the import file formats. This module covers the
catalogue and the imported time series:

    medicine_item, supplier, item_supplier, import_batch,
    consumption_record, stock_snapshot, receipt, planned_receipt

The remaining entities (forecast_run, forecast, risk_assessment, notification,
app_user, audit_log, threshold_config) are added with their own tasks.

Conventions (sections 2.1 to 2.5 of the schema document):

- Weekly time series use ``period_start``, the Monday of the ISO week, as the
  period key; one row per item and week (unique constraints below).
  ``stock_snapshot.quantity_on_hand`` is the closing balance at the end of
  that week, as defined in docs/data/data-specification.md.
- Quantities are ``NUMERIC(14, 3)``: most items are counted in packs or
  tablets, but millilitres and grams occur as well. Consumption and stock may
  be zero; received and planned quantities must be positive.
- ``is_stock_out`` on ``stock_snapshot`` flags weeks in which the item was not
  available (closing balance zero), so that zero consumption in those weeks is
  treated as censored demand rather than as zero demand (FR-17).
- Enumerations are Python ``StrEnum`` classes mapped with ``sqlalchemy.Enum``
  as ``native_enum=False``: the column is a ``VARCHAR`` with a CHECK constraint
  on every dialect, and no PostgreSQL ENUM type is created (decision DB-7).
- Surrogate keys of the high-volume tables are ``bigint`` identity columns on
  PostgreSQL and JSON payloads are ``jsonb``; both are declared as dialect
  variants so that the mapping tests can run on an in-memory SQLite database.
- Referential actions follow section 2.5 of the schema document: rows that
  reference a medicine item or an import batch are never removed implicitly
  (``ON DELETE RESTRICT``); supplier links cascade with their supplier, and
  supplier references on deliveries are set to NULL.
- Constraint and index names follow the naming convention of ``app.db.base``;
  composite unique constraints and composite or partial indexes carry the
  explicit names used in the schema document. Constraints that exist only on
  PostgreSQL (the Monday check on ``period_start``) are part of the
  migrations, not of the models.
"""

import enum
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

QUANTITY = Numeric(14, 3)
# jsonb on PostgreSQL (decision DB-2 of the schema document); the portable JSON
# type on SQLite, which stores the document as text and is enough for the tests.
JSON_DOCUMENT = JSON().with_variant(JSONB(), "postgresql")
# bigint identity keys for the high-volume tables (section 2.2 of the schema
# document). SQLite assigns row ids only to INTEGER PRIMARY KEY columns, hence
# the variant.
BIG_ID = BigInteger().with_variant(Integer(), "sqlite")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# --- Enumerations -------------------------------------------------------------


class ImportSourceType(enum.StrEnum):
    """Which import file format a batch was produced from (see data specification)."""

    consumption = "consumption"
    stock = "stock"
    receipts = "receipts"
    planned_receipts = "planned_receipts"


class ImportStatus(enum.StrEnum):
    """Lifecycle of an import batch.

    ``pending`` and ``processing`` are transient while the upload is handled;
    a client reads ``completed`` (FR-01-S1) or ``failed``.
    """

    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class PlannedReceiptStatus(enum.StrEnum):
    planned = "planned"
    received = "received"
    cancelled = "cancelled"


def _enum(enum_class: type[enum.StrEnum], name: str, length: int) -> Enum:
    """``VARCHAR(length)`` plus a CHECK constraint over the enumeration values.

    ``name`` is ``<column>_values``; the naming convention turns it into
    ``ck_<table>_<column>_values`` as required by section 2.4 of the schema
    document. Values outside the enumeration are rejected by the database.
    """
    return Enum(
        enum_class,
        name=name,
        native_enum=False,
        create_constraint=True,
        length=length,
        values_callable=lambda members: [m.value for m in members],
    )


# --- Catalogue ----------------------------------------------------------------


class MedicineItem(Base):
    """A medicine item of the catalogue (FR-03). ``code`` is the identifier used in import files."""

    __tablename__ = "medicine_item"
    __table_args__ = (CheckConstraint("length(trim(code)) > 0", name="code_not_blank"),)

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    unit: Mapped[str] = mapped_column(String(32))
    # "group" is a reserved word in SQL; SQLAlchemy quotes it automatically.
    group: Mapped[str | None] = mapped_column(String(128), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))

    suppliers: Mapped[list["ItemSupplier"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )
    consumption_records: Mapped[list["ConsumptionRecord"]] = relationship(back_populates="item")
    stock_snapshots: Mapped[list["StockSnapshot"]] = relationship(back_populates="item")
    receipts: Mapped[list["Receipt"]] = relationship(back_populates="item")
    planned_receipts: Mapped[list["PlannedReceipt"]] = relationship(back_populates="item")

    def __repr__(self) -> str:
        return f"MedicineItem(id={self.id!r}, code={self.code!r})"


class Supplier(Base):
    """A supplier of medicines (FR-04), for example the central distributor or a local wholesaler."""

    __tablename__ = "supplier"

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    items: Mapped[list["ItemSupplier"]] = relationship(
        back_populates="supplier", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Supplier(id={self.id!r}, name={self.name!r})"


class ItemSupplier(Base):
    """Lead time of a supplier for an item (FR-04); the primary supplier drives the risk calculation (FR-08)."""

    __tablename__ = "item_supplier"
    __table_args__ = (
        CheckConstraint("lead_time_days >= 0", name="lead_time_nonnegative"),
        # At most one primary supplier per item (partial unique index).
        Index(
            "uq_item_supplier_primary",
            "item_id",
            unique=True,
            postgresql_where=text("is_primary"),
            sqlite_where=text("is_primary"),
        ),
    )

    item_id: Mapped[int] = mapped_column(
        ForeignKey("medicine_item.id", ondelete="RESTRICT"), primary_key=True
    )
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("supplier.id", ondelete="CASCADE"), primary_key=True
    )
    lead_time_days: Mapped[int] = mapped_column(SmallInteger)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))

    item: Mapped["MedicineItem"] = relationship(back_populates="suppliers")
    supplier: Mapped["Supplier"] = relationship(back_populates="items")


# --- Imports ------------------------------------------------------------------


class ImportBatch(Base):
    """One uploaded file (FR-01). ``summary_json`` holds validation errors and the data-quality summary (FR-02, FR-18)."""

    __tablename__ = "import_batch"

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255))
    source_type: Mapped[ImportSourceType] = mapped_column(
        _enum(ImportSourceType, "source_type_values", 32)
    )
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        index=True,
    )
    # References app_user.id; the foreign key constraint is added together with
    # the users and roles task (FR-14). Null for command-line imports.
    user_id: Mapped[int | None] = mapped_column(Integer, index=True)
    status: Mapped[ImportStatus] = mapped_column(
        _enum(ImportStatus, "status_values", 16),
        default=ImportStatus.pending,
        server_default=text("'pending'"),
    )
    summary_json: Mapped[dict[str, Any]] = mapped_column(
        JSON_DOCUMENT, default=dict, server_default=text("'{}'")
    )

    consumption_records: Mapped[list["ConsumptionRecord"]] = relationship(back_populates="import_batch")
    stock_snapshots: Mapped[list["StockSnapshot"]] = relationship(back_populates="import_batch")
    receipts: Mapped[list["Receipt"]] = relationship(back_populates="import_batch")

    def __repr__(self) -> str:
        return f"ImportBatch(id={self.id!r}, file_name={self.file_name!r}, status={self.status!r})"


# --- Weekly time series -------------------------------------------------------


class ConsumptionRecord(Base):
    """Consumption of an item in one week (``consumption.csv``)."""

    __tablename__ = "consumption_record"
    __table_args__ = (
        UniqueConstraint("item_id", "period_start", name="uq_consumption_record_item_period"),
        CheckConstraint("quantity >= 0", name="quantity_nonnegative"),
    )

    id: Mapped[int] = mapped_column(BIG_ID, Identity(always=True), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("medicine_item.id", ondelete="RESTRICT"))
    period_start: Mapped[date] = mapped_column(Date, index=True)
    quantity: Mapped[Decimal] = mapped_column(QUANTITY)
    # The batch that last wrote the row; a batch with rows cannot be deleted.
    import_batch_id: Mapped[int] = mapped_column(
        ForeignKey("import_batch.id", ondelete="RESTRICT"), index=True
    )

    item: Mapped["MedicineItem"] = relationship(back_populates="consumption_records")
    import_batch: Mapped["ImportBatch"] = relationship(back_populates="consumption_records")


class StockSnapshot(Base):
    """Closing stock balance of an item at the end of one week (``stock.csv``), with the stock-out flag (FR-17)."""

    __tablename__ = "stock_snapshot"
    __table_args__ = (
        UniqueConstraint("item_id", "period_start", name="uq_stock_snapshot_item_period"),
        CheckConstraint("quantity_on_hand >= 0", name="quantity_nonnegative"),
        # Stock-out weeks only: used to build the censoring mask of a history.
        Index(
            "ix_stock_snapshot_stock_out",
            "item_id",
            "period_start",
            postgresql_where=text("is_stock_out"),
            sqlite_where=text("is_stock_out"),
        ),
    )

    id: Mapped[int] = mapped_column(BIG_ID, Identity(always=True), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("medicine_item.id", ondelete="RESTRICT"))
    period_start: Mapped[date] = mapped_column(Date)
    quantity_on_hand: Mapped[Decimal] = mapped_column(QUANTITY)
    is_stock_out: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    import_batch_id: Mapped[int] = mapped_column(
        ForeignKey("import_batch.id", ondelete="RESTRICT"), index=True
    )

    item: Mapped["MedicineItem"] = relationship(back_populates="stock_snapshots")
    import_batch: Mapped["ImportBatch"] = relationship(back_populates="stock_snapshots")


# --- Deliveries ---------------------------------------------------------------


class Receipt(Base):
    """A delivery that was received (``receipts.csv``).

    One row per item, delivery date and supplier; the importer sums the lines
    of a file that share these three values, so that a re-import is idempotent.
    """

    __tablename__ = "receipt"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
        # NULLS NOT DISTINCT (PostgreSQL 15+) makes rows without a supplier
        # unique as well; on SQLite the constraint is a plain UNIQUE.
        UniqueConstraint(
            "item_id",
            "received_on",
            "supplier_id",
            name="uq_receipt_item_date_supplier",
            postgresql_nulls_not_distinct=True,
        ),
        Index("ix_receipt_item_id_received_on", "item_id", "received_on"),
    )

    id: Mapped[int] = mapped_column(BIG_ID, Identity(always=True), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("medicine_item.id", ondelete="RESTRICT"))
    received_on: Mapped[date] = mapped_column(Date)
    quantity: Mapped[Decimal] = mapped_column(QUANTITY)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("supplier.id", ondelete="SET NULL"))
    import_batch_id: Mapped[int] = mapped_column(
        ForeignKey("import_batch.id", ondelete="RESTRICT"), index=True
    )

    item: Mapped["MedicineItem"] = relationship(back_populates="receipts")
    supplier: Mapped["Supplier | None"] = relationship()
    import_batch: Mapped["ImportBatch"] = relationship(back_populates="receipts")


class PlannedReceipt(Base):
    """An expected delivery (FR-10, ``planned_receipts.csv``); counted in the projected stock of the risk calculation (FR-08)."""

    __tablename__ = "planned_receipt"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
        Index("ix_planned_receipt_item_id_expected_on", "item_id", "expected_on"),
        # The risk calculation reads only `planned` rows inside the horizon.
        Index("ix_planned_receipt_status_expected_on", "status", "expected_on"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("medicine_item.id", ondelete="RESTRICT"))
    expected_on: Mapped[date] = mapped_column(Date)
    quantity: Mapped[Decimal] = mapped_column(QUANTITY)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("supplier.id", ondelete="SET NULL"))
    status: Mapped[PlannedReceiptStatus] = mapped_column(
        _enum(PlannedReceiptStatus, "status_values", 16),
        default=PlannedReceiptStatus.planned,
        server_default=text("'planned'"),
    )

    item: Mapped["MedicineItem"] = relationship(back_populates="planned_receipts")
    supplier: Mapped["Supplier | None"] = relationship()
