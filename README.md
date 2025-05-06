# Excel Data Masker

A local Python application for masking sensitive data in Excel spreadsheets using a visual UI grid.  
Designed to help users anonymize data fields for compliance, testing, or sharing purposes without exposing internal formats or IP.

## ✨ Features

- Fuzzy logic to auto-suggest fields for masking
- Spreadsheet-style interface using tksheet
- Manual field selection and live editing
- Supports full, partial, or replacement masking
- Preview masking results in Excel before applying

## 🔧 Requirements

- Python 3.12
- Pandas 2.2.0
- OpenPyXL 3.1.2
- Tksheet 7.4.18
- Pillow 11.1.0
- NumPy 1.26.4

Install dependencies with:

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
python main_app.py
```

## 📁 File Structure

```
excel-data-masker/
├── main_app.py
├── ui_field_selector_grid.py
├── mask_logic.py
├── requirements.txt
├── README.md
├── LICENSE
└── sample_data/
    └── example_input.xlsx (optional)
```

## 🧪 Sample Use Case

- Load an Excel file with PII columns
- Review the suggested fields to mask
- Confirm masking type (e.g., Full, Partial, Replace)
- Click 'Preview' to generate a masked version for review
- Submit for actual masking

## 📷 Screenshots

(Insert screenshots here if available)

## 📜 License

MIT © 2025 Christian A. Brzostowicz

## 🧑‍💻 Author

Created and Compiled By: **Christian A. Brzostowicz**  
Contact: BuffaloNYChris@GMail.com
