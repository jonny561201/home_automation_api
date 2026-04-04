INSERT INTO devices (user_id, device_type_id, ip_address, ip_port, node_name, node_device) VALUES
    ((SELECT ID FROM user_information WHERE first_name = 'Jon'), (SELECT ID FROM device_type WHERE type = 'garage_door'), '127.0.0.1', 5001, 'Jon''s Door', 1);
