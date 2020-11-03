ALTER TABLE user_preferences ADD COLUMN alarm_light_group VARCHAR(3);
ALTER TABLE user_preferences ADD COLUMN alarm_time TIME;
ALTER TABLE user_preferences ADD COLUMN alarm_days VARCHAR(21);
ALTER TABLE user_preferences ADD COLUMN alarm_group_name VARCHAR(255);