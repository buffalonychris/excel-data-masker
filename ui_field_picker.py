import os
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import json
from masking_engine import get_mask_type, normalize

SESSION_FILE = "last_session.json"

SUGGEST_MASK_KEYWORDS = [
    "ssn", "socialsecurity", "name", "lastname", "completename",
    "phone", "originalaccount", "accountnumber", "routing", "address", "address1", "address2",
    "primaryinsurance", "primaryinsurancepolicynumber",
    "secondaryinsurance", "secondaryinsurancepolicynumber",
    "employer", "contact", "policy"
]

NEVER_MASK_KEYWORDS = [
    "balance", "principal", "interest", "amountpaid", "datepaid", "date",
    "age", "score", "productname", "accounttype"
]

def suggest_fields(columns):
    suggested = []
    for col in columns:
        norm = normalize(col)
        if any(skip in norm for skip in NEVER_MASK_KEYWORDS):
            continue
        if any(tag in norm for tag in SUGGEST_MASK_KEYWORDS):
            suggested.append(col)
    return suggested

def launch_field_picker(filepath, on_submit_callback):
    xls = pd.ExcelFile(filepath, engine='openpyxl')
    first_sheet = xls.sheet_names[0]
    df = pd.read_excel(xls, sheet_name=first_sheet)
    columns = list(df.columns)

    saved_fields = []
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                saved_fields = json.load(f)
        except:
            saved_fields = []

    suggested_fields = suggest_fields(columns)

    window = tk.Tk()
    window.title("Select Columns to Mask")
    window.geometry("800x600")
    window.resizable(True, True)

    # Place window on left screen (multi-monitor aware)
    try:
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window.geometry(f"800x600+0+{int((screen_height-600)/2)}")
    except:
        pass  # fallback if multi-monitor placement fails

    # Create scrollable canvas if needed
    canvas = tk.Canvas(window)
    scrollbar_y = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
    scrollbar_x = tk.Scrollbar(window, orient="horizontal", command=canvas.xview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x.pack(side="bottom", fill="x")

    var_dict = {}

    for idx, col in enumerate(columns):
        preselect = col in saved_fields or col in suggested_fields
        var = tk.BooleanVar(value=preselect)
        cb = tk.Checkbutton(scrollable_frame, text=col, variable=var)
        cb.grid(row=idx, column=0, sticky='w')
        var_dict[col] = var

    def open_preview(selected_cols, title="Masked Preview (First 10 Rows)"):
        preview_df = df.copy()
        for col in selected_cols:
            mask_func = get_mask_type(col)
            preview_df[col] = preview_df[col].apply(mask_func)

        top = tk.Toplevel(window)
        top.title(title)
        top.geometry("800x600")
        top.resizable(True, True)

        # Try to place on right screen if available
        try:
            screen_width = top.winfo_screenwidth()
            screen_height = top.winfo_screenheight()
            top.geometry(f"800x600+{screen_width - 800}+{int((screen_height-600)/2)}")
        except:
            pass

        text = tk.Text(top, wrap="none")
        scrollbar_v = tk.Scrollbar(top, orient="vertical", command=text.yview)
        scrollbar_h = tk.Scrollbar(top, orient="horizontal", command=text.xview)
        text.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

        text.insert("end", preview_df.head(10).to_string(index=False))
        text.pack(side="left", fill="both", expand=True)
        scrollbar_v.pack(side="right", fill="y")
        scrollbar_h.pack(side="bottom", fill="x")

    def manual_preview():
        selected_cols = [col for col in columns if var_dict[col].get()]
        if not selected_cols:
            messagebox.showinfo("Preview", "No fields selected.")
            return
        open_preview(selected_cols)

    def submit():
        selected = [col for col in columns if var_dict[col].get()]
        if not selected:
            messagebox.showinfo("Info", "No columns selected for masking.")
            return
        with open(SESSION_FILE, "w") as f:
            json.dump(selected, f)
        window.destroy()
        on_submit_callback(selected)

    tk.Button(scrollable_frame, text="Preview", command=manual_preview).grid(row=len(columns)+1, column=0, pady=10)
    tk.Button(scrollable_frame, text="Submit", command=submit).grid(row=len(columns)+1, column=1, pady=10)

    # Automatically show preview of suggested fields
    window.after(500, lambda: open_preview(suggested_fields, title="Auto Preview (Suggested Masked Fields)"))

    window.mainloop()
