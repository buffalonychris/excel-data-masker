import os
import pandas as pd
from datetime import datetime

# ✅ Files to process
files_to_process = [
    r"C:\Users\Chris\Downloads\SPMCGC Patient AR Balances 4.2.25 (1).xlsx",
    r"C:\Users\Chris\Downloads\SPMCGC Patient AR Balances 4.2.25_Grouped.xlsx",
    r"C:\Users\Chris\Downloads\SPMCGC Patient AR Balances 4.7.25.xlsx",
    r"C:\Users\Chris\Downloads\SPMCGC Patient AR Balances 4.7.25_Grouped.xlsx"
]

# ✅ Keywords to trigger masking (lowercased, fuzzy matched)
MASK_KEYWORDS = [
    "account",
    "phone",
    "ssn",
    "address",
    "name",
    "last name",
    "employer",
    "contact",
    "primary insurance",
    "primary insurance policy number",
    "secondary insurance",
    "secondary insurance policy number"
]

# ✅ Apply masking to matching columns
def apply_mask(df):
    matched_columns = []

    for col in df.columns:
        col_clean = col.strip().lower()
        if any(keyword in col_clean for keyword in MASK_KEYWORDS):
            df[col] = df[col].apply(lambda x: "AVAILABLE" if pd.notnull(x) else x)
            matched_columns.append(col)

    if not matched_columns:
        print("⚠️  No matching columns found for masking.")
    else:
        print(f"✅ Masked columns: {', '.join(matched_columns)}")

    return df

# ✅ Process each file
for file_path in files_to_process:
    print(f"\n🔄 Processing: {file_path}")
    try:
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        masked_sheets = {}

        for sheet in xls.sheet_names:
            print(f"   📄 Sheet: {sheet}")
            df = pd.read_excel(xls, sheet_name=sheet)
            masked_sheets[sheet] = apply_mask(df)

        # Save result
        output_dir = os.path.join(os.path.dirname(file_path), "Masked")
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = os.path.basename(file_path)
        out_path = os.path.join(output_dir, f"{os.path.splitext(base)[0]}_masked_{timestamp}.xlsx")

        with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
            for sheet_name, df in masked_sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"✅ Saved masked file to:\n   {out_path}")

    except Exception as e:
        print(f"❌ Failed: {file_path}")
        print(str(e))
