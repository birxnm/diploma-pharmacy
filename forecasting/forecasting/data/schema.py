"""Schema of the input frames of the forecasting package.

Column names, expected dtypes and the weekly frequency are defined once here
and reused by validation, series preparation and the API. The names follow the
import file formats (``consumption.csv``, ``stock.csv``, ``receipts.csv``) and
the database entities ``consumption_record``, ``stock_snapshot`` and
``receipt`` described in ``docs/architecture/database-schema.md``.

Conventions (FQ-01):

* the time step is one calendar week;
* ``period_start`` is the Monday of the week, an ISO date without a time part;
* quantities are non-negative numbers in the item's unit of measurement.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

# Weekly frequency anchored on Monday (pandas offset alias). Every period in
# the package is identified by its Monday.
WEEKLY_FREQ = "W-MON"
PERIOD_DAYS = 7
MONDAY = 0  # value of ``Series.dt.weekday`` for Monday

# Forecast horizon in weeks (FQ-03).
MIN_HORIZON_WEEKS = 1
MAX_HORIZON_WEEKS = 52
DEFAULT_HORIZON_WEEKS = 12

# Column names shared by the frames.
ITEM_CODE = "item_code"
ITEM_NAME = "item_name"
UNIT = "unit"
PERIOD_START = "period_start"
QUANTITY = "quantity"
QUANTITY_ON_HAND = "quantity_on_hand"
RECEIVED_ON = "received_on"
SUPPLIER = "supplier"
IS_STOCK_OUT = "is_stock_out"
# Added by ``make_regular_weekly``: True for weeks that were absent from the
# input and were filled with the fill value.
IS_FILLED = "is_filled"

# Target dtypes after validation (pandas dtype strings).
STRING = "str"
DATE = "datetime64[ns]"
FLOAT = "float64"
BOOL = "bool"


@dataclass(frozen=True)
class FrameSchema:
    """Describes one tabular input of the package.

    Attributes:
        name: Short name used in error messages.
        required: Columns that must be present.
        optional: Columns that are validated and typed when present.
        dtypes: Target dtype per column after validation.
        date_columns: Columns parsed as ISO dates.
        week_start_columns: Subset of ``date_columns`` that must be Mondays.
        quantity_columns: Numeric, non-negative columns.
        boolean_columns: Columns that must contain only True/False.
        key: Columns that must be unique together; empty means no rule.
    """

    name: str
    required: tuple[str, ...]
    optional: tuple[str, ...]
    dtypes: Mapping[str, str]
    date_columns: tuple[str, ...]
    week_start_columns: tuple[str, ...]
    quantity_columns: tuple[str, ...]
    boolean_columns: tuple[str, ...] = ()
    key: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "dtypes", MappingProxyType(dict(self.dtypes)))

    @property
    def columns(self) -> tuple[str, ...]:
        """Required columns followed by optional ones, in canonical order."""
        return self.required + self.optional


# Weekly consumption per item. The import file ``consumption.csv`` carries
# ``item_name`` and ``unit`` as well; the forecasting module needs only the
# three required columns. ``is_stock_out`` is supplied by the backend when it
# builds the history from ``stock_snapshot`` (FQ-02).
CONSUMPTION = FrameSchema(
    name="consumption",
    required=(ITEM_CODE, PERIOD_START, QUANTITY),
    optional=(ITEM_NAME, UNIT, IS_STOCK_OUT),
    dtypes={
        ITEM_CODE: STRING,
        PERIOD_START: DATE,
        QUANTITY: FLOAT,
        ITEM_NAME: STRING,
        UNIT: STRING,
        IS_STOCK_OUT: BOOL,
    },
    date_columns=(PERIOD_START,),
    week_start_columns=(PERIOD_START,),
    quantity_columns=(QUANTITY,),
    boolean_columns=(IS_STOCK_OUT,),
    key=(ITEM_CODE, PERIOD_START),
)

# Weekly stock per item: closing balance at the end of the week, after that
# week's receipts and consumption (docs/data/data-specification.md, section 2).
STOCK = FrameSchema(
    name="stock",
    required=(ITEM_CODE, PERIOD_START, QUANTITY_ON_HAND),
    optional=(IS_STOCK_OUT,),
    dtypes={
        ITEM_CODE: STRING,
        PERIOD_START: DATE,
        QUANTITY_ON_HAND: FLOAT,
        IS_STOCK_OUT: BOOL,
    },
    date_columns=(PERIOD_START,),
    week_start_columns=(PERIOD_START,),
    quantity_columns=(QUANTITY_ON_HAND,),
    boolean_columns=(IS_STOCK_OUT,),
    key=(ITEM_CODE, PERIOD_START),
)

# Deliveries. ``received_on`` is a calendar date, not a week start. Several
# deliveries of one item on the same day are legitimate, so there is no
# uniqueness rule.
RECEIPTS = FrameSchema(
    name="receipts",
    required=(ITEM_CODE, RECEIVED_ON, QUANTITY),
    optional=(SUPPLIER,),
    dtypes={
        ITEM_CODE: STRING,
        RECEIVED_ON: DATE,
        QUANTITY: FLOAT,
        SUPPLIER: STRING,
    },
    date_columns=(RECEIVED_ON,),
    week_start_columns=(),
    quantity_columns=(QUANTITY,),
    key=(),
)

SCHEMAS: Mapping[str, FrameSchema] = MappingProxyType(
    {frame.name: frame for frame in (CONSUMPTION, STOCK, RECEIPTS)}
)
