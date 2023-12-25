import sqlite3

#returns 0 is successful, -1 if there is an error
def add_product(product_dict):
    
    TEXT_ATTRIBUTES = ["code", "product_name", "generic_name", "brands", "quantity", "stores", "serving_size"]
    for key in product_dict:
        #if attribute is a string type, add extra quotes so that they get added to the SQL statement
        if key in TEXT_ATTRIBUTES:
            temp = product_dict[key]
            product_dict[key] = "\"" + str(temp) + "\""
        #if attribute is a numeric type, check the data type is correct
        else:
            try:
                temp = float(product_dict[key])
            except:
                return -1
    
    con = sqlite3.connect("myfood\\myfoodfacts.db")
    cursor = con.cursor()
    
    statement = "INSERT INTO {table} ({columns}) VALUES ({values});".format(table="Product", columns=",".join(product_dict.keys()), values=",".join(list(product_dict.values())))
    
    cursor.execute(statement)
    
    con.commit()
    con.close()
    
    return 0
