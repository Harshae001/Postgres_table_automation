# main.py
import json
from schema_utils import build_columns, extract_lists, mandatory_columns, excluded_columns
from db_manager import create_table

def main():
    with open('input.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Flatten to top-level + submitted_data.data
    base = dict(data)
    if 'submitted_data' in base and 'data' in base['submitted_data']:
        base.update(base['submitted_data']['data'])

    lists = extract_lists(base)
    non_list_keys = {k: v for k, v in base.items() if k not in lists and k not in excluded_columns}

    if lists:
        for list_key, list_val in lists.items():
            table_name = f"{base.get('table_name', 'auto_generated_table')}_{list_key}"
            # Use non-list keys + keys from first element of the list
            list_keys = list_val[0].keys()
            columns = build_columns(non_list_keys, extra_keys=list_keys)
            create_table(table_name, columns, mandatory_columns)
    else:
        table_name = base.get('table_name', 'auto_generated_table')
        columns = build_columns(non_list_keys)
        create_table(table_name, columns, mandatory_columns)

if __name__ == '__main__':
    main()