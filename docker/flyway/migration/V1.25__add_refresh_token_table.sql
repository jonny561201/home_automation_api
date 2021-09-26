create table refresh_token (
    ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    refresh UUID NOT NULL,
    count SMALLINT NOT NULL DEFAULT 0
);