import openfoodfacts

RI_ADULT_PER_DAY = { "energy-kcal":2000, "fat":70, "saturated-fat":20, "carbohydrates":260, "sugars":90, "fiber":30, "proteins":50, "sodium":6 }

api = openfoodfacts.API(user_agent="FoodTrackerApp")

# returns [ image, attr1, attr2, ... ]
def get_product_by_code(code:int, attributes:str):
    attr_list = attributes.split(',')
    attr_list.insert(0, "image_url")
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
    
    
    
    