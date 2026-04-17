DROP TABLE refresh_token;
DROP TABLE user_login;

ALTER TABLE daily_sump_level ADD COLUMN device_id UUID REFERENCES devices(ID);
ALTER TABLE average_daily_sump_level ADD COLUMN device_id UUID REFERENCES devices(ID);

UPDATE daily_sump_level dsl
SET device_id = d.id
FROM devices d
JOIN device_type dt ON d.device_type_id = dt.id
WHERE dt.type = 'sump_pump' AND d.user_id = dsl.user_id;

UPDATE average_daily_sump_level adsl
SET device_id = d.id
FROM devices d
JOIN device_type dt ON d.device_type_id = dt.id
WHERE dt.type = 'sump_pump' AND d.user_id = adsl.user_id;

DELETE FROM daily_sump_level WHERE device_id IS NULL;
DELETE FROM average_daily_sump_level WHERE device_id IS NULL;

ALTER TABLE daily_sump_level ALTER COLUMN device_id SET NOT NULL;
ALTER TABLE average_daily_sump_level ALTER COLUMN device_id SET NOT NULL;

ALTER TABLE daily_sump_level DROP COLUMN user_id;
ALTER TABLE average_daily_sump_level DROP COLUMN user_id;

ALTER TABLE user_preferences RENAME COLUMN preferred_garage_node_id TO garage_node_id;
