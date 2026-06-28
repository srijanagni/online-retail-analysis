# Online Retail Sales Analysis

![Python](https://img.shields.io/badge/Python-3.9-blue) ![pandas](https://img.shields.io/badge/pandas-2.0-lightgrey) ![SQL](https://img.shields.io/badge/SQL-SQLite-orange)

End-to-end exploratory data analysis on 500K+ real retail transactions from a UK-based online store (2010–2011). Covers data cleaning, customer segmentation using RFM analysis, business intelligence queries in SQL, and data visualizations.

---

## Table of Contents
- [Overview](#overview)
- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Setup & Usage](#setup--usage)
- [Key Findings](#key-findings)
- [Visualizations](#visualizations)
- [Tech Stack](#tech-stack)

---

## Overview

This project analyzes transactional data from a UK-based non-store online retailer. The goal is to uncover revenue patterns, identify high-value customers, and surface actionable business insights.

**Business Questions Answered:**
- Which products and countries generate the most revenue?
- What does monthly revenue trend look like — is there seasonality?
- Who are the most valuable customers (RFM segmentation)?
- Which days of the week see the highest order volume?

---

## Dataset

| Property | Value |
|---|---|
| Source | [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/online+retail) |
| Records | ~541,000 transactions |
| Period | December 2010 – December 2011 |
| Features | InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country |

> **Note:** Download `online_retail.xlsx` from the link above and place it in the `data/` folder before running.

---

## Project Structure

```
online_retail_project/
├── data/
│   ├── online_retail.xlsx        # raw dataset (download separately)
│   ├── cleaned_retail.csv        # generated after running analysis.py
│   ├── rfm_segments.csv          # generated after running analysis.py
│   └── monthly_summary.csv       # generated after running analysis.py
├── notebooks/
│   └── analysis.ipynb            # Jupyter notebook version
├── sql/
│   └── queries.sql               # all SQL queries
├── visuals/                      # charts saved after running analysis.py
├── analysis.py                   # main analysis script
├── requirements.txt
└── README.md
```

---

## Setup & Usage

**1. Clone the repository**
```bash
git clone https://github.com/srijanagni/online-retail-analysis.git
cd online-retail-analysis
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Download the dataset**

Download `online_retail.xlsx` from [UCI / Kaggle](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci) and place it in the `data/` folder.

**4. Run the analysis**
```bash
python3 analysis.py
```

Outputs: cleaned CSVs in `data/`, charts in `visuals/`, SQL query results printed to console.

---

## Key Findings

- **85%** of revenue originates from the United Kingdom
- Revenue peaks in **November**, indicating strong seasonal/holiday demand
- Top **10% of customers** generate approximately **50% of total revenue**
- **Tuesday and Thursday** see the highest order volumes
- **Champions segment** customers have 3× higher average order value than Lost customers
- Top product by quantity: *WHITE HANGING HEART T-LIGHT HOLDER*

---

## Visualizations

| Chart | Description |
|---|---|
| `monthly_revenue.png` | Revenue trend over 12 months |
| `top_products.png` | Top 10 products by revenue |
| `top_countries.png` | Revenue by country |
| `orders_by_day.png` | Order volume by day of week |

---

## Tech Stack

- **Python** — pandas, NumPy, matplotlib, seaborn
- **SQL** — SQLite (via Python's `sqlite3`)
- **Jupyter Notebook** — for exploratory work
