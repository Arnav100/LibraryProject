CREATE DATABASE IF NOT EXISTS library;

USE library;

CREATE TABLE IF NOT EXISTS books (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    name varchar(255) NOT NULL, 
    author varchar(255) NOT NULL, 
    isbn varchar(255) NOT NULL, 
    total_copies INT NOT NULL,
    CHECK (total_copies >= 0),
    available_copies INT NOT NULL,
    CHECK (available_copies >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    name varchar(255) NOT NULL, 
    username varchar(255) NOT NULL UNIQUE,
    password varchar(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS checkouts (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    book_id INT NOT NULL, 
    FOREIGN KEY (book_id) REFERENCES books(id),
    user_id INT NOT NULL, 
    FOREIGN KEY (user_id) REFERENCES users(id),
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP NOT NULL,
    returned BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS holds (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    book_id INT REFERENCES books(id),
    user_id INT REFERENCES users(id),
    position INT NOT NULL,
    hold_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (book_id, user_id),
    UNIQUE (book_id, position)
);