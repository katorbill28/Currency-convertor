Currency Converter
==================

This project contains two assignment parts:

1. Part1_Program
   A quick prototype script that converts hardcoded INR expenses to USD.

2. Part2_SystemsProduct
   A production-style command-line currency converter using a JSON rates file,
   logging, validation, and automated tests.


Installation
------------

Python 3.10 or newer is recommended.

No external packages are required. The requirements.txt file is included for
assignment completeness.


Part 1 Usage
------------

From the repository root, run:

    python Part1_Program/script.py


Part 2 Usage
------------

From the Part2_SystemsProduct folder, run:

    python main.py --from USD --to EUR --amount 150

By default, the app tries the live ExchangeRate-API endpoint first.

If an API key is provided, it uses:

    https://v6.exchangerate-api.com/v6/YOUR-API-KEY/latest/USD

Without an API key, it uses the open endpoint:

    https://open.er-api.com/v6/latest/USD

If the API is unavailable, it automatically falls back to rates.json.

Examples:

    python main.py --from INR --to USD --amount 9524
    python main.py --from USD --to GBP --amount 75.50
    python main.py --from EUR --to INR --amount 20
    python main.py --from USD --to EUR --amount 150 --source api
    python main.py --from USD --to EUR --amount 150 --source api --api-key YOUR-API-KEY
    python main.py --from USD --to EUR --amount 150 --source config


API and Rates Configuration
---------------------------

The application includes live API integration using ExchangeRate-API's open
access endpoint and the official API-key endpoint.

To use your API key temporarily:

    python main.py --from USD --to EUR --amount 150 --source api --api-key YOUR-API-KEY

To avoid typing the key each time, set an environment variable.

PowerShell:

    $env:EXCHANGE_RATE_API_KEY="YOUR-API-KEY"

Bash:

    export EXCHANGE_RATE_API_KEY="YOUR-API-KEY"

You can choose the rate source:

    --source auto
    --source api
    --source config

The default is auto, which tries the API and then uses rates.json if the API
cannot be reached.

The local rates.json file stores rates as the value of each currency for 1 USD.

Example:

    {
      "base": "USD",
      "rates": {
        "USD": 1.0,
        "INR": 95.24,
        "EUR": 0.92
      }
    }

To use another rates file:

    python main.py --from USD --to INR --amount 10 --rates path/to/rates.json


Logging
-------

Successful conversions and handled errors are written to:

    app.log


Testing
-------

From the repository root, run:

    python -m unittest discover Part2_SystemsProduct/tests

The tests cover successful conversion, negative amount validation,
non-numeric input, unsupported currencies, and invalid/missing rates files.
