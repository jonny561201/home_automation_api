CREATE TABLE scheduled_task_types (
    ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_name VARCHAR(25) NOT NULL,
    activity_desc VARCHAR(255)
);

INSERT INTO scheduled_task_types (activity_name, activity_desc) VALUES
('sunrise alarm', 'gradually turn on lights over a scheduled period'),
('turn on', 'turn on lights at a scheduled time'),
('turn off', 'turn off lights at a scheduled time');

ALTER TABLE schedule_tasks ADD COLUMN enabled boolean NOT NULL;
ALTER TABLE schedule_tasks ADD COLUMN task_type_id UUID NOT NULL;

ALTER TABLE schedule_tasks
    ADD CONSTRAINT scheduled_task_types_fk FOREIGN KEY (task_type_id) REFERENCES scheduled_task_types(ID);

