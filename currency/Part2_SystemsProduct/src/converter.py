"""Currency conversion logic backed by a JSON rates configuration file."""

import json
import urllib.error
import urllib.request
from pathlib import Path


class CurrencyConverterError(Exception):
    """Base exception for user-facing converter errors."""


class RatesFileError(CurrencyConverterError):
    """Raised when the rates file is missing or invalid."""


class UnsupportedCurrencyError(CurrencyConverterError):
    """Raised when a requested currency code is not available."""


class InvalidAmountError(CurrencyConverterError):
    """Raised when the requested amount cannot be converted."""


class ApiError(CurrencyConverterError):
    """Raised when live API rates cannot be loaded."""


OPEN_API_URL = "https://open.er-api.com/v6/latest/USD"
KEYED_API_URL_TEMPLATE = "https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"


def load_rates(rates_path):
    """Load currency rates from a JSON file.

    The rates file stores each currency as its value per 1 USD.
    Example: {"USD": 1.0, "INR": 95.24, "EUR": 0.92}
    """
    path = Path(rates_path)

    if not path.exists():
        raise RatesFileError(f"Rates file not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RatesFileError("Rates file is not valid JSON.") from exc
    except OSError as exc:
        raise RatesFileError(f"Could not read rates file: {path}") from exc

    rates = data.get("rates") if isinstance(data, dict) else None
    if not isinstance(rates, dict) or not rates:
        raise RatesFileError("Rates file must contain a non-empty 'rates' object.")

    normalized_rates = {}
    for code, rate in rates.items():
        normalized_code = str(code).upper()
        try:
            normalized_rate = float(rate)
        except (TypeError, ValueError) as exc:
            raise RatesFileError(f"Invalid rate for {normalized_code}.") from exc

        if normalized_rate <= 0:
            raise RatesFileError(f"Rate for {normalized_code} must be greater than zero.")

        normalized_rates[normalized_code] = normalized_rate

    if "USD" not in normalized_rates:
        raise RatesFileError("Rates file must include USD.")

    return normalized_rates


def fetch_rates_from_api(api_key=None, api_url=None, timeout=10):
    """Fetch latest USD-based exchange rates from ExchangeRate-API."""
    if api_url is None:
        api_url = (
            KEYED_API_URL_TEMPLATE.format(api_key=api_key)
            if api_key
            else OPEN_API_URL
        )

    request = urllib.request.Request(
        api_url,
        headers={"User-Agent": "currency-converter-assignment/1.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise ApiError("Could not connect to the currency API.") from exc
    except TimeoutError as exc:
        raise ApiError("Currency API request timed out.") from exc

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ApiError("Currency API returned invalid JSON.") from exc

    if data.get("result") not in (None, "success"):
        raise ApiError("Currency API returned an unsuccessful response.")

    rates = data.get("rates") or data.get("conversion_rates")
    if not isinstance(rates, dict) or not rates:
        raise ApiError("Currency API response did not include rates.")

    normalized_rates = {}
    for code, rate in rates.items():
        normalized_code = str(code).upper()
        try:
            normalized_rate = float(rate)
        except (TypeError, ValueError) as exc:
            raise ApiError(f"Currency API returned an invalid rate for {normalized_code}.") from exc

        if normalized_rate <= 0:
            raise ApiError(f"Currency API returned a non-positive rate for {normalized_code}.")

        normalized_rates[normalized_code] = normalized_rate

    if "USD" not in normalized_rates:
        raise ApiError("Currency API response must include USD.")

    return normalized_rates


def parse_amount(value):
    """Convert a CLI amount value into a valid non-negative float."""
    try:
        amount = float(value)
    except (TypeError, ValueError) as exc:
        raise InvalidAmountError("Amount must be a valid number.") from exc

    if amount < 0:
        raise InvalidAmountError("Amount cannot be negative.")

    return amount


def convert_currency(amount, from_currency, to_currency, rates):
    """Convert amount from one currency to another using USD-based rates."""
    amount = parse_amount(amount)
    source = str(from_currency).upper()
    target = str(to_currency).upper()

    if source not in rates:
        raise UnsupportedCurrencyError(f"Unsupported currency code: {source}")
    if target not in rates:
        raise UnsupportedCurrencyError(f"Unsupported currency code: {target}")

    amount_in_usd = amount / rates[source]
    return amount_in_usd * rates[target]
