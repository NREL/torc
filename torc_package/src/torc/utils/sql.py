"""Utility functions for inserting data into a SQLite database"""

import shutil
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional

from loguru import logger


_TYPE_MAP = {int: "INTEGER", float: "REAL", str: "TEXT", bool: "INTEGER"}


def make_table(
    db_file: Path,
    table: str,
    row: dict[str, Any],
    primary_key: Optional[str] = None,
    types: Optional[dict[str, Any]] = None,
):
    """Create a table in the database based on the types in row.

    Parameters
    ----------
    db_file
        Database file. Create if it doesn't already exist.
    table
    row
        Each key will be a column in the table. Define schema by the types of the values.
    primary_key
        Column name to define as the primary key
    types
        If a dict is passed, use it as a mapping of column to type.
        This is required if values can be null.
    """
    schema = []
    for name, val in row.items():
        if types is None:
            column_type = _TYPE_MAP[type(val)]
        else:
            column_type = _TYPE_MAP[types[name]]
        entry = f"{name} {column_type}"
        if name == primary_key:
            entry += " PRIMARY KEY"
        schema.append(entry)

    con = sqlite3.connect(db_file)
    cur = con.cursor()
    schema_text = ", ".join(schema)
    cur.execute(f"CREATE TABLE {table}({schema_text})")
    con.commit()
    logger.trace("Created table={} in db_file={}", table, db_file)


def insert_rows(db_file: Path, table: str, rows: list[tuple]) -> None:
    """Insert a list of rows into the database table.

    Parameters
    ----------
    db_file : Path
    table : str
    rows : list[tuple]
        Each row should be a tuple of values.
    """
    with sqlite3.connect(db_file) as con:
        cur = con.cursor()
        placeholder = ""
        num_columns = len(rows[0])
        for i in range(num_columns):
            if i == num_columns - 1:
                placeholder += "?"
            else:
                placeholder += "?, "
        query = f"INSERT INTO {table} VALUES({placeholder})"
        cur.executemany(query, rows)
        con.commit()
        logger.trace("Inserted rows into table={} in db_file={}", table, db_file)


def union_tables(dst_db_file: Path, src_db_file: Path, tables: Optional[list[str]] = None) -> None:
    """Write all rows from src_db_file to the end of dst_db_file. Single read, single write,
    no batching. If dst_db_file doesn't exist, copy src to dst.

    Parameters
    ----------
    dst_db_file : Path
    src_db_file : Path
    tables : None | list
        If a list, union these tables. Otherwise, perform a union on all tables.
    """
    if not dst_db_file.exists() and not tables:
        shutil.copyfile(src_db_file, dst_db_file)
        return

    with sqlite3.connect(src_db_file) as con_src:
        cur_src = con_src.cursor()
        _tables: Iterable[str] = tables or cur_src.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        for table in _tables:
            if not _does_table_exist(cur_src, table):
                continue
            rows = cur_src.execute(f"SELECT * FROM {table}").fetchall()
            with sqlite3.connect(dst_db_file) as con_dst:
                cur_dst = con_dst.cursor()
                if not _does_table_exist(cur_dst, table):
                    cmd = f"select sql from sqlite_master where type = 'table' and name='{table}'"
                    create_query = cur_src.execute(cmd).fetchall()[0][0]
                    cur_dst.execute(create_query)
                    con_dst.commit()
                if rows:
                    insert_rows(dst_db_file, table, rows)
            logger.info("Added table {} from {} to {}", table, src_db_file, dst_db_file)


def _does_table_exist(cur, table):
    query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
    result = cur.execute(query).fetchone()
    return bool(result)
