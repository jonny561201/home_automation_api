INSERT INTO user_information (first_name, last_name, email, id) VALUES
('Jon', 'Tester', 'fake1234@gmail.com', 'e97febc0-fd10-11e9-8f0b-362b9e155667');

INSERT INTO user_login (user_name, password, user_id) VALUES
('Jonny561201', 'password', (SELECT ID FROM user_information WHERE first_name = 'Jon')),
('l33t', 'password1', (SELECT ID FROM user_information WHERE first_name = 'Jon')),
('dingDongFoo', 'obviouslyPassword1', (SELECT ID FROM user_information WHERE first_name = 'Jon'));

INSERT INTO user_roles (user_id, role_id) VALUES
((SELECT ID FROM user_information WHERE first_name = 'Jon'), (SELECT ID FROM roles WHERE role_name = 'garage_door')),
((SELECT ID FROM user_information WHERE first_name = 'Jon'), (SELECT ID FROM roles WHERE role_name = 'security')),
((SELECT ID FROM user_information WHERE first_name = 'Jon'), (SELECT ID FROM roles WHERE role_name = 'thermostat')),
((SELECT ID FROM user_information WHERE first_name = 'Jon'), (SELECT ID FROM roles WHERE role_name = 'lighting')),
((SELECT ID FROM user_information WHERE first_name = 'Jon'), (SELECT ID FROM roles WHERE role_name = 'sump_pump'));

INSERT INTO user_preferences (is_fahrenheit, is_imperial, user_id, city) VALUES (TRUE, TRUE, (SELECT ID FROM user_information WHERE last_name = 'Tester'), 'Des Moines');

INSERT INTO daily_sump_level (distance, user_id, warning_level) VALUES (31.7, 'e97febc0-fd10-11e9-8f0b-362b9e155667', 3);
INSERT INTO average_daily_sump_level (distance, user_id) VALUES (33.4, 'e97febc0-fd10-11e9-8f0b-362b9e155667');