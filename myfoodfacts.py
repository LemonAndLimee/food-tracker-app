import sqlite3

db_filepath = "myfood\\myfood.db"

RI_ADULT_PER_DAY = { "energy_kcal":2000, "fat":70, "saturates":20, "carbohydrates":260, "sugars":90, "fibre":30, "proteins":50, "sodium":6 }

PRODUCT = 0
GENERIC = 1
TEXT_ATTRIBUTES = [["code", "product_name", "generic_name", "brands", "quantity", "stores", "categories", "serving_size"],
                   ["item_name", "categories", "serving_size"]]
SEARCH_TEXT_ATTRIBUTES = [["product_name", "brands", "quantity"],
                          ["item_name", "serving_size"]]
ATTRIBUTE_RELEVANCE_SCORES = [[2, 2, 2, 2, 1, 1, 2, 0],
                              [2, 2, 0]]

PAGE_SIZE = 20
current_page = 1
is_last_page = False

current_search_list = [] #contains list of current item ids that match the search

#returns 0 is successful, -1 if there is an error
def add(product_dict:dict, is_product:bool):
    
    con = sqlite3.connect(db_filepath)
    cursor = con.cursor()
    
    if is_product:
        #validate barcode input
        barcode = product_dict["code"]
        try:
            int_ver = int(barcode)
            if len(barcode) != 13:
                return -1
        except:
            return -1
    else: #if item is generic, generate ID based on count from database
        cursor.execute("SELECT MAX(code) FROM Generics")
        max = cursor.fetchall()[0][0]
        product_dict["code"] = 0 if max is None else str(max+1)
    
    for key in product_dict:
        #if attribute is a string type, add extra quotes so that they get added to the SQL statement
        if key in TEXT_ATTRIBUTES[0] or key in TEXT_ATTRIBUTES[1]:
            temp = product_dict[key]
            product_dict[key] = "\"" + str(temp) + "\""
        #if attribute is a numeric type, check the data type is correct
        else:
            try:
                temp = float(product_dict[key])
            except:
                return -1
    
    #insert record into relevant table
    statement = "INSERT INTO {table} ({columns}) VALUES ({values});".format(table="Products" if is_product else "Generics", columns=",".join(product_dict.keys()), values=",".join(list(product_dict.values())))
    cursor.execute(statement)
    
    #add new item entity linking to Products or Generics table
    cursor.execute("SELECT MAX(item_id) FROM Items")
    max = cursor.fetchall()[0][0]
    item_id = 0 if max is None else str(max+1)
    statement = "INSERT INTO Items (item_id, code, item_type) VALUES ({id}, {c}, {t})".format(id=item_id, c=product_dict["code"], t="\"Product\"" if is_product else "\"Generic\"")
    cursor.execute(statement)
    
    con.commit()
    con.close()
    
    return 0

#returns list of item ids that match the search query
def search(qry:str):
    query = qry.split()
    
    con = sqlite3.connect(db_filepath)
    cursor = con.cursor()
    
    items_dict = {}
    
    for i in range(len(query)):
        for j in range(len(TEXT_ATTRIBUTES[PRODUCT])): #search in products
            statement = """SELECT item_id
                FROM Items, Products
                WHERE Products.{attr} LIKE '%{q}%'
                    AND Items.code = Products.code
            """.format(attr=TEXT_ATTRIBUTES[PRODUCT][j], q=query[i])
            cursor.execute(statement)
            id_list = cursor.fetchall()
            for x in range(len(id_list)):
                id = id_list[x][0]
                if id in items_dict:
                    items_dict[id] = items_dict[id] + ATTRIBUTE_RELEVANCE_SCORES[PRODUCT][j]
                else:
                    items_dict[id] = ATTRIBUTE_RELEVANCE_SCORES[PRODUCT][j]

        for j in range(len(TEXT_ATTRIBUTES[GENERIC])): # search in generics
            statement = """SELECT item_id
                FROM Items, Generics
                WHERE Generics.{attr} LIKE '%{q}%'
                    AND Items.code = Generics.code
            """.format(attr=TEXT_ATTRIBUTES[GENERIC][j], q=query[i])
            cursor.execute(statement)
            id_list= cursor.fetchall()
            for x in range(len(id_list)):
                id = id_list[x][0]
                if id in items_dict:
                    items_dict[id] = items_dict[id] + ATTRIBUTE_RELEVANCE_SCORES[GENERIC][j]
                else:
                    items_dict[id] = ATTRIBUTE_RELEVANCE_SCORES[GENERIC][j]
    
    con.commit()
    con.close()
    
    items_list = []
    ordered_list = sorted(items_dict.items(), key=lambda item: item[1], reverse=True)
    for item in ordered_list:
        items_list.append(item[0])
    
    #print(items_list)
    return items_list

#returns get_page, if no results returns -1
def initiate_search(query:str):
    global current_search_list
    current_search_list = search(query)
    if len(current_search_list) == 0:
        return -1
    return get_page(1)
    #return get page

# returns [attr1, attr2, attr3, ...]
def get_item(id:str, attr_list:list):
    con = sqlite3.connect(db_filepath)
    cursor = con.cursor()
    
    #gets item type and code from Items
    #print("SELECT item_type, code FROM Items WHERE item_id = " + str(id))
    cursor.execute("SELECT item_type, code FROM Items WHERE item_id = " + str(id))
    result = cursor.fetchall()[0]
    item_type = result[0]
    code = result[1]
    
    #select attributes from relevant entity in Products or Generics
    statement = "SELECT"
    for attr in attr_list:
        statement = statement + " " + attr + ","
    statement = statement[:-1] + " FROM " + item_type + "s WHERE Code = '{c}'".format(c=code)
    #print(statement)
    cursor.execute(statement)
    result = cursor.fetchall()[0]
    
    con.commit()
    con.close()
    
    return list(result)

#returns (id, type)
#returns -1 if error
def get_item_from_code(code:str):
    con = sqlite3.connect(db_filepath)
    cursor = con.cursor()
    
    #gets item type and code from Items
    #print("SELECT item_id, item_type FROM Items WHERE code = '{c}'".format(c=code))
    cursor.execute("SELECT item_id, item_type FROM Items WHERE code = '{c}'".format(c=code))
    try:
        result = cursor.fetchall()[0]
    except: return -1
    
    con.close()
    return (result[0], result[1])
    
# returns (items, images, codes)
# where items = [attr1, attr2, attr3, ...]
# where images = [] (added for future potential images)
# where codes = [code1, code2, code3, ...]
def get_page(page_num:int):
    global current_search_list, is_last_page, current_page
    if page_num + 1 > len(current_search_list) // PAGE_SIZE:
        is_last_page = True
    else:
        is_last_page = False
    current_page = page_num
    
    starting_index = PAGE_SIZE * (page_num-1)
    
    items = []
    images = []
    codes = []
    
    for i in range(starting_index, starting_index+PAGE_SIZE):
        if i >= len(current_search_list): break
        current_id = current_search_list[i]
        images.append("")
        
        con = sqlite3.connect(db_filepath)
        cursor = con.cursor()
        #gets item type and code from Items
        cursor.execute("SELECT item_type, code FROM Items WHERE item_id = " + str(current_id))
        result = cursor.fetchall()[0]
        item_type = result[0]
        current_code = result[1]
        codes.append(current_code)
        ITEM_TYPE_INT = PRODUCT if item_type == "Product" else GENERIC
        
        
        items.append(get_item(current_id, SEARCH_TEXT_ATTRIBUTES[ITEM_TYPE_INT]))
    
    return (items, images, codes)

def move_page(amount:int):
    return get_page(current_page + amount)

def get_is_last_page():
    return is_last_page
def get_current_page():
    return current_page

def get_nutrition_table(id:str):
    headers = ["Nutrition Info", "Per 100g", "Per Serving"]
    ATTRIBUTES = ["energy_kcal", "fat", "saturates", "carbohydrates", "sugars", "fibre", "proteins", "sodium"]
    ATTR_NAMES = ["Energy", "Fat", "of which saturates", "Carbohydrates", "of which sugars", "Fibre", "Protein", "Salt"]
    
    #gets item type and code from Items
    con = sqlite3.connect(db_filepath)
    cursor = con.cursor()
    cursor.execute("SELECT item_type FROM Items WHERE item_id = " + str(id))
    item_type = cursor.fetchall()[0][0]
    
    total_attributes = ["serving_size"]
    for attr in ATTRIBUTES:
        if item_type == "Product":
            total_attributes.append(attr + "_100g")
        total_attributes.append(attr + "_serving")
    
    item = get_item(id, total_attributes)
    
    has_serving = True
    try: # if serving size exists, add it to caption
        headers[2] = headers[2] + " (" + str(item[0] + ")") #0 is the index of serving_size
        headers.append("% RI (serving)")
    except:
        headers.remove("Per Serving")
        has_serving = False
    
    # first column
    results = [ ATTR_NAMES ]
    
    # second and third column
    if item_type == "Product":
        results.append([  ])
    else:
        headers.remove("Per 100g")
        
    if has_serving: results.append([  ])
    
    index_100g = -2 if has_serving else -1
    
    for attribute in ATTRIBUTES:
        append_string = "kcal" if attribute == "energy_kcal" else "g"
        if item_type == "Product":
            try:
                results[index_100g].append(str(item[total_attributes.index(attribute + "_100g")]) + append_string)
            except:
                results[index_100g].append("N/A")
        
        if has_serving:
            try:
                results[-1].append(str(item[total_attributes.index(attribute + "_serving")]) + append_string)
            except:
                #print("serving fail")
                results[-1].append("N/A")
    
    # last column
    if has_serving:
        results.append([  ])
        for attr in ATTRIBUTES:
            try:
                percent_of_ri = (item[total_attributes.index(attr + "_serving")] / RI_ADULT_PER_DAY[attr]) * 100
                percent_of_ri = round(percent_of_ri, 2)
                results[-1].append(str(percent_of_ri) + "%")
            except:
                results[-1].append("N/A")
    
    colour_values = []
    if item_type == "Product":
        colour_values.append(get_colour_value(item, total_attributes.index("fat_100g"), "fat_100g"))
        colour_values.append(get_colour_value(item, total_attributes.index("saturates_100g"), "saturates_100g"))
        colour_values.append(get_colour_value(item, total_attributes.index("sugars_100g"), "sugars_100g"))
        colour_values.append(get_colour_value(item, total_attributes.index("sodium_100g"), "sodium_100g"))
    else:
        colour_values = ["white", "white", "white", "white"]

    return [headers, results, colour_values]

# returns food label colour in line with UK food labelling
def get_colour_value(item:list, attribute_index:int, attribute:str):
    COLOURS = {"green":"#57C411", "orange":"#F5B922", "red":"#E42000", "unknown":"white"}
    HIGH_VALUES = {"fat_100g": 17.5, "saturates_100g":5, "sugars_100g":22.5, "sodium_100g":1.5}
    LOW_VALUES = {"fat_100g":3, "saturates_100g":1.5, "sugars_100g":5, "sodium_100g":0.3}
    try:
        value = item[attribute_index]
        if value >= HIGH_VALUES[attribute]: return COLOURS["red"]
        elif value > LOW_VALUES[attribute]: return COLOURS["orange"]
        else: return COLOURS["green"]
    except:
        return COLOURS["unknown"]