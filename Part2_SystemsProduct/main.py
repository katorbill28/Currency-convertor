"""Currency converter app with both GUI and command-line interfaces."""

import argparse
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from src.converter import (
    ApiError,
    CurrencyConverterError,
    convert_currency,
    fetch_rates_from_api,
    load_rates,
)
from src.logger import setup_logger


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_RATES_PATH = PROJECT_DIR / "rates.json"
LOG_PATH = PROJECT_DIR / "app.log"


def get_rates(source, rates_path, api_key, logger):
    """Load rates from the selected source."""
    if source == "api":
        rates = fetch_rates_from_api(api_key=api_key)
        rate_source = "live keyed API" if api_key else "live open API"
    elif source == "config":
        rates = load_rates(rates_path)
        rate_source = "local config"
    else:
        try:
            rates = fetch_rates_from_api(api_key=api_key)
            rate_source = "live keyed API" if api_key else "live open API"
        except ApiError as exc:
            logger.warning("API unavailable, falling back to rates file: %s", exc)
            rates = load_rates(rates_path)
            rate_source = "local config fallback"

    return rates, rate_source


def build_parser():
    parser = argparse.ArgumentParser(description="Convert currency amounts.")
    parser.add_argument("--from", dest="from_currency", help="Source currency code")
    parser.add_argument("--to", dest="to_currency", help="Target currency code")
    parser.add_argument("--amount", help="Amount to convert")
    parser.add_argument(
        "--source",
        choices=["auto", "api", "config"],
        default="auto",
        help="Rate source: live API, local config, or auto fallback",
    )
    parser.add_argument(
        "--rates",
        default=str(DEFAULT_RATES_PATH),
        help="Path to a JSON rates configuration file",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="ExchangeRate-API key. Can also be set with EXCHANGE_RATE_API_KEY.",
    )
    parser.add_argument("--gui", action="store_true", help="Open the graphical interface")
    return parser


class CurrencyConverterApp:
    def __init__(self, root, logger):
        self.root = root
        self.logger = logger
        self.rates = None
        self.rate_source = None

        self.root.title("Currency Converter")
        self.root.geometry("460x380")
        self.root.minsize(420, 360)

        self.amount_var = tk.StringVar()
        self.from_var = tk.StringVar(value="USD")
        self.to_var = tk.StringVar(value="INR")
        self.source_var = tk.StringVar(value="config")
        self.status_var = tk.StringVar(value="Ready")
        self.result_var = tk.StringVar(value="Enter an amount and convert.")
        self.api_key_var = tk.StringVar(value=os.getenv("EXCHANGE_RATE_API_KEY", ""))

        self.currency_values = self._load_initial_currency_values()
        self._build_widgets()

    def _load_initial_currency_values(self):
        try:
            rates = load_rates(DEFAULT_RATES_PATH)
        except CurrencyConverterError:
            return ["USD", "INR", "EUR", "GBP", "JPY", "AUD", "CAD"]

        return sorted(rates)

    def _build_widgets(self):
        self.root.columnconfigure(0, weight=1)

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(1, weight=1)

        title = ttk.Label(main_frame, text="Currency Converter", font=("Segoe UI", 18, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 18))

        ttk.Label(main_frame, text="Amount").grid(row=1, column=0, sticky="w", pady=6)
        amount_entry = ttk.Entry(main_frame, textvariable=self.amount_var)
        amount_entry.grid(row=1, column=1, sticky="ew", pady=6)
        amount_entry.focus()

        ttk.Label(main_frame, text="From").grid(row=2, column=0, sticky="w", pady=6)
        from_box = ttk.Combobox(
            main_frame,
            textvariable=self.from_var,
            values=self.currency_values,
            state="readonly",
        )
        from_box.grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(main_frame, text="To").grid(row=3, column=0, sticky="w", pady=6)
        to_box = ttk.Combobox(
            main_frame,
            textvariable=self.to_var,
            values=self.currency_values,
            state="readonly",
        )
        to_box.grid(row=3, column=1, sticky="ew", pady=6)

        ttk.Label(main_frame, text="Rate source").grid(row=4, column=0, sticky="w", pady=6)
        source_box = ttk.Combobox(
            main_frame,
            textvariable=self.source_var,
            values=("config", "auto", "api"),
            state="readonly",
        )
        source_box.grid(row=4, column=1, sticky="ew", pady=6)

        ttk.Label(main_frame, text="API key").grid(row=5, column=0, sticky="w", pady=6)
        ttk.Entry(main_frame, textvariable=self.api_key_var, show="*").grid(
            row=5,
            column=1,
            sticky="ew",
            pady=6,
        )

        actions = ttk.Frame(main_frame)
        actions.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(14, 12))
        actions.columnconfigure((0, 1), weight=1)

        self.convert_button = ttk.Button(actions, text="Convert", command=self.convert)
        self.convert_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(actions, text="Swap", command=self.swap_currencies).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0),
        )

        result_label = ttk.Label(
            main_frame,
            textvariable=self.result_var,
            font=("Segoe UI", 14, "bold"),
            wraplength=390,
        )
        result_label.grid(row=7, column=0, columnspan=2, sticky="w", pady=(8, 4))

        ttk.Label(main_frame, textvariable=self.status_var, foreground="#555555").grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="w",
        )

        self.root.bind("<Return>", lambda _event: self.convert())

    def swap_currencies(self):
        source = self.from_var.get()
        target = self.to_var.get()
        self.from_var.set(target)
        self.to_var.set(source)

    def convert(self):
        self.convert_button.configure(state="disabled")
        self.status_var.set("Loading rates...")
        self.result_var.set("Working...")

        worker = threading.Thread(target=self._convert_in_background, daemon=True)
        worker.start()

    def _convert_in_background(self):
        try:
            api_key = self.api_key_var.get().strip() or None
            rates, rate_source = get_rates(
                self.source_var.get(),
                DEFAULT_RATES_PATH,
                api_key,
                self.logger,
            )
            result = convert_currency(
                self.amount_var.get(),
                self.from_var.get(),
                self.to_var.get(),
                rates,
            )
        except CurrencyConverterError as exc:
            self.logger.error(str(exc))
            self.root.after(0, self._show_error, str(exc))
            return

        amount = float(self.amount_var.get())
        source = self.from_var.get().upper()
        target = self.to_var.get().upper()
        self.logger.info(
            "Converted %.2f %s to %.2f %s using %s",
            amount,
            source,
            result,
            target,
            rate_source,
        )
        self.root.after(0, self._show_result, amount, source, result, target, rate_source)

    def _show_result(self, amount, source, result, target, rate_source):
        self.result_var.set(f"{amount:.2f} {source} = {result:.2f} {target}")
        self.status_var.set(f"Using {rate_source}")
        self.convert_button.configure(state="normal")

    def _show_error(self, message):
        self.result_var.set(f"Error: {message}")
        self.status_var.set("Please check the input and try again.")
        self.convert_button.configure(state="normal")


def run_gui(logger):
    root = tk.Tk()
    CurrencyConverterApp(root, logger)
    root.mainloop()
    return 0


def run_cli(args, logger):
    missing = [
        option
        for option, value in (
            ("--from", args.from_currency),
            ("--to", args.to_currency),
            ("--amount", args.amount),
        )
        if value is None
    ]
    if missing:
        print(f"Error: missing required CLI arguments: {', '.join(missing)}")
        print("Run without arguments to open the interface, or use --help for CLI usage.")
        return 2

    api_key = args.api_key or os.getenv("EXCHANGE_RATE_API_KEY")

    try:
        rates, rate_source = get_rates(args.source, args.rates, api_key, logger)
        result = convert_currency(
            args.amount,
            args.from_currency,
            args.to_currency,
            rates,
        )
    except CurrencyConverterError as exc:
        logger.error(str(exc))
        print(f"Error: {exc}")
        return 1

    source = args.from_currency.upper()
    target = args.to_currency.upper()
    amount = float(args.amount)
    logger.info(
        "Converted %.2f %s to %.2f %s using %s",
        amount,
        source,
        result,
        target,
        rate_source,
    )
    print(f"{amount:.2f} {source} = {result:.2f} {target}")
    return 0


def main(argv=None):
    logger = setup_logger(LOG_PATH)
    parser = build_parser()
    args = parser.parse_args(argv)
    provided_args = sys.argv[1:] if argv is None else argv

    if args.gui or len(provided_args) == 0:
        return run_gui(logger)

    return run_cli(args, logger)


if __name__ == "__main__":
    raise SystemExit(main())
