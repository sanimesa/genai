CREATE TABLE `bigquery-public-data.thelook_ecommerce.users`
(
  id INT64,
  first_name STRING,
  last_name STRING,
  email STRING,
  age INT64,
  gender STRING,
  state STRING,
  street_address STRING,
  postal_code STRING,
  city STRING,
  country STRING,
  latitude FLOAT64,
  longitude FLOAT64,
  traffic_source STRING,
  created_at TIMESTAMP
);

CREATE TABLE `bigquery-public-data.thelook_ecommerce.order_items`
(
  id INT64,
  order_id INT64,
  user_id INT64,
  product_id INT64,
  inventory_item_id INT64,
  status STRING,
  created_at TIMESTAMP,
  shipped_at TIMESTAMP,
  delivered_at TIMESTAMP,
  returned_at TIMESTAMP,
  sale_price FLOAT64
);

CREATE TABLE `bigquery-public-data.thelook_ecommerce.products`
(
  id INT64,
  cost FLOAT64,
  category STRING,
  name STRING,
  brand STRING,
  retail_price FLOAT64,
  department STRING,
  sku STRING,
  distribution_center_id INT64
);

CREATE TABLE `bigquery-public-data.thelook_ecommerce.orders`
(
  order_id INT64,
  user_id INT64,
  status STRING,
  gender STRING,
  created_at TIMESTAMP,
  returned_at TIMESTAMP,
  shipped_at TIMESTAMP,
  delivered_at TIMESTAMP,
  num_of_item INT64
);


CREATE TABLE `bigquery-public-data.thelook_ecommerce.distribution_centers`
(
  id INT64,
  name STRING,
  latitude FLOAT64,
  longitude FLOAT64
);

CREATE TABLE `bigquery-public-data.thelook_ecommerce.inventory_items`
(
  id INT64,
  product_id INT64,
  created_at TIMESTAMP,
  sold_at TIMESTAMP,
  cost FLOAT64,
  product_category STRING,
  product_name STRING,
  product_brand STRING,
  product_retail_price FLOAT64,
  product_department STRING,
  product_sku STRING,
  product_distribution_center_id INT64
);

CREATE TABLE `bigquery-public-data.thelook_ecommerce.events`
(
  id INT64,
  user_id INT64,
  sequence_number INT64,
  session_id STRING,
  created_at TIMESTAMP,
  ip_address STRING,
  city STRING,
  state STRING,
  postal_code STRING,
  browser STRING,
  traffic_source STRING,
  uri STRING,
  event_type STRING
);