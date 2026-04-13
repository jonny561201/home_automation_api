create table device_type (
    ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(255) NOT NULL,
    auth0_role_id VARCHAR(255)
);

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
    user_id UUID REFERENCES user_information(ID),
    device_type_id UUID NOT NULL REFERENCES device_type(ID),
    ip_address INET NOT NULL,
    ip_port INTEGER CHECK (ip_port BETWEEN 1 AND 65535),
    api_key VARCHAR(64) NOT NULL,
    name VARCHAR(50) NOT NULL,
    max_nodes SMALLINT NOT NULL DEFAULT 1,
    registered BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE device_nodes (
    ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES devices(ID),
    node_device SMALLINT NOT NULL,
    node_name VARCHAR(50) NOT NULL
);

CREATE TABLE user_devices (
    ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_information(ID),
    device_id UUID NOT NULL REFERENCES devices(ID)
);
