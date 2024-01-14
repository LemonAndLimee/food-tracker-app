import myfoodfacts, openfoodfacts_search
from flask import render_template

# search global variables
OPENFOODFACTS_DB = True
current_search_db = [OPENFOODFACTS_DB, "Search MyFoodFacts"]
last_search_query = ""


def search(query:str=None):
    global last_search_query
    
    if query == None:
        if len(last_search_query) == 0:
            return render_template("search.html", db_button=current_search_db[1])
        else: query = last_search_query
    else: last_search_query = query
    
    if current_search_db[0] == OPENFOODFACTS_DB: results = openfoodfacts_search.initiate_search(query, "product_name,brands,quantity")
    else: results = myfoodfacts.initiate_search(query)
    
    if results == -1:
        return render_template("search.html", error_message="No Search Results", db_button=current_search_db[1])
    return render_search_page(results)

def render_search_page(search_results):
    if current_search_db[0] == OPENFOODFACTS_DB:
        next_enabled = "enabled" if openfoodfacts_search.get_is_last_page() == False else "disabled"
        prev_enabled = "enabled" if openfoodfacts_search.get_current_page_number() > 1 else "disabled"
        db = "openfoodfacts"
    else:
        next_enabled = "enabled" if myfoodfacts.get_is_last_page() == False else "disabled"
        prev_enabled = "enabled" if myfoodfacts.get_current_page() > 1 else "disabled"
        db = "myfoodfacts"
    
    params = {
        "products":search_results[0],
        "images":search_results[1],
        "codes":search_results[2],
        "prev_btn_enabled":prev_enabled,
        "next_btn_enabled":next_enabled,
        "db_button":current_search_db[1],
        "current_db":db
    }
    return render_template("search.html", **params)
        

def toggle_db():
    current_search_db[0] = not current_search_db[0]
    current_search_db[1] = "Search MyFoodFacts" if current_search_db[0] == OPENFOODFACTS_DB else "Search OpenFoodFacts"

def reset_last_search_query():
    global last_search_query
    last_search_query = ""

def move_page(increment:bool):
    if current_search_db[0] == OPENFOODFACTS_DB: results = openfoodfacts_search.increment_page() if increment else openfoodfacts_search.decrement_page()
    else: results = myfoodfacts.move_page(1) if increment else myfoodfacts.move_page(-1)
    
    return render_search_page(results)

def get_product_page(code:str, default_db=OPENFOODFACTS_DB):
    ATTRIBUTES = ["product_name,generic_name,brands,quantity,stores,categories",
                  "item_name,serving_size,categories"]
    ATTRIBUTE_NAMES = [["", "", "Quantity: ", "Sold by: ", "Categories: "],
                       ["Serving Size: ", "Categories: "]]
    PRODUCT = 0
    GENERIC = 1
    item_type = PRODUCT
    item = myfoodfacts.get_item_from_code(code)
    if item == -1 and default_db == OPENFOODFACTS_DB: #if searching openfoodfacts
        item_info = openfoodfacts_search.get_product_by_code(code, ATTRIBUTES[PRODUCT])
        
        nutrition_table = openfoodfacts_search.get_nutrition_table(code)
    else: # if searching myfoodfacts
        id = item[0]
        item_type = PRODUCT if item[1] == "Product" else GENERIC

        
        attr_list = ATTRIBUTES[item_type].split()
        item_info = myfoodfacts.get_item(id, attr_list)
        item_info.insert(0, "") # add empty string because no image
        nutrition_table = myfoodfacts.get_nutrition_table(id)
    
    nutrition_headers = nutrition_table[0]
    nutrition_columns = nutrition_table[1]
    params= {
        "image":item_info[0],
        "title":item_info[1],
        "product":item_info[2:],
        "names":ATTRIBUTE_NAMES[item_type],
        "nutrition_table":nutrition_columns,
        "headers":nutrition_headers,
        "colours":nutrition_table[2]
    }
    
    path = "product.html" if item_type == PRODUCT else "item.html"
    return render_template(path, **params)