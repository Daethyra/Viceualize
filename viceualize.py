#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module: viceualize.py
Description: Process .ods and .xlsx files and create an interactive Plotly figure with zoom/scroll functionality
Author: Daethyra Carino
Date: 2025-02-23
Version: 0.1.1
License: MIT
"""

import glob
import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go


def process_files(directory="."):
    """Process all .ods and .xlsx files in the specified directory and return a dictionary of data."""
    head_dict = {}
    file_list = []
    for ext in ["*.ods", "*.xlsx"]:
        file_list.extend(glob.glob(os.path.join(directory, ext)))

    if not file_list:
        print("No .ods or .xlsx files found in the directory.")
        return head_dict

    for file_path in file_list:
        filename = os.path.basename(file_path)
        print(f"\nProcessing file: {filename}")

        # Determine the appropriate engine for reading the file
        if file_path.endswith(".ods"):
            engine = "odf"
        else:
            engine = "openpyxl"

        try:
            df = pd.read_excel(file_path, engine=engine, skiprows=1, header=None)
        except Exception as e:
            print(f"Error reading {filename}: {str(e)}")
            continue

        data_dict = {}
        num_rows = 0
        num_date_errors = 0

        for idx, row in df.iterrows():
            num_rows += 1
            excel_row = idx + 2  # Adjusting for 0-based index and skipped header row

            # Process date from column A (index 0)
            date_str = row[0]
            try:
                date = pd.to_datetime(date_str)
            except Exception as e:
                print(
                    f"Invalid date '{date_str}' in row {excel_row} of {filename}. Skipping row. Error: {str(e)}"
                )
                num_date_errors += 1
                continue

            # Process sum of columns B-E (indices 1 to 4)
            sum_val = 0
            invalid_cells = 0
            for cell in row.iloc[1:5]:
                try:
                    sum_val += int(cell)
                except (ValueError, TypeError):
                    sum_val += 0
                    invalid_cells += 1

            if invalid_cells > 0:
                print(
                    f"Warning: {invalid_cells} non-integer value(s) in columns B-E of row {excel_row} in {filename}. Treated as 0."
                )

            # Check for duplicate dates and warn
            if date in data_dict:
                print(
                    f"Warning: Duplicate date {date} in row {excel_row} of {filename}. Overwriting previous entry."
                )
            data_dict[date] = sum_val

        valid_rows = num_rows - num_date_errors
        print(
            f"Processed {valid_rows} valid rows from {filename} with {num_date_errors} date errors."
        )
        head_dict[filename] = data_dict

    return head_dict


def plot_data(head_dict):
    """Create an interactive Plotly figure with zoom/scroll functionality"""
    if not head_dict:
        print("No data available to plot.")
        return

    fig = go.Figure()

    # Create sorted list of files based on their earliest date
    sorted_files = sorted(
        [(fn, data) for fn, data in head_dict.items() if data],
        key=lambda x: min(x[1].keys()),  # Sort by earliest date
        # or sort by latest date: key=lambda x: max(x[1].keys())
    )

    for filename, data_dict in sorted_files:
        if not data_dict:
            print(f"Skipping {filename} as it contains no valid data.")
            continue

        # Sort data by date
        sorted_dates = sorted(data_dict.keys())
        sorted_sums = [data_dict[date] for date in sorted_dates]

        fig.add_trace(
            go.Scatter(
                x=sorted_dates,
                y=sorted_sums,
                mode="lines+markers",
                name=filename,
                hovertemplate="Date: %{x|%Y-%m-%d}<br>Sum: %{y}<extra></extra>",
            )
        )

    # Configure layout with time slider and zoom tools
    fig.update_layout(
        title="Cannabis-Use Statistics",
        xaxis=dict(
            title="Date",
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
            rangeslider=dict(visible=True),
            type="date",
        ),
        yaxis=dict(title="Total Hits Per Day"),
        hovermode="x unified",
        height=600,
        template="plotly_white",
    )

    # Add a helpful annotation about controls
    fig.add_annotation(
        text="Use the slider below to zoom, or select 'Pan' in the top right corner to drag to pan | Double-click to reset",
        xref="paper",
        yref="paper",
        x=0.5,
        y=-0.3,
        showarrow=False,
        font=dict(size=12, color="#666"),
    )

    fig.show()
    fig.write_html(
        f"assets/Cannabis-Use-Statistics-{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    )  # Create backup
    fig.write_html("assets/index.html")  # Export main page


if __name__ == "__main__":
    directory = input("Enter the directory path: ")  # Set to the target directory path
    data = process_files(directory)
    plot_data(data)
