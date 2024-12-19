def get_admin():
    return "SELECT adminlogin, adminpassword, contractnumber FROM admin"

def get_client():
    return "SELECT id, surname, name,  secondname, birthdate, telephone FROM client"

def get_equipment():
    return "SELECT id, category, description, hall, price, place FROM equipment"

def get_gamesession():
    return "SELECT id, client, equipment, starttime, duration, price, completed FROM gamesessions;"

def get_hall():
    return "SELECT id, name, placecount FROM halls"

def get_loyalsystem():
    return "SELECT hourquantity, discount FROM loyalsystem"

def get_reports():
    return "SELECT id, name, description, request FROM reports"

def add_client(name, surname, secname, datebirth, phone):
    return f"INSERT INTO client (surname, name, secondname, birthdate, telephone) VALUES ('{surname}', '{name}', '{secname}', '{datebirth}', '{phone}');"

def add_equipment(category, description, hall, price, place):
    return f"INSERT INTO equipment (category, description, hall, price, place) VALUES ('{category}', '{description}', '{hall}', '{price}', '{place}');"

def add_gamesession(client, equipment, starttime, duration, price):
    return f"INSERT INTO gamesessions (client, equipment, starttime, duration, price, completed) VALUES ('{client}', '{equipment}', '{starttime}', '{duration}', '{price}', '0');"

def add_hall(name, placecount):
    return f"INSERT INTO halls (name, placecount) VALUES ('{name}', '{placecount}');"

def add_loyal_settings(hourquantity, discount):
    return f"INSERT INTO loyalsystem (hourquantity, discount) VALUES ('{hourquantity}', '{discount}');"

def del_client(id):
    return f"DELETE FROM client WHERE id = '{id}';"

def del_equipment(id):
    return f"DELETE FROM equipment WHERE id = '{id}';"

def del_gamesession(id):
    return f"DELETE FROM gamesessions WHERE id = '{id}';"

def stop_gamesession(id):
    return f"UPDATE gamesessions SET completed = '1' WHERE id = '{id}'"

def del_hall(id):
    return f"DELETE FROM halls WHERE id = '{id}';"

def del_loyal_settings(hourquantity):
    return f"DELETE FROM loyalsystem WHERE hourquantity = '{hourquantity}';"

def update_client(id, surname, name, secname, dbirth, tel):
    return f"UPDATE client SET surname = '{surname}', name = '{name}', secondname = '{secname}', birthdate = '{dbirth}', telephone = '{tel}' WHERE id = '{id}';"

def update_hall(id, name, placecount):
    return f"UPDATE halls SET name = '{name}', placecount = '{placecount}' WHERE id = '{id}';"

def update_equip(id, category, descriprion, hall, price, place):
    return f"UPDATE equipment SET category = '{category}', description = '{descriprion}', hall = '{hall}', price = '{price}', place = '{place}' WHERE id = '{id}';"

def update_gamesession(id, client, equipment, starttime, duration, price):
    return f"UPDATE gamesessions SET client = '{client}', equipment = '{equipment}', starttime = '{starttime}', duration = '{duration}', price = '{price}' WHERE id = '{id}';"

def get_client_hours(id):
    return f"SELECT SEC_TO_TIME(SUM(TIME_TO_SEC(duration))) FROM gamesessions WHERE id > '{id}';"