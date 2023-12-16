import data

api = data.api

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
def return_filtered(products, attributes_list):
    results = []
    for i in range(len(products)):
        if "United Kingdom" in products[i]["countries"]:
            if check_for_valid_data(products[i]) == True:
                try:
                    results.append([products[i]["image_url"],])
                except:
                    results.append([""])
                for a in attributes_list:
                    try:
                        results[-1].append(a + ": " + str(products[i][a]))
                    except:
                        results[-1].append(a + " NOT FOUND")
    return results


# gets info for desired page, starting at 1
# should only be called after search is initalised, otherwise will return error or previous page pointers
def get_page(query:str, attributes:str, page_num:int):
    global is_last_page
    
    db_page_pointers = current_page_pointers[page_num]
    print("get page call, pnum= " + str(page_num) + " db ptrs= " + str(db_page_pointers[0]) + " " + str(db_page_pointers[1]))
    
    attr_list = attributes.split(',')
    current_search = api.product.text_search(query=query, page=db_page_pointers[0])
    current_search_filtered = return_filtered(current_search["products"], attr_list)
    print("len filtered= " + str(len(current_search_filtered)))
    
    current_index = 0
    products_list = []
    images_list = []
    
    
    next_pointers = [db_page_pointers[0], 0]
    while len(products_list) < PAGE_SIZE and not is_last_page:
        
        next_page = True if current_index == len(current_search_filtered) or len(current_search_filtered) == 0 else False
        while next_page:
            if next_pointers[0]+1 > current_search["page_count"]:
                print("end of pages, nextptr= " + str(next_pointers[0]+1) + " pcount= " + str(current_search["page_count"]))
                is_last_page = True
                # if no search results, return error, else return what we have
                if len(products_list) == 0: return -1
                else: break
            current_index = 0
            next_pointers[0] = next_pointers[0] + 1
            current_search = api.product.text_search(query=query, page=next_pointers[0])
            current_search_filtered = return_filtered(current_search["products"], attr_list)
            print("len filtered= " + str(len(current_search_filtered)))
            if len(current_search_filtered) > 0:
                next_page = False
        
        if not is_last_page:
            current_product = current_search_filtered[current_index]
            products_list.append(current_product[1:])
            images_list.append(current_product[0])
        
        current_index += 1
    next_pointers[1]  = current_index
    current_page_pointers[page_num+1] = next_pointers
    
    print("len of pr, img= " + str(len(products_list)) + " " + str(len(images_list)))
    print(next_pointers)
    result = (products_list, images_list)
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