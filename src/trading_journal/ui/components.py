"""
UI component builders
"""
import tkinter as tk
from tkinter import ttk


def create_table_frame(parent, columns: tuple, column_widths: dict):
    """
    Create a table frame with treeview and scrollbars
    
    Args:
        parent: Parent widget
        columns: Tuple of column names
        column_widths: Dictionary mapping column names to widths
        
    Returns:
        Tuple of (table_frame, tree)
    """
    table_frame = ttk.Frame(parent)
    table_frame.columnconfigure(0, weight=1)
    table_frame.rowconfigure(0, weight=1)
    
    # Create scrollbars
    scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
    scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
    
    # Create treeview
    tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                       yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    
    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)
    
    # Configure columns
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=column_widths.get(col, 100), anchor=tk.CENTER)
    
    # Grid widgets
    tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
    scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    return table_frame, tree
