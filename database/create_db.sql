CREATE DATABASE IF NOT EXISTS library;

USE library;

-- ----------------------------
-- Users Table
-- ----------------------------

CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL, 
    username varchar(255) NOT NULL UNIQUE,
    password varchar(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------
-- Books Table
-- ----------------------------

CREATE TABLE IF NOT EXISTS books (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL, 
    author VARCHAR(255),
    isbn VARCHAR(255) UNIQUE,
    price_cents INT NOT NULL,
    purchased_at TIMESTAMP NULL,
    cover_url VARCHAR(255), 
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------
-- Gifts
-- ----------------------------

CREATE TABLE IF NOT EXISTS gifts (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,                          -- recipient
    book_id INT NOT NULL,
    purchased_by VARCHAR(255) DEFAULT 'arnav',
    note TEXT,
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

-- ----------------------------
-- Wishlists
-- ----------------------------

CREATE TABLE IF NOT EXISTS wishlists (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    shop_url VARCHAR(255) NOT NULL,
    price_cents INT NOT NULL,
    note TEXT,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fulfilled BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
