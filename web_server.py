#http://127.0.0.1/
#http://127.0.0.1/search

import search, data

from flask import Flask, request, render_template
app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/search")
def my_form():
    return render_template("search.html")
@app.route("/search", methods=["POST"])
def post_form():
    # when user enters a search
    if "searchbar" in request.form:
        query = request.form["searchbar"]
        results = search.initiate_search(query, "product_name,brands,quantity")
        if results == -1:
            return render_template("search.html", error_message="No Search Results")
        return render_search_page(results)
    # when user presses next page button
    elif "next_page" in request.form:
        results = search.increment_page()
        return render_search_page(results)
    # when user presses previous page button
    elif "prev_page" in request.form:
        results = search.decrement_page()
        return render_search_page(results)
    # when user clicks on product
    elif "product" in request.form:
        return render_template("product.html", code=request.form["product"])
    else:
        return render_template("search.html")
def render_search_page(search_results):
    next_enabled = "enabled" if search.get_is_last_page() == False else "disabled"
    prev_enabled = "enabled" if search.get_current_page_number() > 1 else "disabled"
    return render_template("search.html", products=search_results[0], images=search_results[1], codes=search_results[2], prev_btn_enabled=prev_enabled, next_btn_enabled=next_enabled)

@app.route("/product/<product_code>")
def product(product_code):
    attributes = "product_name,generic_name,brands,quantity,stores,categories"
    attribute_names = ["", "", "Quantity: ", "Sold by: ", "Categories: "]
    product_info = data.get_product_by_code(product_code, attributes)
    
    nutrition_table = data.get_nutrition_table(product_code)
    nutrition_headers = nutrition_table[0]
    nutrition_columns = nutrition_table[1]
    
    return render_template("product.html", image=product_info[0], title=product_info[1], product=product_info[2:], names=attribute_names, nutrition_table=nutrition_columns, headers=nutrition_headers)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)