create table scene_details (
	ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	light_group VARCHAR(3),
	light_group_name VARCHAR(255),
	light_brightness SMALLINT
);

create table scenes (
	ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	name VARCHAR(30),
	detail_id UUID REFERENCES scene_details(ID) NOT NULL
);