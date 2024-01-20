import openfoodfacts

RI_ADULT_PER_DAY = { "energy-kcal":2000, "fat":70, "saturated-fat":20, "carbohydrates":260, "sugars":90, "fiber":30, "proteins":50, "sodium":6 }

api = openfoodfacts.API(user_agent="FoodTrackerApp")

''' Methods for displaying search pages '''

PAGE_SIZE = 20
# pointers to where to begin in text search
# [x,y] at key i means that for page i+1, call a text search for page x, and begin at index y in those results
current_page_pointers = {1:[1,0]}
current_search_params = []
current_page = 1
is_last_page = False

# if missing nutritional info return false
def check_for_valid_data(product):
    try:
        if len(product["nutriments"]) == 0: return False
        energy = product["nutriments"]["energy"]
        return True
    except: return False

# removes any products with insufficient data, or not from the UK
# results = [ [product1], [product2], ... ] where product = [ code, image, attributes...]
def return_filtered(products, attributes_list):
    results = []
    for i in range(len(products)):
        if "United Kingdom" in products[i]["countries"]:
            if check_for_valid_data(products[i]) == True:
                try:
                    results.append([products[i]["code"]])
                    
                    try:
                        results[-1].append(products[i]["image_url"])
                    except:
                        results[-1].append("")
                    for a in attributes_list:
                        try:
                            results[-1].append(str(products[i][a]))
                        except:
                            results[-1].append("")
                except: #if item has no code, skip
                    continue
    return results


# gets info for desired page, starting at 1
# should only be called after search is initalised, otherwise will return error or previous page pointers
def get_page(query:str, attributes:str, page_num:int):
    global is_last_page
    
    db_page_pointers = current_page_pointers[page_num]
    
    attr_list = attributes.split(',')
    current_search = api.product.text_search(query=query, page=db_page_pointers[0])
    current_search_filtered = return_filtered(current_search["products"], attr_list)
    
    current_index = 0
    products_list = []
    images_list = []
    codes_list = []
    
    next_pointers = [db_page_pointers[0], 0]
    while len(products_list) < PAGE_SIZE and not is_last_page:
        
        next_page = True if current_index == len(current_search_filtered) or len(current_search_filtered) == 0 else False
        while next_page:
            if next_pointers[0]+1 > current_search["page_count"]:
                is_last_page = True
                # if no search results, return error, else return what we have
                if len(products_list) == 0: return -1
                else: break
            current_index = 0
            next_pointers[0] = next_pointers[0] + 1
            current_search = api.product.text_search(query=query, page=next_pointers[0])
            current_search_filtered = return_filtered(current_search["products"], attr_list)
            if len(current_search_filtered) > 0:
                next_page = False
        
        if not is_last_page:
            current_product = current_search_filtered[current_index]
            products_list.append(current_product[2:])
            images_list.append(current_product[1])
            codes_list.append(current_product[0])
        
        current_index += 1
    next_pointers[1]  = current_index
    current_page_pointers[page_num+1] = next_pointers
    
    result = (products_list, images_list, codes_list)
    return result

def increment_page():
    global current_page
    current_page = current_page + 1
    return get_page(current_search_params[0], current_search_params[1], current_page)
    #add exceptions for if no more pages left

def decrement_page():
    global current_page, is_last_page
    current_page = current_page - 1
    result = get_page(current_search_params[0], current_search_params[1], current_page)
    if result == -1: is_last_page = False
    return result

def initiate_search(query:str, attributes:str):
    global current_page, current_page_pointers, current_search_params, is_last_page
    is_last_page = False
    current_page_pointers = {1:[1,0]}
    current_search_params = [query, attributes]
    current_page = 1
    return get_page(query, attributes, 1)

def get_current_page_number():
    return current_page
def get_is_last_page():
    return is_last_page


''' Methods for fetching product '''

# returns [ image, attr1, attr2, ... ]
def get_product_by_code(code:int, attributes:str, include_image=True):
    attr_list = attributes.split(',')
    if include_image: attr_list.insert(0, "image_url")
    product = api.product.get(code, fields=attr_list)
    
    results = []
    for i in range(len(attr_list)):
        try:
            results.append(str(product[attr_list[i]]))
        except:
            if i == 0: # if image:
                results.append("")
            else:
                results.append("Not available")
    
    return results

#returns [attr1, attr2, ...] for a given list of attributes
#returns -1 if not available
def get_product_attributes(code:str, attr_list:list):
    product = api.product.get(str(code), fields=attr_list)
    results = []
    for i in range(len(attr_list)):
        try:
            results.append(product[attr_list[i]])
        except:
            return -1
    return results

# returns [ [headers],  [[column1], [column2], ...], [colours]] where [column] = [cell, cell, ...], and [colours] is the colour labels
def get_nutrition_table(code:int):
    headers = ["Nutrition Info", "Per 100g", "Per Serving"]
    ATTRIBUTES = ["energy-kcal", "fat", "saturated-fat", "carbohydrates", "sugars", "fiber", "proteins", "sodium"]
    ATTR_NAMES = ["Energy", "Fat", "of which saturates", "Carbohydrates", "of which sugars", "Fibre", "Protein", "Salt"]

    total_attributes = ["serving_size"]
    for attr in ATTRIBUTES:
        total_attributes.append(attr + "_100g")
        total_attributes.append(attr + "_serving")
        
    product = api.product.get(code, total_attributes)
    
    has_serving = True
    try: # if serving size exists, add it to caption
        headers[2] = headers[2] + " (" + str(product["serving_size"] + ")")
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
        append_string = "kcal" if attribute == "energy-kcal" else "g"
        try:
            results[index_100g].append(str(product[attribute + "_100g"]) + append_string)
        except:
            print("100g fail")
            results[index_100g].append("N/A")
        
        if has_serving:
            try:
                results[-1].append(str(product[attribute + "_serving"]) + append_string)
            except:
                print("serving fail")
                results[-1].append("N/A")
    
    # last column
    if has_serving:
        results.append([  ])
        for attr in ATTRIBUTES:
            try:
                percent_of_ri = (product[attr + "_serving"] / RI_ADULT_PER_DAY[attr]) * 100
                percent_of_ri = round(percent_of_ri, 2)
                results[-1].append(str(percent_of_ri) + "%")
            except:
                results[-1].append("N/A")
    
    
    colour_values = []
    colour_values.append(get_colour_value(product, "fat_100g"))
    colour_values.append(get_colour_value(product, "saturated-fat_100g"))
    colour_values.append(get_colour_value(product, "sugars_100g"))
    colour_values.append(get_colour_value(product, "sodium_100g"))
    
    return [headers, results, colour_values]

# returns food label colour in line with UK food labelling
def get_colour_value(product, attribute_name):
    COLOURS = {"green":"#57C411", "orange":"#F5B922", "red":"#E42000", "unknown":"white"}
    HIGH_VALUES = {"fat_100g": 17.5, "saturated-fat_100g":5, "sugars_100g":22.5, "sodium_100g":1.5}
    LOW_VALUES = {"fat_100g":3, "saturated-fat_100g":1.5, "sugars_100g":5, "sodium_100g":0.3}
    try:
        value = product[attribute_name]
        if value >= HIGH_VALUES[attribute_name]: return COLOURS["red"]
        elif value > LOW_VALUES[attribute_name]: return COLOURS["orange"]
        else: return COLOURS["green"]
    except:
        return COLOURS["unknown"]
    
