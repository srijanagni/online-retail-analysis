-- ─────────────────────────────────────────────
-- Online Retail Sales - SQL Queries
-- Database: SQLite (retail.db)
-- Run via Python: analysis.py or any SQL client
-- ─────────────────────────────────────────────


-- ── 1. Overall Summary ──
SELECT
    COUNT(DISTINCT InvoiceNo)  AS total_orders,
    COUNT(DISTINCT CustomerID) AS total_customers,
    ROUND(SUM(Revenue), 2)     AS total_revenue,
    ROUND(AVG(Revenue), 2)     AS avg_order_value
FROM retail;


-- ── 2. Monthly Revenue Trend ──
SELECT
    YearMonth,
    ROUND(SUM(Revenue), 2)    AS monthly_revenue,
    COUNT(DISTINCT InvoiceNo) AS orders
FROM retail
GROUP BY YearMonth
ORDER BY YearMonth;


-- ── 3. Monthly Revenue Growth Rate (Window Function) ──
WITH monthly AS (
    SELECT
        YearMonth,
        ROUND(SUM(Revenue), 2) AS revenue
    FROM retail
    GROUP BY YearMonth
)
SELECT
    YearMonth,
    revenue,
    LAG(revenue) OVER (ORDER BY YearMonth)                                AS prev_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY YearMonth)) * 100.0
        / LAG(revenue) OVER (ORDER BY YearMonth),
    2) AS growth_pct
FROM monthly;


-- ── 4. Top 10 Products by Revenue ──
SELECT
    Description,
    SUM(Quantity)          AS total_units_sold,
    ROUND(SUM(Revenue), 2) AS total_revenue
FROM retail
GROUP BY Description
ORDER BY total_revenue DESC
LIMIT 10;


-- ── 5. Revenue by Country ──
SELECT
    Country,
    COUNT(DISTINCT CustomerID) AS customers,
    ROUND(SUM(Revenue), 2)     AS total_revenue
FROM retail
GROUP BY Country
ORDER BY total_revenue DESC;


-- ── 6. Top 10 Customers by Revenue ──
SELECT
    CustomerID,
    COUNT(DISTINCT InvoiceNo)  AS total_orders,
    ROUND(SUM(Revenue), 2)     AS total_spent
FROM retail
GROUP BY CustomerID
ORDER BY total_spent DESC
LIMIT 10;


-- ── 7. Average Order Value by Country (Top 10) ──
SELECT
    Country,
    COUNT(DISTINCT InvoiceNo)                              AS orders,
    ROUND(SUM(Revenue) / COUNT(DISTINCT InvoiceNo), 2)    AS avg_order_value
FROM retail
GROUP BY Country
ORDER BY avg_order_value DESC
LIMIT 10;


-- ── 8. Revenue by Day of Week ──
SELECT
    DayOfWeek,
    COUNT(DISTINCT InvoiceNo)  AS orders,
    ROUND(SUM(Revenue), 2)     AS revenue
FROM retail
GROUP BY DayOfWeek
ORDER BY revenue DESC;


-- ── 9. Repeat vs One-Time Customers ──
SELECT
    CASE
        WHEN order_count = 1 THEN 'One-Time'
        ELSE 'Repeat'
    END AS customer_type,
    COUNT(*) AS customers
FROM (
    SELECT CustomerID, COUNT(DISTINCT InvoiceNo) AS order_count
    FROM retail
    GROUP BY CustomerID
) t
GROUP BY customer_type;


-- ── 10. Top 10 Products by Units Sold ──
SELECT
    Description,
    SUM(Quantity)          AS total_units_sold,
    ROUND(SUM(Revenue), 2) AS total_revenue
FROM retail
GROUP BY Description
ORDER BY total_units_sold DESC
LIMIT 10;
