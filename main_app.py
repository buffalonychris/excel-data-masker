from ui_field_picker import launch_field_picker
from masking_engine import run_processing
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading

def main():
    root = tk.Tk()
    root.title("Excel Data Masker")
    root.geometry("800x600")

    instruction = tk.Label(root, text="Select an Excel file to mask:", font=("Arial", 14))
    instruction.pack(pady=20)

    status_label = tk.Label(root, text="", font=("Arial", 12), wraplength=700, justify="center")
    status_label.pack(pady=20)

    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate', variable=progress_var)
    progress_bar.pack(pady=10)

    def start():
        try:
            filepath = filedialog.askopenfilename(
                title="Select Excel File", filetypes=[("Excel files", "*.xlsx")]
            )
            if not filepath:
                return

            def after_field_selection(selected_cols):
                threading.Thread(
                    target=run_processing,
                    args=(filepath, selected_cols, status_label, progress_var)
                ).start()

            launch_field_picker(filepath, after_field_selection)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

    tk.Button(root, text="Select File and Start", command=start, font=("Arial", 12)).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    main()
