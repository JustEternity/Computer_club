def get_admin():
    return "SELECT adminlogin, adminpassword, contractnumber FROM admin"

def get_client():
    return "SELECT id, surname, name,  secondname, birthdate, telephone FROM client"

def get_equipment():
    return "SELECT id, category, description, hall, price, place FROM equipment"

def get_gamesession():
    return "SELECT id, client, equipment, starttime, duration, price FROM gamesessions"

def get_hall():
    return "SELECT id, name, placecount FROM halls"

def get_loyalsystem():
    return "SELECT hourquantity, discount FROM loyalsystem"

def get_reports():
    return "SELECT idreport, name, description, request FROM reports"

def add_client(name, surname, secname, datebirth, phone):
    return f"INSERT INTO client (surname, name, secondname, birthdate, telephone) VALUES ({surname}, {name}, {secname}, {datebirth}, {phone});"

def add_equipment(category, description, hall, price, place):
    return f"INSERT INTO equipment (category, description, hall, price, place) VALUES ({category}, {description}, {hall}, {price}, {place});"

def add_gamesession(client, equipment, starttime, duration, price):
    return f"INSERT INTO gamesessions (client, equipment, starttime, duration, price) VALUES ({client}, {equipment}, {starttime}, {duration}, {price});"

def add_hall(name, placecount):
    return f"INSERT INTO halls (name, placecount) VALUES ({name}, {placecount});"

def add_loyal_settings(hourquantity, discount):
    return f"INSERT INTO loyalsystem (hourquantity, discount) VALUES ({hourquantity}, {discount});"

def del_client(id):
    return f"DELETE FROM client WHERE id = {id};"

def del_equipment(id):
    return f"DELETE FROM equipment WHERE id = {id};"

def del_gamesession(id):
    return f"DELETE FROM gamesessions WHERE id = {id};"

def del_hall(id):
    return f"DELETE FROM halls WHERE id = {id};"

def del_loyal_settings(hourquantity):
    return f"DELETE FROM loyalsystem WHERE hourquantity = {hourquantity};"