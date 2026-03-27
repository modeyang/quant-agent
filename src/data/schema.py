from __future__ import annotations

import sqlite3


SCHEMA_SQL = """
create table if not exists candidate_plan (
    id integer primary key autoincrement,
    run_id text not null,
    symbol text not null,
    asset_type text not null,
    score real not null,
    status text not null default 'planned',
    created_at text not null default current_timestamp,
    unique(run_id, symbol)
);
"""


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()
