CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    department VARCHAR(50)
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    budget NUMERIC,
    status VARCHAR(20)
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(100),
    contact_email VARCHAR(100)
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    customer_id INT,
    amount NUMERIC,
    transaction_date DATE
);

INSERT INTO employees (first_name, last_name, email, department) VALUES
('John', 'Doe', 'j.doe@example.com', 'Engineering'),
('Jane', 'Smith', 'j.smith@example.com', 'Marketing'),
('Alice', 'Johnson', 'a.johnson@example.com', 'Sales');

INSERT INTO projects (name, budget, status) VALUES
('Project Alpha', 100000.00, 'In Progress'),
('Project Beta', 50000.00, 'Planning');

INSERT INTO customers (company_name, contact_email) VALUES
('Tech Corp', 'contact@techcorp.example.com'),
('Global Industries', 'info@global.example.com');

INSERT INTO transactions (customer_id, amount, transaction_date) VALUES
(1, 1500.00, '2023-01-15'),
(2, 3200.50, '2023-02-20');
