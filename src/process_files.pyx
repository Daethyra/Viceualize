import numpy as np
cimport numpy as cnp
import pandas as pd
from cython cimport boundscheck, wraparound

@boundscheck(False)
@wraparound(False)
def process_rows(cnp.ndarray[object, ndim=2] df_values, str filename):
    cdef:
        Py_ssize_t i, j, num_rows = df_values.shape[0]
        int num_date_errors = 0, invalid_cells, sum_val
        object date_str, cell
        dict data_dict = {}
        list invalid_cells_log = []
        list duplicate_dates_log = []
    
    for i in range(num_rows):
        excel_row = i + 2  # Match original row numbering
        date_str = df_values[i, 0]
        sum_val = 0
        invalid_cells = 0

        # Date processing
        try:
            date = pd.to_datetime(date_str)
        except Exception as e:
            num_date_errors += 1
            continue

        # Sum columns B-E
        for j in range(1, 5):
            cell = df_values[i, j]
            try:
                sum_val += int(cell)
            except (ValueError, TypeError):
                invalid_cells += 1

        # Log warnings
        if invalid_cells > 0:
            invalid_cells_log.append( (excel_row, invalid_cells) )
        
        if date in data_dict:
            duplicate_dates_log.append((excel_row, str(date)))
        
        data_dict[date] = sum_val

    return {
        'data_dict': data_dict,
        'num_date_errors': num_date_errors,
        'invalid_cells': invalid_cells_log,
        'duplicate_dates': duplicate_dates_log,
        'total_rows': num_rows
    }