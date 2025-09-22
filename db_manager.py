import psycopg2
from psycopg2 import pool
from config import DB_CONFIG

CONN_POOL = pool.SimpleConnectionPool(1, 10, **DB_CONFIG)

def get_db_connection():
    return CONN_POOL.getconn()

def release_db_connection(conn):
    CONN_POOL.putconn(conn)

def create_table(table_name, columns, mandatory_columns):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT to_regclass('{table_name}')")
    exists = cur.fetchone()[0] is not None
    if not exists:
        columns_sql = ',\n    '.join(mandatory_columns + columns)
        sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {columns_sql}
        );
        """
        cur.execute(sql)
    else:
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = %s", (table_name,))
        existing_cols = set(row[0].lower() for row in cur.fetchall())
        for col_def in columns:
            col_name = col_def.split()[0].replace('"', '').lower()
            if col_name not in existing_cols:
                alter_sql = f'ALTER TABLE {table_name} ADD COLUMN {col_def};'
                cur.execute(alter_sql)
    conn.commit()
    cur.close()
    release_db_connection(conn)