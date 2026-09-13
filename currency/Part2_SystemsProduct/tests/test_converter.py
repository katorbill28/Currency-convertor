import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Part2_SystemsProduct.src.converter import (
    ApiError,
    InvalidAmountError,
    RatesFileError,
    UnsupportedCurrencyError,
    convert_currency,
    fetch_rates_from_api,
    load_rates,
)


class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.rates = {"USD": 1.0, "INR": 95.24, "EUR": 0.92}

    def test_convert_usd_to_eur(self):
        result = convert_currency(150, "USD", "EUR", self.rates)
        self.assertAlmostEqual(result, 138.0)

    def test_convert_inr_to_usd(self):
        result = convert_currency(95.24, "INR", "USD", self.rates)
        self.assertAlmostEqual(result, 1.0)

    def test_negative_amount_raises_error(self):
        with self.assertRaises(InvalidAmountError):
            convert_currency(-10, "USD", "EUR", self.rates)

    def test_non_numeric_amount_raises_error(self):
        with self.assertRaises(InvalidAmountError):
            convert_currency("abc", "USD", "EUR", self.rates)

    def test_unsupported_currency_raises_error(self):
        with self.assertRaises(UnsupportedCurrencyError):
            convert_currency(10, "USD", "XYZ", self.rates)

    def test_load_rates_from_json_file(self):
        payload = {"base": "USD", "rates": self.rates}
        with tempfile.TemporaryDirectory() as temp_dir:
            rates_path = Path(temp_dir) / "rates.json"
            rates_path.write_text(json.dumps(payload), encoding="utf-8")

            loaded_rates = load_rates(rates_path)

        self.assertEqual(loaded_rates["USD"], 1.0)
        self.assertEqual(loaded_rates["INR"], 95.24)

    def test_missing_rates_file_raises_error(self):
        with self.assertRaises(RatesFileError):
            load_rates("missing-rates-file.json")

    def test_invalid_rates_file_raises_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            rates_path = Path(temp_dir) / "rates.json"
            rates_path.write_text("not json", encoding="utf-8")

            with self.assertRaises(RatesFileError):
                load_rates(rates_path)

    def _fake_api_response(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def read(self):
                return json.dumps({"result": "success", "rates": self.rates}).encode("utf-8")

        fake_response = FakeResponse()
        fake_response.rates = self.rates
        return fake_response

    @patch("Part2_SystemsProduct.src.converter.urllib.request.urlopen")
    def test_fetch_rates_from_api(self, mock_urlopen):
        fake_response = self._fake_api_response()
        mock_urlopen.return_value = fake_response

        loaded_rates = fetch_rates_from_api()

        self.assertEqual(loaded_rates["USD"], 1.0)
        self.assertEqual(loaded_rates["EUR"], 0.92)

    @patch("Part2_SystemsProduct.src.converter.urllib.request.urlopen")
    def test_fetch_rates_from_api_with_key(self, mock_urlopen):
        fake_response = self._fake_api_response()
        mock_urlopen.return_value = fake_response

        loaded_rates = fetch_rates_from_api(api_key="test-key")
        request = mock_urlopen.call_args.args[0]

        self.assertIn("/test-key/latest/USD", request.full_url)
        self.assertEqual(loaded_rates["USD"], 1.0)

    @patch("Part2_SystemsProduct.src.converter.urllib.request.urlopen")
    def test_fetch_rates_from_keyed_api_response_shape(self, mock_urlopen):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def read(self):
                payload = {"result": "success", "conversion_rates": self.rates}
                return json.dumps(payload).encode("utf-8")

        fake_response = FakeResponse()
        fake_response.rates = self.rates
        mock_urlopen.return_value = fake_response

        loaded_rates = fetch_rates_from_api(api_key="test-key")

        self.assertEqual(loaded_rates["USD"], 1.0)
        self.assertEqual(loaded_rates["INR"], 95.24)

    @patch("Part2_SystemsProduct.src.converter.urllib.request.urlopen")
    def test_fetch_rates_from_api_failure(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError()

        with self.assertRaises(ApiError):
            fetch_rates_from_api()


if __name__ == "__main__":
    unittest.main()
