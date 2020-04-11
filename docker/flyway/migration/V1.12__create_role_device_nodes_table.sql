create table role_devices (
	ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	ip_address INET NOT NULL,
	max_nodes SMALLINT DEFAULT 1,
	user_role_id UUID REFERENCES user_roles(ID) NOT NULL
);

create table role_device_nodes (
	ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	node_name VARCHAR(50) NOT NULL,
	node_device SMALLINT NOT NULL,
	role_device_id UUID REFERENCES role_devices(ID) NOT NULL
);