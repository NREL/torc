"""Utility functions for inserting data into a SQLite database"""

import logging
import sqlite3


_TYPE_MAP = {int: "INTEGER", float: "REAL", str: "TEXT", bool: "INTEGER"}
logger = logging.getLogger(__name__)


def make_table(db_file, table, row, primary_key=None, types=None):
    """Create a table in the database based on the types in row.

    Parameters
    ----------
    db_file : Path
        Database file. Create if it doesn't already exist.
    table : str
    row : dict
        Each key will be a column in the table. Define schema by the types of the values.
    primary_key : str | None
        Column name to define as the primary key
    types: dict | None
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
    logger.info("Created table=%s in db_file=%s", table, db_file)


def insert_rows(db_file, table, rows):
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
        logger.debug("Inserted rows into table=%s in db_file=%s", table, db_file)
