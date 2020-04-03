ALTER TABLE user_login DROP CONSTRAINT roles_fk;
ALTER TABLE user_login DROP COLUMN role_id;

ALTER TABLE user_roles rename TO roles;

CREATE TABLE user_roles(
	    ID UUID PRIMARY KEY DEFAULT gen_random_uuid()
);

ALTER TABLE user_roles
    ADD COLUMN role_id UUID NOT NULL;

ALTER TABLE user_roles
    ADD COLUMN user_id UUID NOT NULL;

ALTER TABLE user_roles
    ADD CONSTRAINT roles_fk FOREIGN KEY (role_id) REFERENCES roles(ID);

ALTER TABLE user_roles
    ADD CONSTRAINT user_fk FOREIGN KEY (user_id) REFERENCES user_information(ID);

INSERT INTO roles (role_name, role_desc) VALUES
('lighting', 'access to the lighting functionality');