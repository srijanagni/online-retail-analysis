import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import datetime
import os

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

DATA_PATH = "data/online_retail.csv"
VISUALS_PATH = "visuals/"
DB_PATH = "data/retail.db"

os.makedirs(VISUALS_PATH, exist_ok=True)
os.makedirs("data", exist_ok=True)

# ─────────────────────────────────────────────
# STEP 1: LOAD DATA
# ─────────────────────────────────────────────

print("Loading data...")
df = pd.read_csv(DATA_PATH, encoding='unicode_escape')

# Rename columns to standardized names
df = df.rename(columns={
    "Invoice":     "InvoiceNo",
    "Price":       "UnitPrice",
    "Customer ID": "CustomerID"
})

print(f"Raw data shape: {df.shape}")
print(df.head())
print("\nMissing values:\n", df.isnull().sum())
print("\nDuplicates:", df.duplicated().sum())

# ─────────────────────────────────────────────
# STEP 2: CLEAN DATA
# ─────────────────────────────────────────────

print("\nCleaning data...")

# Drop rows with missing CustomerID
df = df.dropna(subset=["CustomerID"])

# Remove cancelled orders (InvoiceNo starting with 'C')
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]

# Remove rows with negative or zero Quantity and UnitPrice
df = df[df["Quantity"] > 0]
df = df[df["UnitPrice"] > 0]

# Remove duplicates
df = df.drop_duplicates()

# Fix data types
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["CustomerID"] = df["CustomerID"].astype(int)

# Create Revenue column
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

# Extract date parts
df["Year"] = df["InvoiceDate"].dt.year
df["Month"] = df["InvoiceDate"].dt.month
df["YearMonth"] = df["InvoiceDate"].dt.to_period("M")
df["DayOfWeek"] = df["InvoiceDate"].dt.day_name()

print(f"Cleaned data shape: {df.shape}")
print(df.dtypes)

# ─────────────────────────────────────────────
# STEP 3: EXPLORATORY DATA ANALYSIS
# ─────────────────────────────────────────────

print("\nRunning EDA...")

# ── 3.1 Monthly Revenue Trend ──
monthly_revenue = df.groupby("YearMonth")["Revenue"].sum().reset_index()
monthly_revenue["YearMonth"] = monthly_revenue["YearMonth"].astype(str)

plt.figure(figsize=(12, 5))
plt.plot(monthly_revenue["YearMonth"], monthly_revenue["Revenue"], marker="o", color="steelblue")
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue (GBP)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{VISUALS_PATH}monthly_revenue.png")
plt.close()
print("Saved: monthly_revenue.png")

# ── 3.2 Top 10 Products by Revenue ──
top_products = (
    df.groupby("Description")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure(figsize=(10, 6))
top_products.plot(kind="barh", color="coral")
plt.title("Top 10 Products by Revenue")
plt.xlabel("Revenue (GBP)")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f"{VISUALS_PATH}top_products.png")
plt.close()
print("Saved: top_products.png")

# ── 3.3 Top 10 Countries by Revenue ──
top_countries = (
    df.groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure(figsize=(10, 6))
top_countries.plot(kind="bar", color="mediumseagreen")
plt.title("Top 10 Countries by Revenue")
plt.xlabel("Country")
plt.ylabel("Revenue (GBP)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{VISUALS_PATH}top_countries.png")
plt.close()
print("Saved: top_countries.png")

# ── 3.4 Orders by Day of Week ──
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
orders_by_day = df.groupby("DayOfWeek")["InvoiceNo"].nunique().reindex(day_order)

plt.figure(figsize=(8, 5))
orders_by_day.plot(kind="bar", color="mediumpurple")
plt.title("Number of Orders by Day of Week")
plt.xlabel("Day")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{VISUALS_PATH}orders_by_day.png")
plt.close()
print("Saved: orders_by_day.png")

# ── 3.5 Distribution of Order Values ──
order_value = df.groupby("InvoiceNo")["Revenue"].sum()

plt.figure(figsize=(10, 5))
order_value[order_value < 500].hist(bins=50, color="steelblue", edgecolor="white")
plt.title("Distribution of Order Values (under £500)")
plt.xlabel("Order Value (GBP)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig(f"{VISUALS_PATH}order_distribution.png")
plt.close()
print("Saved: order_distribution.png")

# ── 3.6 Quantity vs Unit Price Scatter ──
plt.figure(figsize=(8, 5))
plt.scatter(df["Quantity"], df["UnitPrice"], alpha=0.3, color="tomato", s=5)
plt.title("Quantity vs Unit Price")
plt.xlabel("Quantity")
plt.ylabel("Unit Price (GBP)")
plt.xlim(0, 100)
plt.ylim(0, 50)
plt.tight_layout()
plt.savefig(f"{VISUALS_PATH}quantity_vs_price.png")
plt.close()
print("Saved: quantity_vs_price.png")

correlation = df["Quantity"].corr(df["UnitPrice"])
print(f"Correlation between Quantity and Unit Price: {correlation:.4f}")

# ─────────────────────────────────────────────
# STEP 4: SQL ANALYSIS
# ─────────────────────────────────────────────

print("\nLoading data into SQLite...")
df_sql = df.copy()
df_sql["YearMonth"] = df_sql["YearMonth"].astype(str)
df_sql["InvoiceDate"] = df_sql["InvoiceDate"].astype(str)

conn = sqlite3.connect(DB_PATH)
df_sql.to_sql("retail", conn, if_exists="replace", index=False)
print("Data loaded into SQLite successfully.")

queries = {
    "Overall Summary": """
        SELECT
            COUNT(DISTINCT InvoiceNo)  AS total_orders,
            COUNT(DISTINCT CustomerID) AS total_customers,
            ROUND(SUM(Revenue), 2)     AS total_revenue,
            ROUND(AVG(Revenue), 2)     AS avg_order_value
        FROM retail
    """,
    "Monthly Revenue": """
        SELECT
            YearMonth,
            ROUND(SUM(Revenue), 2)        AS monthly_revenue,
            COUNT(DISTINCT InvoiceNo)     AS orders
        FROM retail
        GROUP BY YearMonth
        ORDER BY YearMonth
    """,
    "Top 10 Products": """
        SELECT
            Description,
            SUM(Quantity)              AS total_units_sold,
            ROUND(SUM(Revenue), 2)     AS total_revenue
        FROM retail
        GROUP BY Description
        ORDER BY total_revenue DESC
        LIMIT 10
    """,
    "Revenue by Country": """
        SELECT
            Country,
            COUNT(DISTINCT CustomerID) AS customers,
            ROUND(SUM(Revenue), 2)     AS total_revenue
        FROM retail
        GROUP BY Country
        ORDER BY total_revenue DESC
    """,
    "Top 10 Customers": """
        SELECT
            CustomerID,
            COUNT(DISTINCT InvoiceNo)  AS total_orders,
            ROUND(SUM(Revenue), 2)     AS total_spent
        FROM retail
        GROUP BY CustomerID
        ORDER BY total_spent DESC
        LIMIT 10
    """,
    "Avg Order Value by Country": """
        SELECT
            Country,
            COUNT(DISTINCT InvoiceNo)                                  AS orders,
            ROUND(SUM(Revenue) / COUNT(DISTINCT InvoiceNo), 2)         AS avg_order_value
        FROM retail
        GROUP BY Country
        ORDER BY avg_order_value DESC
        LIMIT 10
    """
}

for name, query in queries.items():
    print(f"\n── {name} ──")
    result = pd.read_sql_query(query, conn)
    print(result.to_string(index=False))

conn.close()

# ─────────────────────────────────────────────
# STEP 5: RFM CUSTOMER SEGMENTATION
# ─────────────────────────────────────────────

print("\nRunning RFM segmentation...")

reference_date = df["InvoiceDate"].max() + datetime.timedelta(days=1)

rfm = df.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda x: (reference_date - x.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("Revenue", "sum")
).reset_index()

rfm["Monetary"] = rfm["Monetary"].round(2)

rfm["R_Score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1])
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
rfm["M_Score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4])

def segment(row):
    score = int(row["R_Score"]) + int(row["F_Score"]) + int(row["M_Score"])
    if score >= 10:
        return "Champions"
    elif score >= 7:
        return "Loyal Customers"
    elif score >= 5:
        return "At Risk"
    else:
        return "Lost"

rfm["Segment"] = rfm.apply(segment, axis=1)

print("\nCustomer Segments:")
print(rfm["Segment"].value_counts())
print("\nRFM Sample:")
print(rfm.head(10).to_string(index=False))

# RFM segment revenue summary
segment_summary = rfm.groupby("Segment").agg(
    Customers=("CustomerID", "count"),
    Avg_Recency=("Recency", "mean"),
    Avg_Frequency=("Frequency", "mean"),
    Avg_Monetary=("Monetary", "mean")
).round(2).reset_index()

print("\nSegment Summary:")
print(segment_summary.to_string(index=False))

# ── RFM Segment Bar Chart ──
segment_counts = rfm["Segment"].value_counts()
plt.figure(figsize=(8, 5))
segment_counts.plot(kind="bar", color=["#2ecc71", "#3498db", "#e67e22", "#e74c3c"])
plt.title("Customer Segments (RFM)")
plt.xlabel("Segment")
plt.ylabel("Number of Customers")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(f"{VISUALS_PATH}rfm_segments.png")
plt.close()
print("Saved: rfm_segments.png")

# ─────────────────────────────────────────────
# STEP 6: EXPORT DATA FOR POWER BI
# ─────────────────────────────────────────────

print("\nExporting data for Power BI...")

df_export = df.copy()
df_export["YearMonth"] = df_export["YearMonth"].astype(str)
df_export["InvoiceDate"] = df_export["InvoiceDate"].astype(str)
df_export.to_csv("data/cleaned_retail.csv", index=False)
print("Exported: data/cleaned_retail.csv")

rfm.to_csv("data/rfm_segments.csv", index=False)
print("Exported: data/rfm_segments.csv")

monthly_summary = df.groupby("YearMonth").agg(
    Revenue=("Revenue", "sum"),
    Orders=("InvoiceNo", "nunique"),
    Customers=("CustomerID", "nunique")
).reset_index()
monthly_summary["YearMonth"] = monthly_summary["YearMonth"].astype(str)
monthly_summary.to_csv("data/monthly_summary.csv", index=False)
print("Exported: data/monthly_summary.csv")

print("\nAll done! Check the visuals/ and data/ folders.")
