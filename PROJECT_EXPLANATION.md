# Project Explanation: Online Retail Sales Analysis
### Written so you can explain it to anyone clearly

---

## WHAT IS THIS PROJECT ABOUT?

We took real transaction data from a UK-based online store — over 1 million rows of purchase records — and analyzed it to answer business questions like:
- Which products make the most money?
- Which countries buy the most?
- Which customers are most valuable?
- Is revenue growing month over month?

We used Python to clean and analyze the data, SQL to query it like a database, and the results are exported so they can be visualized in Power BI.

---

## THE DATASET

The dataset is called **Online Retail II** from the UCI Machine Learning Repository. It contains real sales data from December 2009 to December 2011.

Each row in the dataset represents one item in one order. So if a customer bought 3 products in one order, that's 3 rows.

The columns are:
- **Invoice** — the order ID
- **StockCode** — a code for the product
- **Description** — the name of the product
- **Quantity** — how many units were bought
- **InvoiceDate** — when the order was placed
- **Price** — the price per unit in British Pounds (GBP)
- **Customer ID** — a unique number for each customer
- **Country** — where the customer is from

---

## STEP-BY-STEP EXPLANATION OF THE CODE

---

### STEP 1 — LOADING THE DATA

```python
df = pd.read_csv(DATA_PATH, encoding='unicode_escape')
```

**What it does:**
We load the CSV file into a pandas DataFrame — think of it like loading the data into an Excel sheet inside Python. The `encoding='unicode_escape'` part is needed because the file contains special characters (like £ or accented letters in product names) that can cause errors without it.

**Difficulty you might face:**
- If you forget the encoding, Python throws a `UnicodeDecodeError`. This is one of the most common beginner errors when loading real-world CSV files.
- If the file is in the wrong folder, Python throws a `FileNotFoundError`.

---

### STEP 2 — RENAMING COLUMNS

```python
df = df.rename(columns={
    "Invoice":     "InvoiceNo",
    "Price":       "UnitPrice",
    "Customer ID": "CustomerID"
})
```

**What it does:**
The Online Retail II dataset uses slightly different column names than the original dataset. For example, it calls the price column "Price" instead of "UnitPrice", and the customer column "Customer ID" (with a space) instead of "CustomerID". We rename them so the rest of the code works consistently.

**Difficulty you might face:**
- If you don't rename and then try to use `df["UnitPrice"]`, Python throws a `KeyError` saying the column doesn't exist.
- The space in "Customer ID" is a very common source of bugs — easy to miss.

---

### STEP 3 — CLEANING THE DATA

Real-world data is never perfect. This step fixes all the problems.

#### Remove rows with missing Customer ID
```python
df = df.dropna(subset=["CustomerID"])
```
About 25% of rows have no Customer ID — these are guest checkouts. We drop them because we can't do customer-level analysis without knowing who the customer is.

#### Remove cancelled orders
```python
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
```
Any invoice starting with the letter "C" is a cancellation (e.g. "C536379"). We don't want cancellations in our revenue calculations. The `~` means "NOT" — keep everything that does NOT start with C.

#### Remove negative or zero quantities and prices
```python
df = df[df["Quantity"] > 0]
df = df[df["UnitPrice"] > 0]
```
Some rows have negative quantities (returns) or zero prices (free items or errors). We remove these to keep only valid sales.

#### Remove duplicates
```python
df = df.drop_duplicates()
```
Sometimes the same row appears twice in the data due to system errors. We remove exact duplicates.

#### Fix data types
```python
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["CustomerID"] = df["CustomerID"].astype(int)
```
When Python loads a CSV, it treats everything as text by default. We tell it that InvoiceDate is actually a date, and CustomerID is a whole number. This lets us do date calculations and group by customer later.

#### Create the Revenue column
```python
df["Revenue"] = df["Quantity"] * df["UnitPrice"]
```
The dataset doesn't have a revenue column — it only has quantity and price. We multiply them to calculate how much money each line item generated.

#### Extract date parts
```python
df["Year"] = df["InvoiceDate"].dt.year
df["Month"] = df["InvoiceDate"].dt.month
df["YearMonth"] = df["InvoiceDate"].dt.to_period("M")
df["DayOfWeek"] = df["InvoiceDate"].dt.day_name()
```
We extract the year, month, year-month combination, and day of week from the date column. This makes it easy to group and analyze by time period later.

**Difficulty you might face:**
- Forgetting to convert InvoiceDate to datetime format means date operations will fail.
- The cancellation filter is easy to miss — if you don't remove them, your revenue numbers will be wrong.
- Negative quantities and prices can silently distort your averages and totals if not removed.

---

### STEP 4 — EXPLORATORY DATA ANALYSIS (EDA)

This step answers visual questions about the data by creating charts.

#### Monthly Revenue Trend
```python
monthly_revenue = df.groupby("YearMonth")["Revenue"].sum().reset_index()
```
We group all transactions by month and add up the revenue for each month. This tells us whether the business is growing, shrinking, or seasonal.

#### Top 10 Products by Revenue
```python
top_products = df.groupby("Description")["Revenue"].sum().sort_values(ascending=False).head(10)
```
We group by product name, sum the revenue, sort from highest to lowest, and take the top 10. This tells us which products make the most money.

#### Top 10 Countries by Revenue
Same logic as above but grouped by country. Helps understand which markets are most important.

#### Orders by Day of Week
```python
orders_by_day = df.groupby("DayOfWeek")["InvoiceNo"].nunique().reindex(day_order)
```
We count how many unique orders were placed on each day of the week. `nunique()` counts unique values — important because one order can have many rows (one per product).

#### Distribution of Order Values
```python
order_value = df.groupby("InvoiceNo")["Revenue"].sum()
order_value[order_value < 500].hist(bins=50)
```
We first calculate the total value of each order (sum all items in that order), then plot a histogram to see how order values are distributed. We limit to under £500 to avoid a few very large outliers stretching the chart.

#### Quantity vs Unit Price Scatter Plot
```python
correlation = df["Quantity"].corr(df["UnitPrice"])
```
We check if there's a relationship between how many units are bought and the price. A negative correlation would mean cheaper items are bought in larger quantities.

**Difficulty you might face:**
- Using `count()` instead of `nunique()` for orders gives the wrong number — count includes every row, not every unique order.
- Forgetting `reset_index()` after `groupby` can cause issues when plotting.
- Outliers in order values make histograms unreadable — you need to filter them out manually.

---

### STEP 5 — SQL ANALYSIS

```python
conn = sqlite3.connect(DB_PATH)
df_sql.to_sql("retail", conn, if_exists="replace", index=False)
```

**What it does:**
We load the cleaned pandas DataFrame into a SQLite database — a lightweight database that lives as a single file on your computer. This lets us run SQL queries on the data.

We then run queries like:

**Monthly growth rate using a window function:**
```sql
LAG(revenue) OVER (ORDER BY YearMonth)
```
`LAG` is a window function that looks at the previous row's value. Here it gives us last month's revenue, so we can calculate the percentage change month over month.

**Repeat vs one-time customers:**
```sql
CASE WHEN order_count = 1 THEN 'One-Time' ELSE 'Repeat' END
```
We classify customers based on how many orders they've placed.

**Difficulty you might face:**
- SQLite doesn't support all SQL features — for example, some advanced window functions behave differently than in PostgreSQL or MySQL.
- The `YearMonth` column needs to be converted to a string before loading into SQLite, otherwise it throws an error because SQLite doesn't understand pandas Period objects.

---

### STEP 6 — RFM CUSTOMER SEGMENTATION

RFM stands for **Recency, Frequency, Monetary**. It's a classic marketing technique to classify customers by how valuable they are.

- **Recency** — how many days ago did the customer last buy? (lower = better)
- **Frequency** — how many orders have they placed? (higher = better)
- **Monetary** — how much total money have they spent? (higher = better)

```python
rfm = df.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda x: (reference_date - x.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("Revenue", "sum")
).reset_index()
```

For each customer we calculate all three values. Then we score them 1–4 on each dimension using quartiles:

```python
rfm["R_Score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1])
```

`pd.qcut` splits the data into 4 equal groups. Score 4 = best recency (bought recently), score 1 = worst (bought a long time ago). Note the labels are reversed for Recency because lower recency days = better.

Then we add up the three scores and classify:

```python
if score >= 10:   → "Champions"       (buy often, recently, spend a lot)
elif score >= 7:  → "Loyal Customers" (good but not top tier)
elif score >= 5:  → "At Risk"         (used to buy but slowing down)
else:             → "Lost"            (haven't bought in a long time)
```

**Difficulty you might face:**
- `pd.qcut` throws an error if there are duplicate values at the bin edges — fixed by using `rank(method='first')` for Frequency.
- The reference date must be one day AFTER the last transaction, not the same day — otherwise the most recent customer gets a Recency of 0 which can cause issues.
- Forgetting to reverse the Recency score labels is a common mistake — lower days = better customer, so it should get a higher score.

---

### STEP 7 — EXPORTING FOR POWER BI

```python
df_export.to_csv("data/cleaned_retail.csv", index=False)
rfm.to_csv("data/rfm_segments.csv", index=False)
monthly_summary.to_csv("data/monthly_summary.csv", index=False)
```

We export three CSV files:
- `cleaned_retail.csv` — the full cleaned transaction data
- `rfm_segments.csv` — one row per customer with their RFM scores and segment
- `monthly_summary.csv` — revenue, orders, and customers per month

These three files are imported into Power BI to build the dashboard.

**Difficulty you might face:**
- The `YearMonth` column is a pandas Period object — Power BI can't read it. You must convert it to a string first with `.astype(str)`.
- Same for `InvoiceDate` — convert to string before exporting, otherwise Power BI may misinterpret the format.

---

## COMMON ERRORS AND HOW TO FIX THEM

| Error | Cause | Fix |
|-------|-------|-----|
| `UnicodeDecodeError` | Special characters in CSV | Add `encoding='unicode_escape'` to read_csv |
| `KeyError: 'UnitPrice'` | Column not renamed | Add the rename step at the top |
| `KeyError: 'CustomerID'` | Space in "Customer ID" | Same rename fix |
| `ValueError in pd.qcut` | Duplicate bin edges | Use `.rank(method='first')` before qcut |
| `AttributeError: Period` | YearMonth not converted to string | Add `.astype(str)` before export |
| `FileNotFoundError` | CSV not in data/ folder | Make sure file is named correctly and in the right folder |

---

## HOW TO EXPLAIN THIS PROJECT IN AN INTERVIEW

**"What did you do in this project?"**

> "I took 1 million rows of real transaction data from a UK online retailer and built an end-to-end analysis pipeline. I used Python to clean the data — removing cancellations, nulls, and invalid entries — then did exploratory analysis to find revenue trends, top products, and customer behavior. I used SQL window functions to calculate month-over-month growth, and applied RFM segmentation to classify customers into Champions, Loyal, At Risk, and Lost groups. Finally I exported the data to Power BI for an interactive dashboard."

**"What was the hardest part?"**

> "The data cleaning was the most important part. About 25% of rows had no customer ID, there were thousands of cancelled orders, and some rows had negative quantities. If you don't handle all of that carefully, every number in your analysis is wrong."

**"What did you find?"**

> "85% of revenue came from the UK. Revenue spiked in November — classic seasonal demand. And the top 10% of customers generated about half of all revenue, which is a strong signal for where to focus retention efforts."

---

*This project demonstrates: data cleaning, EDA, SQL, window functions, customer segmentation, and business storytelling — all core data analyst skills.*

---

## RESUME DESCRIPTIONS

Use one of these depending on how much space you have on your resume.

**Option 1 — One line (tight resume)**
> Analyzed 1M+ real retail transactions using Python and SQL; built Power BI dashboard tracking revenue trends, customer segmentation, and product performance across 38 countries.

**Option 2 — Two lines (recommended)**
> Performed end-to-end sales analysis on 1M+ transactional records using Python (pandas, matplotlib) and SQL. Applied RFM segmentation to classify customers and built an interactive Power BI dashboard covering revenue trends, top products, and regional performance.

**Option 3 — Bullet points (if your resume uses bullet format)**
- Cleaned and analyzed 1M+ real retail transactions using Python (pandas), handling nulls, cancellations, and duplicates
- Wrote SQL queries including window functions to calculate month-over-month revenue growth
- Applied RFM segmentation to classify 4,000+ customers into Champions, Loyal, At Risk, and Lost groups
- Built a 3-page interactive Power BI dashboard with KPI cards, slicers, and DAX measures

**Recommendation:** Use Option 3 if you have space — bullet points are easier to scan and each line highlights a specific skill (Python, SQL, RFM, Power BI) that recruiters and ATS systems look for.
