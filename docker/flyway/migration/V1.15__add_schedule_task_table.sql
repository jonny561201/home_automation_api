ALTER TABLE user_preferences DROP COLUMN alarm_light_group;
ALTER TABLE user_preferences DROP COLUMN alarm_time;
ALTER TABLE user_preferences DROP COLUMN alarm_days;
ALTER TABLE user_preferences DROP COLUMN alarm_group_name;

create table schedule_tasks (
	ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID REFERENCES user_information(ID) NOT NULL,
	alarm_light_group VARCHAR(3),
	alarm_group_name VARCHAR(255),
	alarm_time TIME,
	alarm_days VARCHAR(21)
);
