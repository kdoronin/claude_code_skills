# SQL Query Patterns

Common patterns for translating natural language to SQL.

## Counting & Aggregation

**"How many X?"** / **"Count of X"**
```sql
SELECT COUNT(*) as total FROM table_name;
SELECT COUNT(DISTINCT column) as unique_count FROM table_name;
```

**"Total/Sum of X"**
```sql
SELECT SUM(amount) as total FROM table_name;
```

**"Average X"**
```sql
SELECT AVG(value) as average FROM table_name;
```

## Grouping

**"X by Y"** / **"X per Y"**
```sql
SELECT category, COUNT(*) as count
FROM table_name
GROUP BY category
ORDER BY count DESC;
```

**"Revenue by month"**
```sql
SELECT
    strftime('%Y-%m', date_column) as month,  -- SQLite
    -- DATE_FORMAT(date_column, '%Y-%m') as month,  -- MySQL
    SUM(amount) as revenue
FROM orders
GROUP BY month
ORDER BY month;
```

## Filtering

**"X where Y"** / **"X with Y"**
```sql
SELECT * FROM table_name WHERE column = 'value';
SELECT * FROM table_name WHERE column IN ('val1', 'val2');
SELECT * FROM table_name WHERE column LIKE '%pattern%';
```

**Date filtering**
```sql
-- Specific date range
WHERE date_column >= '2024-01-01' AND date_column < '2024-02-01'

-- Last N days (SQLite)
WHERE date_column >= date('now', '-30 days')

-- Last N days (MySQL)
WHERE date_column >= DATE_SUB(NOW(), INTERVAL 30 DAY)
```

## Top-N Queries

**"Top N X"** / **"Best X"**
```sql
SELECT * FROM table_name
ORDER BY metric DESC
LIMIT 10;
```

**"Top N X by Y"**
```sql
SELECT category, SUM(amount) as total
FROM table_name
GROUP BY category
ORDER BY total DESC
LIMIT 10;
```

## Joins

**Joining related tables**
```sql
SELECT o.*, c.customer_name
FROM orders o
JOIN customers c ON o.customer_id = c.id;
```

**Left join (include all from first table)**
```sql
SELECT c.*, COUNT(o.id) as order_count
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id;
```

## Common Transformations

**Percentage**
```sql
SELECT
    category,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
FROM table_name
GROUP BY category;
```

**Running total (SQLite/modern SQL)**
```sql
SELECT
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) as running_total
FROM transactions;
```

## NULL Handling

```sql
-- Filter out nulls
WHERE column IS NOT NULL

-- Replace nulls
COALESCE(column, 'default_value')
IFNULL(column, 0)  -- SQLite/MySQL
```
