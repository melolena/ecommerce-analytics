import re
import sqlite3
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parents[1]


@pytest.fixture
def analytics_db() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript((PROJECT_ROOT / "sql" / "01_create_schema.sql").read_text())
    connection.executemany(
        "INSERT INTO stg_customers VALUES (?, ?, ?, ?, ?)",
        [
            ("c1", "u-repeat", "01000", "sao paulo", "SP"),
            ("c2", "u-repeat", "20000", "rio de janeiro", "RJ"),
            ("c3", "u-missing", "03000", "sao paulo", "SP"),
            ("c4", "u-single", "40000", "salvador", "BA"),
            ("c5", "u-canceled", "50000", "recife", "PE"),
        ],
    )
    connection.executemany(
        "INSERT INTO stg_products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            ("p-en", "categoria_traduzida", 10, 100, 1, 100, 10, 5, 5),
            ("p-pt", "categoria_sem_traducao", 10, 100, 1, 100, 10, 5, 5),
            ("p-null", None, 10, 100, 1, 100, 10, 5, 5),
        ],
    )
    connection.execute(
        "INSERT INTO stg_category_translation VALUES (?, ?)",
        ("categoria_traduzida", "health_beauty"),
    )
    connection.execute(
        "INSERT INTO stg_sellers VALUES (?, ?, ?, ?)",
        ("s1", "01000", "sao paulo", "SP"),
    )
    connection.executemany(
        "INSERT INTO stg_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            ("o1", "c1", "delivered", "2020-01-02 10:00:00", None, None,
             "2020-01-10 10:00:00", "2020-01-10 00:00:00"),
            ("o2", "c2", "delivered", "2020-01-03 10:00:00", None, None,
             "2020-01-11 10:00:00", "2020-01-10 00:00:00"),
            ("o3", "c3", "delivered", "2020-01-04 10:00:00", None, None,
             None, "2020-01-10 00:00:00"),
            ("o4", "c4", "delivered", "2020-01-05 10:00:00", None, None,
             "2020-01-09 10:00:00", "2020-01-10 00:00:00"),
            ("o5", "c5", "canceled", "2020-01-06 10:00:00", None, None,
             "2020-01-09 10:00:00", "2020-01-10 00:00:00"),
        ],
    )
    connection.executemany(
        "INSERT INTO stg_order_items VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            ("o1", 1, "p-en", "s1", None, 10.0, 1.0),
            ("o1", 2, "p-en", "s1", None, 20.0, 2.0),
            ("o1", 3, "p-pt", "s1", None, 5.0, 1.0),
            ("o2", 1, "p-en", "s1", None, 30.0, 3.0),
            ("o3", 1, "p-null", "s1", None, 7.0, 2.0),
            ("o5", 1, "p-en", "s1", None, 100.0, 10.0),
        ],
    )
    connection.executemany(
        "INSERT INTO stg_order_payments VALUES (?, ?, ?, ?, ?)",
        [
            ("o1", 1, "credit_card", 1, 20.0),
            ("o1", 2, "voucher", 1, 16.0),
            ("o2", 1, "credit_card", 1, 33.0),
            ("o3", 1, "boleto", 1, 9.0),
            ("o5", 1, "credit_card", 1, 110.0),
        ],
    )
    connection.executemany(
        """INSERT INTO stg_order_reviews
           (review_id, order_id, review_score, review_comment_title,
            review_comment_message, review_creation_date, review_answer_timestamp)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [
            ("repeated-review-id", "o1", 5, None, None, None, None),
            ("repeated-review-id", "o1", 1, None, None, None, None),
            ("review-late", "o2", 1, None, None, None, None),
            ("review-missing-date", "o3", 5, None, None, None, None),
            ("review-canceled", "o5", 5, None, None, None, None),
        ],
    )
    connection.executescript((PROJECT_ROOT / "sql" / "04_powerbi_views.sql").read_text())
    yield connection
    connection.close()


def _analytics_statements() -> list[str]:
    source = (PROJECT_ROOT / "sql" / "03_delivered_sales_queries.sql").read_text()
    return [
        statement.strip()
        for statement in source.split(";")
        if re.search(r"\b(?:SELECT|WITH)\b", statement, flags=re.IGNORECASE)
    ]


def test_sales_query_counts_orders_once_and_separates_revenue_and_freight(
    analytics_db: sqlite3.Connection,
) -> None:
    row = analytics_db.execute(_analytics_statements()[0]).fetchone()

    assert row == ("2020-01", 4, 72.0, 9.0, 81.0, 20.25)


def test_payment_methods_do_not_change_item_revenue_and_allow_multiple_methods(
    analytics_db: sqlite3.Connection,
) -> None:
    rows = analytics_db.execute(_analytics_statements()[1]).fetchall()

    assert rows == [
        ("credit_card", 2, 2, 53.0),
        ("boleto", 1, 1, 9.0),
        ("voucher", 1, 1, 16.0),
    ]
    # The sales query result remains based on item rows, not payment values.
    sales = analytics_db.execute(_analytics_statements()[0]).fetchone()
    assert sales[2:5] == (72.0, 9.0, 81.0)


def test_delivery_rate_excludes_missing_dates_and_non_delivered_orders(
    analytics_db: sqlite3.Connection,
) -> None:
    row = analytics_db.execute(_analytics_statements()[2]).fetchone()

    assert row == (3, 2, 1, 66.67)
    missing = analytics_db.execute(
        "SELECT COUNT(*) FROM vw_delivered_orders WHERE delivery_outcome = 'Missing dates'"
    ).fetchone()[0]
    assert missing == 1


def test_review_query_averages_within_order_and_ignores_unscored_orders(
    analytics_db: sqlite3.Connection,
) -> None:
    rows = analytics_db.execute(_analytics_statements()[3]).fetchall()

    assert rows == [
        ("late", 1, 1.0, 1),
        ("on_time", 1, 3.0, 2),
    ]
    # Duplicate review_id values remain distinct source records in staging.
    assert analytics_db.execute(
        "SELECT COUNT(*) FROM stg_order_reviews WHERE review_id = 'repeated-review-id'"
    ).fetchone()[0] == 2


def test_repeat_customer_rate_uses_customer_unique_id_and_delivered_orders(
    analytics_db: sqlite3.Connection,
) -> None:
    # Two delivered orders with no identity must not become a synthetic repeat customer.
    analytics_db.execute(
        "INSERT INTO stg_customers VALUES (?, ?, ?, ?, ?)",
        ("c6", None, "60000", "fortaleza", "CE"),
    )
    analytics_db.executemany(
        "INSERT INTO stg_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            ("o6", "c6", "delivered", "2020-02-01 10:00:00", None, None,
             "2020-02-02 10:00:00", "2020-02-03 00:00:00"),
            ("o7", "c6", "delivered", "2020-02-04 10:00:00", None, None,
             "2020-02-05 10:00:00", "2020-02-06 00:00:00"),
        ],
    )

    view_row = analytics_db.execute(
        "SELECT * FROM vw_repeat_customer_summary"
    ).fetchone()
    row = analytics_db.execute(_analytics_statements()[6]).fetchone()

    assert view_row[0:2] == (3, 1)
    assert view_row[2] == pytest.approx(1 / 3)
    assert row == (3, 1, 33.33)


def test_category_query_applies_translation_fallback_and_missing_label(
    analytics_db: sqlite3.Connection,
) -> None:
    rows = analytics_db.execute(_analytics_statements()[4]).fetchall()
    by_category = {row[0]: row[1:] for row in rows}

    assert by_category == {
        "health_beauty": (3, 2, 60.0, 6.0),
        "(missing category)": (1, 1, 7.0, 2.0),
        "categoria_sem_traducao": (1, 1, 5.0, 1.0),
    }


def test_views_preaggregate_items_and_reviews_before_joining(
    analytics_db: sqlite3.Connection,
) -> None:
    row = analytics_db.execute(
        """SELECT order_item_rows, item_revenue, freight_value,
                  mean_review_score, scored_review_records
           FROM vw_delivered_orders WHERE order_id = 'o1'"""
    ).fetchone()

    assert row == (3, 35.0, 4.0, 3.0, 2)
    assert analytics_db.execute(
        "SELECT COUNT(*) FROM vw_delivered_orders"
    ).fetchone()[0] == 4


def test_customer_state_query_uses_buyer_state_without_fanout(
    analytics_db: sqlite3.Connection,
) -> None:
    rows = analytics_db.execute(_analytics_statements()[5]).fetchall()

    assert rows == [
        ("SP", 4, 2, 42.0, 6.0),
        ("RJ", 1, 1, 30.0, 3.0),
    ]
