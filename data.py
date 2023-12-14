import openfoodfacts

api = openfoodfacts.API(user_agent="FoodTrackerApp")

def display_product(product, attributes:str):
    attr = attributes.split(',')
    for i in range(len(attr)):
        try:
            print(attr[i] + ": " + product[attr[i]])
        except:
            print(attr[i] + " not found")


search = api.product.text_search(query="biscuits")

for i in range(3):
    code = search["products"][i]["code"]
    product = api.product.get(code)

    display_product(product, "product_name,quantity,stores,countries")
    print("")