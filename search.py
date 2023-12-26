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
    else: results = myfoodfacts.initiate_search(query, ["product_name", "brands", "quantity"])
    
    if results == -1:
        return render_template("search.html", error_message="No Search Results", db_button=current_search_db[1])
    return render_search_page(results)

def render_search_page(search_results):
    if current_search_db[0] == OPENFOODFACTS_DB:
        next_enabled = "enabled" if openfoodfacts_search.get_is_last_page() == False else "disabled"
        prev_enabled = "enabled" if openfoodfacts_search.get_current_page_number() > 1 else "disabled"
    else:
        next_enabled = "enabled" if myfoodfacts.get_is_last_page() == False else "disabled"
        prev_enabled = "enabled" if myfoodfacts.get_current_page() > 1 else "disabled"
    params = {
        "products":search_results[0],
        "images":search_results[1],
        "codes":search_results[2],
        "prev_btn_enabled":prev_enabled,
        "next_btn_enabled":next_enabled,
        "db_button":current_search_db[1]
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

def get_product(product_code:str):
    attributes = "product_name,generic_name,brands,quantity,stores,categories"
    attribute_names = ["", "", "Quantity: ", "Sold by: ", "Categories: "]
    if current_search_db[0] == OPENFOODFACTS_DB:
        product_info = openfoodfacts_search.get_product_by_code(product_code, attributes)
        
        nutrition_table = openfoodfacts_search.get_nutrition_table(product_code)
    else:
        attr_list = attributes.split()
        product_info = myfoodfacts.get_product(product_code, attr_list)
        product_info.insert(0, "") # add empty string because no image
        nutrition_table = myfoodfacts.get_nutrition_table(product_code)
    
    nutrition_headers = nutrition_table[0]
    nutrition_columns = nutrition_table[1]
    params= {
        "image":product_info[0],
        "title":product_info[1],
        "product":product_info[2:],
        "names":attribute_names,
        "nutrition_table":nutrition_columns,
        "headers":nutrition_headers,
        "colours":nutrition_table[2]
    }
    return render_template("product.html", **params)