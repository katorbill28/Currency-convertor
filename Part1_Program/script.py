"""Prototype INR to USD expense converter with a simple interface."""

import argparse
import tkinter as tk
from tkinter import ttk


INR_TO_USD_RATE = 95.24
DEFAULT_EXPENSES_INR = [250, 799, 1250.50, 3499, 10200]


def convert_inr_to_usd(amount_inr, rate=INR_TO_USD_RATE):
    """Convert one INR amount to USD."""
    try:
        amount = float(amount_inr)
    except (TypeError, ValueError) as exc:
        raise ValueError("Amount must be a valid number.") from exc

    if amount < 0:
        raise ValueError("Amount cannot be negative.")

    return amount / rate


def convert_expenses(expenses_inr, rate=INR_TO_USD_RATE):
    """Convert a list of INR expenses to USD."""
    return [(amount, convert_inr_to_usd(amount, rate)) for amount in expenses_inr]


class ExpenseConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("INR to USD Expense Converter")
        self.root.geometry("520x430")
        self.root.minsize(460, 390)

        self.amount_var = tk.StringVar()
        self.result_var = tk.StringVar(value="Enter an INR amount or use the sample expenses.")
        self.total_var = tk.StringVar()
        self.expenses = list(DEFAULT_EXPENSES_INR)

        self._build_widgets()
        self._refresh_table()

    def _build_widgets(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)

        title = ttk.Label(
            main_frame,
            text="INR to USD Expense Converter",
            font=("Segoe UI", 18, "bold"),
        )
        title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 14))

        rate_label = ttk.Label(main_frame, text=f"Exchange rate: 1 USD = {INR_TO_USD_RATE:.2f} INR")
        rate_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 14))

        ttk.Label(main_frame, text="INR amount").grid(row=2, column=0, sticky="w", pady=6)
        amount_entry = ttk.Entry(main_frame, textvariable=self.amount_var)
        amount_entry.grid(row=2, column=1, sticky="ew", padx=(8, 8), pady=6)
        amount_entry.focus()

        ttk.Button(main_frame, text="Convert", command=self.convert_single_amount).grid(
            row=2,
            column=2,
            sticky="ew",
            pady=6,
        )

        result_label = ttk.Label(
            main_frame,
            textvariable=self.result_var,
            font=("Segoe UI", 12, "bold"),
            wraplength=460,
        )
        result_label.grid(row=3, column=0, columnspan=3, sticky="w", pady=(8, 12))

        columns = ("inr", "usd")
        self.expense_table = ttk.Treeview(main_frame, columns=columns, show="headings", height=8)
        self.expense_table.heading("inr", text="Expense in INR")
        self.expense_table.heading("usd", text="Converted to USD")
        self.expense_table.column("inr", anchor="center", width=160)
        self.expense_table.column("usd", anchor="center", width=160)
        self.expense_table.grid(row=4, column=0, columnspan=3, sticky="nsew")

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.expense_table.yview)
        scrollbar.grid(row=4, column=3, sticky="ns")
        self.expense_table.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(main_frame)
        actions.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(12, 8))
        actions.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(actions, text="Add Amount", command=self.add_amount).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6),
        )
        ttk.Button(actions, text="Reset Samples", command=self.reset_samples).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=6,
        )
        ttk.Button(actions, text="Clear", command=self.clear_expenses).grid(
            row=0,
            column=2,
            sticky="ew",
            padx=(6, 0),
        )

        ttk.Label(main_frame, textvariable=self.total_var, foreground="#555555").grid(
            row=6,
            column=0,
            columnspan=3,
            sticky="w",
        )

        self.root.bind("<Return>", lambda _event: self.convert_single_amount())

    def convert_single_amount(self):
        try:
            usd_amount = convert_inr_to_usd(self.amount_var.get())
        except ValueError as exc:
            self.result_var.set(f"Error: {exc}")
            return

        amount = float(self.amount_var.get())
        self.result_var.set(f"INR {amount:.2f} = USD {usd_amount:.2f}")

    def add_amount(self):
        try:
            amount = float(self.amount_var.get())
            convert_inr_to_usd(amount)
        except ValueError as exc:
            self.result_var.set(f"Error: {exc}")
            return

        self.expenses.append(amount)
        self.amount_var.set("")
        self.result_var.set(f"Added INR {amount:.2f} to the expense list.")
        self._refresh_table()

    def reset_samples(self):
        self.expenses = list(DEFAULT_EXPENSES_INR)
        self.result_var.set("Sample expenses restored.")
        self._refresh_table()

    def clear_expenses(self):
        self.expenses = []
        self.result_var.set("Expense list cleared.")
        self._refresh_table()

    def _refresh_table(self):
        for item in self.expense_table.get_children():
            self.expense_table.delete(item)

        converted_expenses = convert_expenses(self.expenses)
        for amount_inr, amount_usd in converted_expenses:
            self.expense_table.insert("", "end", values=(f"INR {amount_inr:.2f}", f"USD {amount_usd:.2f}"))

        total_inr = sum(self.expenses)
        total_usd = convert_inr_to_usd(total_inr) if total_inr else 0
        self.total_var.set(f"Total: INR {total_inr:.2f} = USD {total_usd:.2f}")


def run_cli():
    print("INR to USD Expense Conversion")
    print(f"Exchange rate: 1 USD = {INR_TO_USD_RATE} INR")
    print()

    for amount_inr, amount_usd in convert_expenses(DEFAULT_EXPENSES_INR):
        print(f"INR {amount_inr:.2f} = USD {amount_usd:.2f}")

    return 0


def run_gui():
    root = tk.Tk()
    ExpenseConverterApp(root)
    root.mainloop()
    return 0


def main():
    parser = argparse.ArgumentParser(description="Convert INR expenses to USD.")
    parser.add_argument("--cli", action="store_true", help="Print the original prototype output")
    args = parser.parse_args()

    if args.cli:
        return run_cli()

    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
