INSERT INTO role_devices (ip_address, ip_port, max_nodes, user_role_id)
VALUES ('127.0.0.1', 5001, 1, (SELECT ur.id
                              FROM user_roles ur
                                       JOIN user_information ui on ui.id = ur.user_id
                                       JOIN roles r ON r.id = ur.role_id
                              WHERE ui.first_name = 'Jon'
                                AND r.role_name = 'garage_door'));

INSERT INTO role_device_nodes (node_name, node_device, role_device_id) VALUES ('garage door ip', 1, (SELECT id FROM role_devices WHERE ip_address = '127.0.0.1'));
