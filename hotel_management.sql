create Schema hotel_management;

USE hotel_management;

CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    room_type VARCHAR(255),
    check_in_date DATE,
    check_out_date DATE,
    num_guests INT,
    num_rooms INT,
    guest_name VARCHAR(255),
    guest_contact VARCHAR(255),
    guest_email VARCHAR(255)
);

select * from bookings;
DELETE FROM bookings;

ALTER TABLE bookings AUTO_INCREMENT = 1;

set sql_safe_updates=0;
