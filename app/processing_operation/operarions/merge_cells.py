def merge_cells_in_column(table, col_key, row_idx1, row_idx2):
    rows = table.columns_content
    hi = max(row_idx1, row_idx2)
    lo = min(row_idx1, row_idx2)
    # Step 1: Merge hi into lo
    cell_lo = rows[lo].get(col_key, {})
    cell_hi = rows[hi].get(col_key, {})
    display_lo = cell_lo.get("display", "")
    display_hi = cell_hi.get("display", "")
    meta_lo = cell_lo.get("meta", "")
    meta_hi = cell_hi.get("meta", "")
    merged_display = display_lo if display_lo == display_hi else f"{display_lo} , {display_hi}" if display_lo and display_hi else display_lo or display_hi
    merged_meta = ", ".join(filter(None, set(str(meta_lo).split(",") + str(meta_hi).split(","))))
    rows[lo][col_key] = {"display": merged_display, "meta": merged_meta}
    rows[hi][col_key] = {"display": "", "meta": None}  # Clear hi cell
    # Step 2: Shift up all following values until next file row (non-empty col0)
    # Find the next file row after hi
    end = hi
    for i in range(hi + 1, len(rows)):
        col0_val = rows[i].get("col0", "")
        if col0_val and ((isinstance(col0_val, dict) and col0_val.get("display", "") != '') or (isinstance(col0_val, str) and col0_val != '')):
            end = i - 1
            break
        else:
            end = i
    # Shift up values from hi+1 to end (not including end)
    for i in range(hi, end):
        next_cell = rows[i + 1].get(col_key, {})
        rows[i][col_key] = {"display": next_cell.get("display", ""), "meta": next_cell.get("meta", "")}
    # Clear the last included row
    if end > hi:
        rows[end][col_key] = {"display": "", "meta": None}
    return table
