import json
from dateutil.parser import parse as dt_parse

# Columns that should not be auto-created
excluded_columns = [
    'project_id', 'stage_id', 'task_id', 'task_status', 'step_name', 'row_num',
    'inserted_datetime', 'date', 'table_name', 'triggers', 'type', 'submitted_data',
    'data', 'user_id', 'language', 'tz', 'project_type', 'offline', 'stages',
    'current_status', 'sample_size', 'fetch'
]

# Columns that must always exist in every table
mandatory_columns = [
    'project_id VARCHAR(1000) NOT NULL',
    'stage_id VARCHAR(1000) NOT NULL',
    'task_id VARCHAR(1000) NOT NULL',
    'task_status VARCHAR(1000)',
    'step_name VARCHAR(1000)',
    'row_num SERIAL',
    'inserted_datetime TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP',
    'date DATE',
    'data JSONB'
]


def infer_pg_type(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return 'INTEGER'
    if isinstance(value, float):
        str_val = str(value)
        if '.' in str_val:
            scale = len(str_val.split('.')[1])
            return f'NUMERIC(10,{scale})'
        else:
            return 'NUMERIC(10,0)'
    if isinstance(value, str):
        try:
            dt = dt_parse(value)
            if len(value) == 10:
                return 'DATE'
            if " " in value:
                return 'TIMESTAMP WITHOUT TIME ZONE'
            return 'TIME WITHOUT TIME ZONE'
        except Exception:
            return 'VARCHAR(1000)'
    if isinstance(value, (list, dict)):
        return 'JSONB'
    return 'VARCHAR(1000)'


def extract_lists(data):
    """Extract list-type fields that contain dicts."""
    lists = {}
    for k, v in data.items():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            lists[k] = v
    return lists


def is_esign_dict(d):
    """Detect if a dict is an e-signature object."""
    return isinstance(d, dict) and 'signature_id' in d

def flatten_json(data, parent_key='', flat_dict=None):
    if flat_dict is None:
        flat_dict = {}
    if isinstance(data, dict):
        for k, v in data.items():
            flatten_json(v, k, flat_dict)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                flatten_json(item, parent_key, flat_dict)
    else:
        flat_dict[parent_key] = data
    return flat_dict




def build_columns(data_dict, extra_keys=None):
    cols = []
    keys = set(data_dict.keys())
    if extra_keys:
        keys |= set(extra_keys)
    for key in keys:
        if key in excluded_columns:
            continue
        value = data_dict.get(key)
        if is_esign_dict(value):
            cols.append(f'"{key}" JSON')
            cols.append(f'"{key}_name" VARCHAR(1000)')
            cols.append(f'"{key}_date" TIMESTAMP WITHOUT TIME ZONE')
        elif isinstance(value, dict):
            cols.append(f'"{key}" JSON')
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                for sub_key, sub_value in value[0].items():
                    col_type = infer_pg_type(sub_value)
                    if col_type:
                        cols.append(f'"{sub_key}" {col_type}')
            else:
                cols.append(f'"{key}" JSONB')
        else:
            col_type = infer_pg_type(value)
            if col_type:
                cols.append(f'"{key}" {col_type}')
    return cols
