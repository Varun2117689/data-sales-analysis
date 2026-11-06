CREATE DATABASE IF NOT EXISTS sales_analysis CHARACTER SET utf8mb4;
USE sales_analysis;

CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL DEFAULT 'Uncategorized'
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    sale_date DATE NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    region VARCHAR(100) NOT NULL DEFAULT 'Unknown',
    sale_hash CHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sales_product FOREIGN KEY (product_id) REFERENCES products(product_id)
);
