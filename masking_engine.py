import pandas as pd
import os
import re
from datetime import datetime
import time
from tkinter import messagebox

ALWAYS_MASK_KEYWORDS = [
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

def normalize(col):
    return ''.join(col.lower().split()).replace("_", "").replace("-", "")

def get_mask_type(col_name):
    norm = normalize(col_name)

    if "ssn" in norm or "socialsecurity" in norm:
        return lambda x: re.sub(r'\d', '*', str(x)) if pd.notnull(x) else x
    elif "name" in norm:
        return lambda x: x[0] + "*"*(len(x)-2) + x[-1] if isinstance(x, str) and len(x) > 2 else x
    elif "address" in norm:
        return lambda x: "Address_Hidden" if pd.notnull(x) else x
    elif "account" in norm:
        return lambda x: f"acct_{abs(hash(x))%100000}" if pd.notnull(x) else x
    elif "phone" in norm or "employer" in norm or "insurance" in norm or "contact" in norm or "policy" in norm:
        return lambda x: "AVAILABLE" if pd.notnull(x) else x
    else:
        return lambda x: "AVAILABLE" if pd.notnull(x) else x

def apply_selected_mask(df, selected_columns):
    masked_columns = []

    for col in df.columns:
        if col in selected_columns:
            mask_func = get_mask_type(col)
            df[col] = df[col].apply(mask_func)
            masked_columns.append(col)

    if not masked_columns:
        print("⚠️  No selected columns were masked.")
    else:
        print(f"✅ Masked columns: {', '.join(masked_columns)}")

    return df

def run_processing(filepath, columns_to_mask, status_label, progress_var):
    """Process the Excel file in a worker thread and update the UI safely."""
    try:
        xls = pd.ExcelFile(filepath, engine='openpyxl')
        masked_sheets = {}
        total = len(xls.sheet_names)

        for i, sheet in enumerate(xls.sheet_names):
            # Schedule UI update on the main thread
            status_label.after(0, lambda s=sheet: status_label.config(text=f"Processing sheet: {s}"))

            df = pd.read_excel(xls, sheet_name=sheet)
            df_masked = apply_selected_mask(df, columns_to_mask)
            masked_sheets[sheet] = df_masked

            percent = int((i + 1) / total * 100)
            status_label.after(0, lambda p=percent: progress_var.set(p))
            time.sleep(0.1)

        out_dir = os.path.join(os.path.dirname(filepath), "Masked")
        os.makedirs(out_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = os.path.basename(filepath)
        out_path = os.path.join(out_dir, f"{os.path.splitext(base)[0]}_masked_{timestamp}.xlsx")

        with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
            for sheet_name, df in masked_sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        status_label.after(0, lambda p=out_path: status_label.config(text=f"Done! Saved to:\n{p}"))
        status_label.after(0, lambda p=out_path: messagebox.showinfo("Done", f"Masked file saved to:\n{p}"))

    except Exception as e:
        status_label.after(0, lambda msg=str(e): messagebox.showerror("Error", f"An error occurred:\n{msg}"))
