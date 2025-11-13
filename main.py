# import json
# from schema_utils import build_columns, mandatory_columns, excluded_columns
# from db_manager import create_table
#
#
# def main():
#     # Load JSON input
#     with open('input.json', 'r', encoding='utf-8') as f:
#         data = json.load(f)
#
#     # ✅ Merge top-level + submitted_data.data
#     base = dict(data)
#     if 'submitted_data' in base and 'data' in base['submitted_data']:
#         base.update(base['submitted_data']['data'])
#
#     # Filter excluded columns
#     filtered = {k: v for k, v in base.items() if k not in excluded_columns}
#
#     # Automatically infer schema from JSON
#     columns = build_columns(filtered)
#
#     # Derive table name
#     table_name = base.get('table_name', 'auto_generated_table')
#
#     # Create table in DB
#     create_table(table_name, columns, mandatory_columns)
#
#     print(f"✅ Table '{table_name}' created successfully with {len(columns)} columns.")
#
#
# if __name__ == '__main__':
#     main()


import json
from schema_utils import build_columns, extract_lists, mandatory_columns, excluded_columns
from db_manager import create_table

def main():
    with open('input.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Flatten: get main data dict
    base = dict(data)
    if 'submitted_data' in base and 'data' in base['submitted_data']:
        base.update(base['submitted_data']['data'])

    # Extract datagrids (list of dicts)
    datagrids = extract_lists(base)

    # Identify non-list (common) keys
    common_data = {k: v for k, v in base.items() if k not in datagrids and k not in excluded_columns}

    # Base table name
    base_table_name = base.get('table_name', 'auto_generated_table')

    # Case 1: Datagrids exist
    if datagrids:
        for dg_name, dg_data in datagrids.items():
            if not dg_data or not isinstance(dg_data[0], dict):
                continue

            # Table name = base_table_datagrid
            table_name = f"{base_table_name}_{dg_name}"

            # Combine common + datagrid keys
            first_row = dg_data[0]
            combined_data = {**common_data, **first_row}

            # Build columns
            columns = build_columns(combined_data)

            # Create table
            create_table(table_name, columns, mandatory_columns)
            print(f"Created/updated table: {table_name}")

    # Case 2: No datagrids — single table
    else:
        table_name = base_table_name
        columns = build_columns(common_data)
        create_table(table_name, columns, mandatory_columns)
        print(f"Created/updated single table: {table_name}")


if __name__ == '__main__':
    main()
