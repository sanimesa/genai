User: Best Selling Item?
Assistant:
SELECT oi.product_id as product_id, p.name as product_name, p.category as product_category, count(*) as num_of_orders
FROM `bigquery-public-data.thelook_ecommerce.products` as p 
JOIN `bigquery-public-data.thelook_ecommerce.order_items` as oi
ON p.id = oi.product_id
GROUP BY 1,2,3
ORDER BY num_of_orders DESC;

User: Top 10 Customers by Average Order Price?
Assistant: SELECT u.id as user_id, u.first_name, u.last_name, avg(oi.sale_price) as avg_sale_price
FROM `bigquery-public-data.thelook_ecommerce.users` as u 
JOIN `bigquery-public-data.thelook_ecommerce.order_items` as oi
ON u.id = oi.user_id
GROUP BY 1,2,3
ORDER BY avg_sale_price DESC
LIMIT 10;