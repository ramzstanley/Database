import sqlite3
import csv

database:str = "crud.db"

def connect():
    return sqlite3.connect(database)

def getprocess(sql:str)->list:
    conn = connect()
    conn.row_factory = sqlite3.Row #return dictionary format
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    return rows
	
def generateCustomer(table)->list:
	conn = connect()
	conn.row_factory = sqlite3.Row
	cursor = conn.cursor()
	data = cursor.execute(f"SELECT c_name, c_email, c_address, username FROM {table}")
	
	with open('CustomerList.csv', 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(['c_name', 'c_email', 'c_address', 'username'])
		writer.writerows(data)
		
def generateSales():
	conn = connect()
	conn.row_factory = sqlite3.Row
	cursor = conn.cursor()
	data = cursor.execute(f"""
        SELECT c.c_name, c.c_email, c.c_address, o.o_id, o.o_date, 
               i.title, io.qty, i.price, (io.qty * i.price) AS total
        FROM Customer c
        JOIN Orders o ON c.c_id = o.c_id
        JOIN ItemsOrdered io ON o.o_id = io.o_id
        JOIN Items i ON io.i_id = i.i_id
    """)
	
	with open('CustomerOrderItemReport.csv', 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(['c_name', 'c_email', 'c_address', 'order_id', 'order_date', 
                         'item_name', 'quantity', 'price', 'total'])
		writer.writerows(data)

def doprocess(sql:str)->bool:    
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    return True if cursor.rowcount>0 else False

def getall(table)->list:
    sql:str = f"SELECT * FROM `{table}`"
    return getprocess(sql)

def addrecord(table:str,**kwargs)->bool:
    keys:list = list(kwargs.keys())
    vals:list = list(kwargs.values())
    flds:str = "`,`".join(keys)
    data:str = "','".join(vals)
    sql:str = f"INSERT INTO `{table}`(`{flds}`) VALUES ('{data}')"
    return doprocess(sql)

def updaterecord(table:str,**kwargs)->bool:
    keys:list = list(kwargs.keys())
    vals:list = list(kwargs.values())
    temp = []

    for key,value in kwargs.items():
    	if key != keys[0] and value != vals[0]:
	    	kv = f"`{key}` = '{value}'"
	    	temp.append(kv)

    key_val = ",".join(temp)
    sql:str = f"UPDATE `{table}` SET {key_val} WHERE `{keys[0]}` = '{vals[0]}'"
    return doprocess(sql)
    
def deleterecord(table:str,**kwargs)->bool:
    keys:list = list(kwargs.keys())
    vals:list = list(kwargs.values())
    sql:str = f"DELETE FROM `{table}` WHERE `{keys[0]}`='{vals[0]}'"
    return doprocess(sql)

def searchlike(table:str,**kwargs)->list:
    keys:list = list(kwargs.keys())
    vals:list = list(kwargs.values())
    temp = []

    for key,value in kwargs.items():
        kv = f"`{key}` LIKE '%{value}%'"
        temp.append(kv)

    key_val = " OR ".join(temp)

    sql:str = f"SELECT * FROM `{table}` WHERE {key_val}"

    return getprocess(sql)
    
def checkfields(*args)->bool:
    for item in args:
        if item == '':
            return False
    return True

def userlogin(table:str,**kwargs)->list:
    keys:list = list(kwargs.keys())
    values:list = list(kwargs.values())
    sql:str = f"SELECT * FROM `{table}` WHERE `{keys[0]}` = '{values[0]}' AND `{keys[1]}` = '{values[1]}'"
    return getprocess(sql)

def getCustomerId(username):
    sql = f"SELECT * FROM `Customer` WHERE `username` = '{username}'"
    return getprocess(sql)

def getOrderId(o_date,ship_address,c_id):
    sql = f"SELECT * FROM `Orders` WHERE `o_date` = '{o_date}' AND `ship_address` = '{ship_address}' AND `c_id` = '{c_id}' ORDER BY `o_id` DESC LIMIT 1"
    return getprocess(sql)
    
def getOrders(c_id):
    sql = f"SELECT O.o_id, I.title, I.price, IO.qty, O.o_date, O.ship_address, (IO.qty * I.price) AS total FROM Items I INNER JOIN ItemsOrdered IO ON I.i_id = IO.i_id INNER JOIN Orders O ON IO.o_id = O.o_id INNER JOIN Customer C ON O.c_id = C.c_id WHERE C.c_id = {c_id}"
    return getprocess(sql)

def getItemsInCart(c_id):
    sql = f"SELECT (IC.qty * I.price) AS total, C.cart_id, IC.ic_id, I.i_id, IC.qty, I.title, I.price FROM Cart C INNER JOIN ItemsInCart IC ON C.cart_id = IC.cart_id INNER JOIN Items I ON IC.i_id = I.i_id WHERE C.cart_id = {c_id}"
    return getprocess(sql)

def getIID(ic_id):
    sql = f"SELECT * FROM ItemsInCart WHERE ic_id = {ic_id}"
    return getprocess(sql)