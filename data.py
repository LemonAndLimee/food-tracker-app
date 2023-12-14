import openfoodfacts

api = openfoodfacts.API(user_agent="FoodTrackerApp")

def display_product(product, attributes:str):
    attr = attributes.split(',')
    for i in range(len(attr)):
        try:
            print(attr[i] + ": " + product[attr[i]])
        except:
            print(attr[i] + " not found")

def search(query:str, attributes:str, number):
    s = api.product.text_search(query=query)
    attr = attributes.split(',')
    products = []
    
    x = 0
    
    while len(products) < number and x < len(s["products"]):
        products.append([])
        
        product = s["products"][x]
        while "United Kingdom" not in product["countries"] and x < len(s["products"])-1:
            x += 1
            product = s["products"][x]
        if "United Kingdom" not in product["countries"]:
            return -1
    
        for i in range(len(attr)):
            try:
                products[-1].append(str(attr[i] + ": " + product[attr[i]]))
            except:
                products[-1].append(str(attr[i] + " not found"))
        
        x += 1
        
    print(products)
    return products