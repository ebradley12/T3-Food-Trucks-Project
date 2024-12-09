
SET search_path TO ellie_bradley_schema;

-- Drop tables if they already exist
DROP TABLE IF EXISTS FACT_Transaction;
DROP TABLE IF EXISTS DIM_Truck;
DROP TABLE IF EXISTS DIM_Payment_Method;


CREATE TABLE DIM_Truck (
    truck_id SMALLINT PRIMARY KEY,
    truck_name TEXT NOT NULL,
    truck_description TEXT,
    has_card_reader BOOLEAN,
    fsa_rating SMALLINT
);

CREATE TABLE DIM_Payment_Method (
    payment_method_id SMALLINT PRIMARY KEY,
    payment_method VARCHAR(50) NOT NULL
);

CREATE TABLE FACT_Transaction (
    transaction_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    truck_id SMALLINT REFERENCES DIM_Truck(truck_id),
    payment_method_id SMALLINT REFERENCES DIM_Payment_Method(payment_method_id),
    total INT,
    at TIMESTAMP NOT NULL
);

