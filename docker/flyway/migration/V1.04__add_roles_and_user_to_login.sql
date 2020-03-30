ALTER TABLE user_login
    ADD COLUMN user_id UUID NOT NULL;

ALTER TABLE user_login
    ADD COLUMN role_id UUID NOT NULL;

ALTER TABLE user_login
    ADD CONSTRAINT user_fk FOREIGN KEY (user_id) REFERENCES user_information(ID);

ALTER TABLE user_login
    ADD CONSTRAINT roles_fk FOREIGN KEY (role_id) REFERENCES user_roles(ID)