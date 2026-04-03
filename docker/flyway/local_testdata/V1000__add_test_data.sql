INSERT INTO user_information (first_name, last_name, email, id) VALUES
('Jon', 'Tester', 'fake1234@gmail.com', 'e97febc0-fd10-11e9-8f0b-362b9e155667'),
('Dylan', 'Tester', 'fake5678@gmail.com', 'e97febc0-fd10-11e9-8f0b-362b9e155666'),
('John', 'Tester', 'fake9012@gmail.com', 'e97febc0-fd10-11e9-8f0b-362b9e155665');

INSERT INTO user_preferences (is_fahrenheit, is_imperial, user_id, city) VALUES (TRUE, TRUE, (SELECT ID FROM user_information WHERE first_name = 'Jon'), 'Des Moines');

INSERT INTO daily_sump_level (distance, user_id, warning_level) VALUES (31.7, 'e97febc0-fd10-11e9-8f0b-362b9e155667', 3);
INSERT INTO average_daily_sump_level (distance, user_id) VALUES (33.4, 'e97febc0-fd10-11e9-8f0b-362b9e155667');