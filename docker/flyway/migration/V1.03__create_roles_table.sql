CREATE TABLE user_roles (
    ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name VARCHAR(50) NOT NULL,
    role_desc VARCHAR(255) NOT NULL
);

INSERT INTO user_roles (role_name, role_desc) VALUES
('garage_door', 'access to the garage door functionality'),
('thermostat', 'access to the thermostat functionality'),
('sump_pump', 'access to the sump pump functionality'),
('security', 'access to the security functionality');