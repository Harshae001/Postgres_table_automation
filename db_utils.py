import psycopg2
from psycopg2 import pool
from config import DB_CONFIG

# Global connection pool
CONN_POOL = pool.SimpleConnectionPool(1, 10, **DB_CONFIG)

def get_db_connection():
    return CONN_POOL.getconn()

def release_db_connection(conn):
    CONN_POOL.putconn(conn)

def ensure_table_exists(table_name, columns):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT to_regclass(%s)", (table_name,))
    exists = cur.fetchone()[0] is not None

    if not exists:
        columns_sql = ',\n    '.join(columns)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    {columns_sql}\n);"
        cur.execute(sql)
        set_table_permissions(cur, table_name)
    else:
        sync_missing_columns(cur, table_name, columns)

    conn.commit()
    cur.close()
    release_db_connection(conn)

def sync_missing_columns(cur, table_name, columns):
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", (table_name,))
    existing_cols = set(row[0].lower() for row in cur.fetchall())
    for col_def in columns:
        col_name = col_def.split()[0].replace('"', '').lower()
        if col_name not in existing_cols:
            cur.execute(f'ALTER TABLE {table_name} ADD COLUMN {col_def};')

def set_table_permissions(cur, table_name):
    db_user = DB_CONFIG.get('user', 'postgres')
    cur.execute(f"ALTER TABLE IF EXISTS public.{table_name} OWNER TO {db_user};")
    cur.execute(f"GRANT ALL ON TABLE public.{table_name} TO {db_user};")
