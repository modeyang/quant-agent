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

create table if not exists run_log (
    id integer primary key autoincrement,
    run_id text not null unique,
    mode text not null,
    status text not null,
    message text,
    started_at text not null default current_timestamp,
    finished_at text
);

create table if not exists orders (
    id integer primary key autoincrement,
    run_id text not null,
    order_id text not null unique,
    symbol text not null,
    side text not null,
    quantity integer not null,
    price real,
    status text not null,
    created_at text not null default current_timestamp
);

create table if not exists fills (
    id integer primary key autoincrement,
    run_id text not null,
    fill_id text not null unique,
    order_id text not null,
    symbol text not null,
    quantity integer not null,
    price real not null,
    filled_at text not null
);

create table if not exists account_snapshot (
    id integer primary key autoincrement,
    run_id text not null,
    cash real not null,
    total_asset real not null,
    position_value real not null,
    snapshot_at text not null default current_timestamp
);

create table if not exists memory_entry (
    id integer primary key autoincrement,
    run_id text not null,
    memory_type text not null,
    symbol text,
    title text not null,
    content text not null,
    score real not null,
    status text not null,
    created_at text not null default current_timestamp
);
"""


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()
