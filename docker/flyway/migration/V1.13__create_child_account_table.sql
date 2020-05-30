create table child_accounts (
	ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	child_user_id UUID REFERENCES user_information(ID) NOT null,
	parent_user_id UUID REFERENCES user_information(ID) NOT NULL
);