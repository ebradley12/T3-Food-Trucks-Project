SET search_path TO ellie_bradley_schema;

-- Insert static data into DIM_Truck
INSERT INTO DIM_Truck (truck_id, truck_name, truck_description, has_card_reader, fsa_rating) VALUES
    (1, 'Burrito Madness', 'An authentic taste of Mexico.', TRUE, 4),
    (2, 'Kings of Kebabs', 'Locally-sourced meat cooked over a charcoal grill.', TRUE, 2),
    (3, 'Cupcakes by Michelle', 'Handcrafted cupcakes made with high-quality, organic ingredients.', TRUE, 5),
    (4, 'Hartmann\'s Jellied Eels', 'A taste of history with this classic English dish.', TRUE, 4),
    (5, 'Yoghurt Heaven', 'All the great tastes, but only some of the calories!', TRUE, 4),
    (6, 'SuperSmoothie', 'Pick any fruit or vegetable, and we\'ll make you a delicious, healthy, multi-vitamin shake.', FALSE, 3);

-- Insert static data into DIM_Payment_Method
INSERT INTO DIM_Payment_Method (payment_method_id, payment_method) VALUES
    (1, 'cash'),
    (2, 'card');