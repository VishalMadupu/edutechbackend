-- Initial SuperAdmin Creation Script
-- Note: The hashed_password below is 'admin123' (Argon2 hashed)
-- You can use this script to manually seed the database if needed.

INSERT INTO superadmins (username, email, hashed_password, is_active) 
VALUES (
    'admin', 
    'admin@edtech.com', 
    '$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc', 
    1
);
