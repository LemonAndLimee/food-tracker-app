import sqlite3

RI_ADULT_PER_DAY = { "energy_kcal":2000, "fat":70, "saturates":20, "carbohydrates":260, "sugars":90, "fibre":30, "proteins":50, "sodium":6 }

TEXT_ATTRIBUTES = ["code", "product_name", "generic_name", "brands", "quantity", "stores", "categories", "serving_size"]
ATTRIBUTE_RELEVANCE_SCORES = [2, 2, 2, 2, 1, 1, 2, 0]

PAGE_SIZE = 20
current_page = 1
is_last_page = False
current_search_params = []

current_search_list = []

#returns 0 is successful, -1 if there is an error
def add(product_dict:dict, is_product:bool):
    if is_product:
        #validate barcode input
        barcode = product_dict["code"]
        try:
            int_ver = int(barcode)
            if len(barcode) != 13:
                return -1
        except:
            return -1
    
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
    
    statement = "INSERT INTO {table} ({columns}) VALUES ({values});".format(table="Products" if is_product else "Generics", columns=",".join(product_dict.keys()), values=",".join(list(product_dict.values())))
    
    cursor.execute(statement)
    
    con.commit()
    con.close()
    
    return 0

def search(qry:str):
    query = qry.split()
    
    con = sqlite3.connect("myfood\\myfoodfacts.db")
    cursor = con.cursor()
    
    codes_dict = {}
    
    for i in range(len(query)):
        for j in range(len(TEXT_ATTRIBUTES)):
            statement = "SELECT code FROM Products WHERE " + TEXT_ATTRIBUTES[j] + " LIKE '%" + query[i] + "%'"
            cursor.execute(statement)
            codes = cursor.fetchall()
            for x in range(len(codes)):
                code = codes[x][0]
                if code in codes_dict:
                    codes_dict[code] = codes_dict[code] + ATTRIBUTE_RELEVANCE_SCORES[j]
                else:
                    codes_dict[code] = ATTRIBUTE_RELEVANCE_SCORES[j]
    
    con.commit()
    con.close()
    
    codes_list = []
    ordered_list = sorted(codes_dict.items(), key=lambda item: item[1], reverse=True)
    for item in ordered_list:
        codes_list.append(item[0])
    
    return codes_list

def initiate_search(query:str, attr_list:list):
    global current_search_list, current_search_params
    current_search_params = attr_list
    current_search_list = search(query)
    if len(current_search_list) == 0:
        return -1
    return get_page(1, attr_list)
    #return get page

# returns [attr1, attr2, attr3, ...]
def get_product(code:str, attr_list:list):
    con = sqlite3.connect("myfood\\myfoodfacts.db")
    cursor = con.cursor()
    
    statement = "SELECT"
    for attr in attr_list:
        statement = statement + " " + attr + ","
    statement = statement[:-1] + " FROM Products WHERE code = '{c}'".format(c=code)
    cursor.execute(statement)
    result = cursor.fetchall()
    
    con.commit()
    con.close()
    
    return list(result[0])

def get_page(page_num:int, attr_list:list):
    global current_search_list, is_last_page, current_page
    if page_num + 1 > len(current_search_list) // PAGE_SIZE:
        is_last_page = True
    else:
        is_last_page = False
    current_page = page_num
    
    starting_index = PAGE_SIZE * (page_num-1)
    
    products = []
    images = []
    codes = []
    
    for i in range(starting_index, starting_index+PAGE_SIZE):
        if i >= len(current_search_list): break
        current_code = current_search_list[i]
        codes.append(current_code)
        images.append("")
        products.append(get_product(current_code, attr_list))
    
    return (products, images, codes)

def move_page(amount:int):
    return get_page(current_page + amount, current_search_params)

def get_is_last_page():
    return is_last_page
def get_current_page():
    return current_page

def get_nutrition_table(code:str):
    headers = ["Nutrition Info", "Per 100g", "Per Serving"]
    ATTRIBUTES = ["energy_kcal", "fat", "saturates", "carbohydrates", "sugars", "fibre", "proteins", "sodium"]
    ATTR_NAMES = ["Energy", "Fat", "of which saturates", "Carbohydrates", "of which sugars", "Fibre", "Protein", "Salt"]
    
    total_attributes = ["serving_size"]
    for attr in ATTRIBUTES:
        total_attributes.append(attr + "_100g")
        total_attributes.append(attr + "_serving")
    
    product = get_product(code, total_attributes)
    
    has_serving = True
    try: # if serving size exists, add it to caption
        headers[2] = headers[2] + " (" + str(product[0] + ")") #0 is the index of serving_size
        headers.append("% RI (serving)")
    except:
        headers.pop(2)
        has_serving = False
    
    # first column
    results = [ ATTR_NAMES ]
    
    # second and third column
    results.append([  ])
    if has_serving: results.append([  ])
    
    index_100g = -2 if has_serving else -1
    
    for attribute in ATTRIBUTES:
        append_string = "kcal" if attribute == "energy_kcal" else "g"
        try:
            results[index_100g].append(str(product[total_attributes.index(attribute + "_100g")]) + append_string)
        except:
            print("100g fail")
            results[index_100g].append("N/A")
        
        if has_serving:
            try:
                results[-1].append(str(product[total_attributes.index(attribute + "_serving")]) + append_string)
            except:
                print("serving fail")
                results[-1].append("N/A")
    
    # last column
    if has_serving:
        results.append([  ])
        for attr in ATTRIBUTES:
            try:
                percent_of_ri = (product[total_attributes.index(attr + "_serving")] / RI_ADULT_PER_DAY[attr]) * 100
                percent_of_ri = round(percent_of_ri, 2)
                results[-1].append(str(percent_of_ri) + "%")
            except:
                results[-1].append("N/A")
    
    colour_values = []
    colour_values.append(get_colour_value(product, total_attributes.index("fat_100g"), "fat_100g"))
    colour_values.append(get_colour_value(product, total_attributes.index("saturates_100g"), "saturates_100g"))
    colour_values.append(get_colour_value(product, total_attributes.index("sugars_100g"), "sugars_100g"))
    colour_values.append(get_colour_value(product, total_attributes.index("sodium_100g"), "sodium_100g"))

    return [headers, results, colour_values]

# returns food label colour in line with UK food labelling
def get_colour_value(product:list, attribute_index:int, attribute:str):
    COLOURS = {"green":"#57C411", "orange":"#F5B922", "red":"#E42000", "unknown":"white"}
    HIGH_VALUES = {"fat_100g": 17.5, "saturates_100g":5, "sugars_100g":22.5, "sodium_100g":1.5}
    LOW_VALUES = {"fat_100g":3, "saturates_100g":1.5, "sugars_100g":5, "sodium_100g":0.3}
    try:
        value = product[attribute_index]
        if value >= HIGH_VALUES[attribute]: return COLOURS["red"]
        elif value > LOW_VALUES[attribute]: return COLOURS["orange"]
        else: return COLOURS["green"]
    except:
        return COLOURS["unknown"]