
DROP TABLE IF EXISTS `New`;


CREATE TABLE IF NOT EXISTS `products` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);


INSERT INTO products (name, category, price) VALUES
('Intel Core i7-13700K', 'CPU', 60999),
('NVIDIA GeForce RTX 4080', 'GPU', 182999),
('Corsair Vengeance DDR4 32GB', 'RAM', 19519),
('ASUS ROG Strix X670E', 'Motherboard', 48799),
('Samsung 980 Pro 2TB NVMe SSD', 'Storage', 36599);
