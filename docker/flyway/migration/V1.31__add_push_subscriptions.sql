create table push_subscriptions (
	ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID REFERENCES user_information(ID) NOT NULL,
	endpoint TEXT NOT NULL UNIQUE,
	p256dh_key TEXT NOT NULL,
	auth_key TEXT NOT NULL
);
