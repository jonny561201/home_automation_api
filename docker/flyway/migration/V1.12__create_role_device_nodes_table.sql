create table role_devices (
	ID UUID primary key default gen_random_uuid(),
	ip_address INET not NULL,
	max_nodes smallint default 1
);

create table role_device_nodes (
	ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	node_name VARCHAR(50) not NULL,
	node_device smallserial,
	role_device_id UUID references role_devices(ID) not NULL
);