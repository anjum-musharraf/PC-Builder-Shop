-- ============================================
-- PC Builder Shop - Complete Database Schema
-- ============================================

CREATE DATABASE IF NOT EXISTS pc_builder_final;
USE pc_builder_final;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table (with BDT prices, socket type for CPU/Motherboard)
CREATE TABLE IF NOT EXISTS products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(30) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    socket_type VARCHAR(20) NULL
);

-- Sample products (BDT prices, USD*122, no decimals)
INSERT INTO products (name, category, price, socket_type) VALUES
('Intel i7-13700K', 'CPU', 48798, 'LGA1700'),
('AMD Ryzen 7 7800X3D', 'CPU', 60998, 'AM5'),
('ASUS Z790', 'Motherboard', 36598, 'LGA1700'),
('MSI B650', 'Motherboard', 30498, 'AM5'),
('RTX 4060', 'GPU', 48798, NULL),
('RX 7700 XT', 'GPU', 54898, NULL),
('16GB DDR5', 'RAM', 10978, NULL),
('32GB DDR5', 'RAM', 19518, NULL),
('1TB NVMe SSD', 'Storage', 15858, NULL),
('2TB HDD', 'Storage', 9758, NULL);

-- Saved builds table (JSON parts)
CREATE TABLE IF NOT EXISTS saved_builds (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    build_name VARCHAR(100) NOT NULL,
    parts JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);