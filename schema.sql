CREATE DATABASE financial_db;
USE financial_db;

CREATE TABLE accounts (
    account_id INT PRIMARY KEY AUTO_INCREMENT,
    account_name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL
);

CREATE TABLE transactions (
    txn_id INT PRIMARY KEY AUTO_INCREMENT,
    account_id INT,
    txn_date DATE,
    amount DECIMAL(10,2),
    description VARCHAR(255),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE TABLE budgets (
    budget_id INT PRIMARY KEY AUTO_INCREMENT,
    account_id INT,
    year INT,
    amount DECIMAL(10,2),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);
