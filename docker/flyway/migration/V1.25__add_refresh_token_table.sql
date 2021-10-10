create table refresh_token (
    ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_information(ID) NOT NULL,
    refresh UUID NOT NULL,
    count SMALLINT NOT NULL DEFAULT 0,
    expire_time TIMESTAMP WITH TIME ZONE NOT NULL
);