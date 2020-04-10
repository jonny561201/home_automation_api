create table role_devices (
	ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	ip_address INET NOT NULL,
	max_nodes SMALLINT DEFAULT 1
);

create table role_device_nodes (
	ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	node_name VARCHAR(50) NOT NULL,
	node_device SMALLINT,
	role_device_id UUID REFERENCES role_devices(ID) NOT NULL
);