Currency Converter
==================

This project contains two assignment parts:

1. Part1_Program
   A quick prototype INR-to-USD expense converter with a graphical interface
   and optional command-line output.

2. Part2_SystemsProduct
   A production-style currency converter with a graphical interface, optional
   command-line usage, a JSON rates file, logging, validation, and automated
   tests.


Installation
------------

Python 3.10 or newer is recommended.

No external packages are required. The requirements.txt file is included for
assignment completeness.


Part 1 Usage
------------

From the repository root, run this to open the interface:

    python Part1_Program/script.py

In Bash:

    cd /c/Users/Torshi/currency
    python Part1_Program/script.py

If your Bash uses python3 instead of python:

    python3 Part1_Program/script.py

The Part 1 interface lets you convert one INR amount, add it to the sample
expense list, reset the sample expenses, clear the list, and view totals.

To print the original command-line prototype output:

    python Part1_Program/script.py --cli


Part 2 Usage
------------

From the Part2_SystemsProduct folder, run this to open the interface:

    python main.py

In Bash, from the repository root:

    cd /c/Users/Torshi/currency/Part2_SystemsProduct
    python main.py

If your Bash uses python3 instead of python:

    python3 main.py

The interface lets you enter the amount, choose source and target currencies,
select the rate source, enter an optional API key, convert, and swap currencies.


Optional Command-Line Usage
---------------------------

The command-line mode is still available. From the Part2_SystemsProduct folder,
run:

    python main.py --from USD --to EUR --amount 150

In Bash, from the repository root:

    cd /c/Users/Torshi/currency/Part2_SystemsProduct
    python main.py --from USD --to EUR --amount 150 --source api

If you are already inside Part2_SystemsProduct, do not run cd again. Just run:

    python main.py --from INR --to USD --amount 9524 --source config

If your Bash uses python3 instead of python:

    python3 main.py --from INR --to USD --amount 9524 --source config

You can also force the graphical interface with:

    python main.py --gui

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

Then run:

    python main.py --from USD --to EUR --amount 150 --source api

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

In Bash:

    cd /c/Users/Torshi/currency
    python -m unittest discover Part2_SystemsProduct/tests

Or with python3:

    python3 -m unittest discover Part2_SystemsProduct/tests

The tests cover successful conversion, negative amount validation,
non-numeric input, unsupported currencies, and invalid/missing rates files.
