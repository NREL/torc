import logging
import sqlite3


logger = logging.getLogger(__name__)


def make_table(db_file, table, row, primary_key=None):
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

    """
    schema = []
    type_map = {int: "INTEGER", float: "REAL", str: "TEXT"}
    for name, val in row.items():
        column_type = type_map.get(type(val), "TEXT")
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
    con = sqlite3.connect(db_file)
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
    logger.info("Inserted rows into table=%s in db_file=%s", table, db_file)
