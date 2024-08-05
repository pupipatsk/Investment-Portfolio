# Investment-Portfolio

## Overview

Investment-Portfolio is a Python-based project designed to track and analyze investment transactions from various sources e.g. Dime US Stocks, Dime Mutual Funds.
The project leverages OCR (Optical Character Recognition) using [Tesseract](https://github.com/tesseract-ocr/tesseract.git) and the [pytesseract](https://github.com/madmaze/pytesseract.git) library to extract transaction data from slip images.
The extracted data is then processed, analyzed, and visualized to provide valuable insights into your investment portfolio.

## Features

- **OCR Processing**: Extracts data from transaction slips using Tesseract OCR.
- **Data Integration**: Combines data from different investment sources into a unified format.
- **Data Analysis**: Analyzes transaction data to provide insights and performance metrics.
- **Visualization**: Visualizes portfolio performance and transaction history using various charts and graphs.

## Prerequisites
- Python 3.6+
- Tesseract OCR
    ```bash
    # MacOS
    brew install tesseract
    ```
- Libraries
  -  pytesseract
  -  pillow
  -  pandas