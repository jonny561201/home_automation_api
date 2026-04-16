INSERT INTO user_information (first_name, last_name, email, id) VALUES
('Jon', 'Tester', 'fake1234@gmail.com', 'e97febc0-fd10-11e9-8f0b-362b9e155667'),
('Dylan', 'Tester', 'fake5678@gmail.com', 'e97febc0-fd10-11e9-8f0b-362b9e155666'),
('John', 'Tester', 'fake9012@gmail.com', 'e97febc0-fd10-11e9-8f0b-362b9e155665');

INSERT INTO user_preferences (is_fahrenheit, is_imperial, user_id, city) VALUES (TRUE, TRUE, (SELECT ID FROM user_information WHERE first_name = 'Jon'), 'Des Moines');

INSERT INTO devices (ip_address, ip_port, name, api_key, user_id, device_type_id, registered)
VALUES ('127.0.0.1', 5001, 'sump-pump', 'test-sump-api-key', 'e97febc0-fd10-11e9-8f0b-362b9e155667', (SELECT id FROM device_type WHERE type = 'sump_pump'), TRUE);

INSERT INTO daily_sump_level (distance, device_id, warning_level) VALUES (31.7, (SELECT id FROM devices WHERE name = 'sump-pump'), 3);
INSERT INTO average_daily_sump_level (distance, device_id) VALUES (33.4, (SELECT id FROM devices WHERE name = 'sump-pump'));
