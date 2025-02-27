#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module: viceualize.py
Description: Process .ods and .xlsx files and create an interactive Plotly figure with zoom/scroll functionality
Author: Daethyra Carino
Date: 2025-02-23
Version: 0.1.2
License: MIT
"""

import glob
import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go

from src.process_files import process_rows # type: ignore


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

        # Convert to numpy array for Cython processing
        df_values = df.values
        
        # Process rows using Cython/pure Python implementation
        results = process_rows(df_values, filename)
        
        # Unpack results
        data_dict = results['data_dict']
        num_date_errors = results['num_date_errors']
        invalid_cells_log = results['invalid_cells']
        duplicate_dates_log = results['duplicate_dates']
        num_rows = results['total_rows']

        # Print accumulated warnings
        for row, count in invalid_cells_log:
            print(f"Warning: {count} non-integer value(s) in columns B-E of row {row} in {filename}. Treated as 0.")
            
        for row, date_str in duplicate_dates_log:
            print(f"Warning: Duplicate date {date_str} in row {row} of {filename}. Overwriting previous entry.")

        valid_rows = num_rows - num_date_errors
        print(f"Processed {valid_rows} valid rows from {filename} with {num_date_errors} date errors.")
        
        head_dict[filename] = data_dict

    return head_dict


def plot_data(head_dict):
    """Create an interactive Plotly figure with zoom/scroll functionality and color segments by month."""
    if not head_dict:
        print("No data available to plot.")
        return

    fig = go.Figure()

    # Define a dictionary mapping month (1-12) to specific colors
    month_to_color = {
        1: 'cyan',
        2: 'hotpink',
        3: 'mediumspringgreen',
        4: 'blue',
        5: 'darkorchid',
        6: 'darksalmon',
        7: 'peru',
        8: 'indianred',
        9: 'coral',
        10: 'orange',
        11: 'goldenrod',
        12: 'green'
    }

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

        # Group data into segments where the month is continuous
        current_month = None
        segment_dates = []
        segment_sums = []
        for date, sum_val in zip(sorted_dates, sorted_sums):
            month = date.month
            if current_month is None:
                current_month = month
            if month != current_month:
                # Plot the current segment
                fig.add_trace(
                    go.Scatter(
                        x=segment_dates,
                        y=segment_sums,
                        mode="lines+markers",
                        name=f"{filename} - {current_month:02d}",
                        line=dict(color=month_to_color.get(current_month, 'black')),
                        hovertemplate=f"Date: %{{x|%Y-%m-%d}}<br>Sum: %{{y}}<br>Month: {current_month:02d}<extra></extra>"
                    )
                )
                # Reset segment for new month
                segment_dates = []
                segment_sums = []
                current_month = month
            segment_dates.append(date)
            segment_sums.append(sum_val)
        # Plot the final segment
        if segment_dates:
            fig.add_trace(
                go.Scatter(
                    x=segment_dates,
                    y=segment_sums,
                    mode="lines+markers",
                    name=f"{filename} - {current_month:02d}",
                    line=dict(color=month_to_color.get(current_month, 'black')),
                    hovertemplate=f"Date: %{{x|%Y-%m-%d}}<br>Sum: %{{y}}<br>Month: {current_month:02d}<extra></extra>"
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
