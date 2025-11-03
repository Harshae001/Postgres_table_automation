import json
from schema_utils import build_columns, mandatory_columns, excluded_columns
from db_manager import create_table


def main():
    # Load JSON input
    with open('input.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # ✅ Merge top-level + submitted_data.data
    base = dict(data)
    if 'submitted_data' in base and 'data' in base['submitted_data']:
        base.update(base['submitted_data']['data'])

    # Filter excluded columns
    filtered = {k: v for k, v in base.items() if k not in excluded_columns}

    # Automatically infer schema from JSON
    columns = build_columns(filtered)

    # Derive table name
    table_name = base.get('table_name', 'auto_generated_table')

    # Create table in DB
    create_table(table_name, columns, mandatory_columns)

    print(f"✅ Table '{table_name}' created successfully with {len(columns)} columns.")


if __name__ == '__main__':
    main()
