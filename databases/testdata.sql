USE `python_check`;
INSERT INTO exercise(id, name, text, language, preset) VALUES (5, 'Kreisberechnung', 'Schreibe Funktionen um den Umfang und die Fläche anhand eines Radiuses zu berechnen. Verwende dazu die pi Variable.', 1, 'pi = 3.1415926

def umfang(radius):


def flaeche(radius):
');
INSERT INTO exercise(id, name, text, language, preset) VALUES (6, 'Quadratberechnung', 'Schreibe eine Funktion, die den Umfang, die Fläche und die Länge der Diagonalen des Quadrats berechnet und (in dieser Reihenfolge) in einem Array zurückgibt.', 1, 'from math import sqrt

def quadratberechnung(a):');
INSERT INTO exercise(id, name, text, language, preset) VALUES (7, 'Rechteckberechnung', 'Schreibe eine Funktion, die den Umfang, die Fläche und die Länge der Diagonalen des Rechtecks berechnet und (in dieser Reihenfolge) in einem Array zurückgibt.', 1, 'from math import sqrt

def rechteckberechnung(a, b):
');
INSERT INTO exercise(id, name, text, language, preset) VALUES (8, 'Benzinverbrauch', 'Wenn ein Fahrzeugbesitzer von einem Tankstopp zum Nächsten ermittelt, wie viele Kilometer er gefahren ist und wie viele Liter Treibstoff dafür verbraucht wurden, kann ermittelt werden, welchen Verbrauch das Fahrzeug pro 100 km hat.

Schreibe eine Funktion, die den Benzinverbrauch eines Autos auf 100km berechnet.', 1, 'def benzinverbrauch(gefahrene_kilometer, getankte_liter):
');
INSERT INTO points(id, number_of_points, exercise) VALUES (12, '50', 5);
INSERT INTO points(id, number_of_points, exercise) VALUES (13, '50', 5);
INSERT INTO points(id, number_of_points, exercise) VALUES (14, '50', 6);
INSERT INTO points(id, number_of_points, exercise) VALUES (15, '50', 7);
INSERT INTO points(id, number_of_points, exercise) VALUES (16, '30', 7);
INSERT INTO points(id, number_of_points, exercise) VALUES (17, '50', 8);
INSERT INTO points(id, number_of_points, exercise) VALUES (18, '10', 8);
INSERT INTO points(id, number_of_points, exercise) VALUES (19, '10', 8);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (11, 'umfang', '31.415926', '5', 12);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (12, 'umfang', '955.0441504', '152', 12);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (13, 'umfang', '63427095.8331072', '10094736', 12);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (14, 'flaeche', '3.1415926', '1', 13);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (15, 'flaeche', '530.9291494', '13', 13);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (16, 'flaeche', '115811.6696064', '192', 13);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (19, 'quadratberechnung', '[4, 1, 1.4142135623730951]', '1', 14);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (20, 'quadratberechnung', '[21.2, 28.09, 7.495331880577404]', '5.3', 14);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (21, 'quadratberechnung', '[392, 9604, 138.59292911256333]', '98', 14);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (22, 'rechteckberechnung', '[22, 50, 11.180339887498949]', '5, 10', 15);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (23, 'rechteckberechnung', '[22, 50, 11.180339887498949]', '10, 5', 15);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (24, 'rechteckberechnung', '[2, 0, 883.0]', '883, 0', 15);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (25, 'rechteckberechnung', '[1782, 409.40000000000003, 890.0001188763965]', '.46, 890', 16);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (26, 'benzinverbrauch', '50', '100, 50', 17);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (27, 'benzinverbrauch', '75', '30, 25', 18);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (28, 'benzinverbrauch', '1049.15036333147', '89.45, 938.465', 19);
INSERT INTO assertion(id, function_name, expected_result, arguments, points) VALUES (29, 'benzinverbrauch', '27.398600185099493', '345.76, 94.73340', 19);
INSERT INTO auth_user(id, first_name, last_name, email, password, registration_key, reset_password_key, registration_id) VALUES (1, 'Jonas', 'Keisel', 'jonas.keisel@gmail.com', 'pbkdf2(1000,20,sha512)$b0a7a0a33a1aa602$742d3c5083de8ad98c16510104d13028b2462dc3', '', '', '');
INSERT INTO auth_user(id, first_name, last_name, email, password, registration_key, reset_password_key, registration_id) VALUES (5, 'Daniel', 'Laxar', 'i.dlaxar@gmail.com', 'pbkdf2(1000,20,sha512)$8bc13de16e4d0d50$09901f23365bc0c22354d461eb10a8792b498415', '', '', '');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (4, '2012-11-26 13:08:57', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (5, '2012-11-26 17:05:41', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (6, '2012-11-26 18:26:44', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (8, '2012-12-02 17:32:48', '127.0.0.1', 1, 'auth', 'User 1 Logged-out');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (9, '2012-12-02 17:32:58', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (10, '2012-12-02 17:33:16', '127.0.0.1', 1, 'auth', 'User 1 Logged-out');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (13, '2012-12-02 17:33:43', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (14, '2012-12-03 10:46:47', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (15, '2012-12-03 17:34:41', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (16, '2012-12-07 17:46:26', '127.0.0.1', 1, 'auth', 'User 1 Logged-out');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (17, '2012-12-07 17:46:33', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (18, '2012-12-07 17:46:47', '127.0.0.1', 1, 'auth', 'User 1 Logged-out');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (19, '2012-12-07 17:46:53', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (20, '2012-12-07 21:54:21', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (21, '2012-12-07 21:55:00', '127.0.0.1', 1, 'auth', 'User 1 Logged-out');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (22, '2012-12-07 21:55:45', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (23, '2012-12-07 21:56:03', '127.0.0.1', 1, 'auth', 'User 1 Logged-out');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (24, '2012-12-07 21:57:12', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (25, '2012-12-07 22:03:02', '127.0.0.1', 1, 'auth', 'User 1 Logged-out');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (26, '2012-12-07 22:03:06', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (27, '2012-12-07 23:25:11', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (28, '2012-12-08 19:35:03', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (29, '2012-12-09 16:29:24', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (33, '2012-12-09 22:29:52', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (34, '2012-12-10 10:55:26', '127.0.0.1', 1, 'auth', 'User 1 Logged-out');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (35, '2012-12-10 10:55:32', '127.0.0.1', 1, 'auth', 'User 1 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (37, '2012-12-11 10:59:43', '192.168.71.1', 5, 'auth', 'User 5 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (38, '2012-12-11 12:56:24', '192.168.71.1', 5, 'auth', 'User 5 Logged-in');
INSERT INTO auth_event(id, time_stamp, client_ip, user_id, origin, description) VALUES (39, '2012-12-16 11:33:21', '192.168.71.1', 5, 'auth', 'User 5 Logged-in');
INSERT INTO auth_membership(id, user_id, group_id) VALUES (1, 1, 3);
INSERT INTO auth_membership(id, user_id, group_id) VALUES (5, 5, 3);

INSERT INTO course(id, name, teacher) VALUES (4, '2012/13 SEW 1BI', 1);
INSERT INTO course_exercise(id, exercise, course, start_date, end_date) VALUES (4, 5, 4, '2012-12-10 11:18:18', '2012-12-31 11:18:21');
INSERT INTO course_exercise(id, exercise, course, start_date, end_date) VALUES (5, 6, 4, '2012-12-10 11:18:26', '2012-12-31 11:18:29');
INSERT INTO enrollment(id, course, student) VALUES (13, 4, 5);
COMMIT;