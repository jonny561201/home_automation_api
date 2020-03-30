CREATE TABLE user_preferences (
    ID SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    is_fahrenheit boolean NOT NULL
);

ALTER TABLE user_preferences
    ADD CONSTRAINT user_fk FOREIGN KEY (user_id) REFERENCES user_information(ID);