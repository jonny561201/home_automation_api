CREATE TABLE daily_sump_level (
    ID SERIAL PRIMARY KEY,
    user_id UUID REFERENCES user_information(ID) NOT NULL,
    distance DOUBLE PRECISION NOT NULL,
    create_date TIMESTAMP NOT NULL
);

CREATE TABLE average_daily_sump_level (
    ID SERIAL PRIMARY KEY,
    user_id UUID REFERENCES user_information(ID) NOT NULL,
    distance DOUBLE PRECISION NOT NULL,
    create_day DATE NOT NULL
);