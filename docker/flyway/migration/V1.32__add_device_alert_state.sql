CREATE TABLE device_alert_state (
    ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES devices(ID) NOT NULL,
    alert_key VARCHAR(255) NOT NULL,
    last_notified TEXT NOT NULL,
    UNIQUE (device_id, alert_key)
);
