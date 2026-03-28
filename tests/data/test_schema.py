from src.data.db import connect_db
from src.data.schema import init_schema


def test_init_schema_creates_candidate_plan_table(tmp_path):
    conn = connect_db(tmp_path / "quant.db")

    init_schema(conn)

    rows = conn.execute(
        "select name from sqlite_master where type='table' and name='candidate_plan'"
    ).fetchall()
    assert rows


def test_init_schema_creates_execution_and_run_tables(tmp_path):
    conn = connect_db(tmp_path / "quant.db")

    init_schema(conn)

    table_names = {
        row["name"]
        for row in conn.execute(
            """
            select name
            from sqlite_master
            where type='table'
              and name in (
                'run_log',
                'orders',
                'fills',
                'account_snapshot',
                'memory_entry',
                'run_stage_event'
              )
            """
        ).fetchall()
    }
    assert table_names == {
        "run_log",
        "orders",
        "fills",
        "account_snapshot",
        "memory_entry",
        "run_stage_event",
    }
