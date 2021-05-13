create table scenes (
	ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	name VARCHAR(30) NOT NULL,
    user_id UUID REFERENCES user_information(ID) NOT NULL
);

create table scene_details (
	ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scene_id UUID REFERENCES scenes(ID) NOT NULL,
	light_group VARCHAR(3),
	light_group_name VARCHAR(255),
	light_brightness SMALLINT
);