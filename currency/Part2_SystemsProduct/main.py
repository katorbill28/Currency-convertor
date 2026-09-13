"""Command-line interface for the production currency converter."""

import argparse
import os
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


def build_parser():
    parser = argparse.ArgumentParser(description="Convert currency amounts.")
    parser.add_argument("--from", dest="from_currency", required=True, help="Source currency code")
    parser.add_argument("--to", dest="to_currency", required=True, help="Target currency code")
    parser.add_argument("--amount", required=True, help="Amount to convert")
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
    return parser


def main():
    logger = setup_logger(LOG_PATH)
    parser = build_parser()
    args = parser.parse_args()
    api_key = args.api_key or os.getenv("EXCHANGE_RATE_API_KEY")

    try:
        if args.source == "api":
            rates = fetch_rates_from_api(api_key=api_key)
            rate_source = "live keyed API" if api_key else "live open API"
        elif args.source == "config":
            rates = load_rates(args.rates)
            rate_source = "local config"
        else:
            try:
                rates = fetch_rates_from_api(api_key=api_key)
                rate_source = "live keyed API" if api_key else "live open API"
            except ApiError as exc:
                logger.warning("API unavailable, falling back to rates file: %s", exc)
                rates = load_rates(args.rates)
                rate_source = "local config fallback"

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


if __name__ == "__main__":
    raise SystemExit(main())
