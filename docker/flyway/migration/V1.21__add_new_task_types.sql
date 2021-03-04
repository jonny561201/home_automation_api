INSERT INTO scheduled_task_types (activity_name, activity_desc) VALUES
('hvac', 'turn on/off the hvac system at scheduled times');

ALTER TABLE schedule_tasks ADD COLUMN hvac_start TIME;
ALTER TABLE schedule_tasks ADD COLUMN hvac_stop TIME;
ALTER TABLE schedule_tasks ADD COLUMN hvac_mode VARCHAR(4);