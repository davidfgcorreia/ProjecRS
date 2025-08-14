def merge_columns(table, col1, col2):
    """
    Merge two columns in the table for a given query_id and return the updated table.
    - Merges header titles: header1 / header2
    - Merges cell values: value1 , value2
    - Merges metadata: meta1, meta2
    """
    # Find column indexes for col1 and col2 based on content keys
    content_keys = list(table.columns_content[0].keys())
    try:
        idx1 = content_keys.index(col1)
        idx2 = content_keys.index(col2)
    except ValueError:
        raise Exception(f"Column key not found: {col1} or {col2}")
    # For headers, use idx1-1 and idx2-1 (headers are one up)
    header_idx1 = idx1 - 1 if idx1 > 0 else 0
    header_idx2 = idx2 - 1 if idx2 > 0 else 0
    merged_header = f"{table.row_ids[header_idx1]} / {table.row_ids[header_idx2]}"
    table.row_ids[header_idx1] = merged_header
    table.row_ids.pop(header_idx2)
    # Merge cell values and metadata
    for row in table.columns_content:
        val1 = row.get(col1)
        val2 = row.get(col2)
        meta1 = val1.get("meta") if isinstance(val1, dict) else None
        meta2 = val2.get("meta") if isinstance(val2, dict) else None
        display1 = val1.get("display") if isinstance(val1, dict) else str(val1)
        display2 = val2.get("display") if isinstance(val2, dict) else str(val2)
        merged_display = f"{display1} , {display2}".strip()
        merged_meta = f"{meta1}, {meta2}" if meta1 or meta2 else None
        row[col1] = {"display": merged_display, "meta": merged_meta}
        row.pop(col2, None)
    # After removing col2, also update col keys in each row if needed
    # (optional: reindex col keys to match new row_ids)
    return table
