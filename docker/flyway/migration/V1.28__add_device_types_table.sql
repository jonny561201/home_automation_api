create table device_type (
    ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(255) NOT NULL,
    auth0_role_id VARCHAR(255)
);_

INSERT INTO device_type (type, auth0_role_id) VALUES
   ('garage_door', 'rol_3x7V3WC9NOQrFGtA'),
   ('thermostat', 'rol_4zQ1dypKB4M5RklD'),
   ('security_system', 'rol_OwZ41BzZImZyd2Et'),
   ('lighting', 'rol_CQ5MOVNScenDWSAj'),
   ('sump_pump', 'rol_nuC1Ik6zxjcWRFZn');

DROP TABLE role_device_nodes;
DROP TABLE role_devices;
DROP TABLE user_roles;
DROP TABLE roles;

CREATE TABLE devices (
    ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_information(ID),
    device_type_id UUID NOT NULL REFERENCES device_type(ID),
    ip_address INET NOT NULL,
    ip_port INTEGER CHECK (ip_port BETWEEN 1 AND 65535),
    node_name VARCHAR(50) NOT NULL,
    node_device SMALLINT,
    registered BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE user_devices (
    ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_information(ID),
    device_id UUID NOT NULL REFERENCES devices(ID)
);
