from src.data.db import connect_db
from src.data.schema import init_schema


def test_init_schema_creates_candidate_plan_table(tmp_path):
    conn = connect_db(tmp_path / "quant.db")

    init_schema(conn)

    rows = conn.execute(
        "select name from sqlite_master where type='table' and name='candidate_plan'"
    ).fetchall()
    assert rows

