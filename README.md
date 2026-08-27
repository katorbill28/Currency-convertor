# Currency Converter

A simple command-line currency converter built with Python.

## Features

* Convert between different currencies
* Supports API and JSON exchange rates
* Simple command-line interface
* Error handling
* Logging
* Unit tests

## Requirements

* Python 3.10+

## Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd currency-converter
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Using API

```bash
python main.py --from USD --to EUR --amount 150 --source api
```

### Using JSON

```bash
python main.py --from USD --to EUR --amount 150 --source json
```

## API Configuration

If the API requires an API key, store it in an environment variable instead of putting it directly in the code.

## Project Structure

```text
currency-converter/
├── main.py
├── rates.json
├── requirements.txt
├── app.log
├── src/
│   ├── converter.py
│   └── logger.py
└── tests/
    └── test_converter.py
```

## Testing

Run the tests with:

```bash
pytest
```

## Logging

Application operations and errors are stored in:

```text
app.log
```

## License

This project is for educational purposes.
