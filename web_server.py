#http://127.0.0.1/
#http://127.0.0.1/search

import myfoodfacts
import search

from flask import Flask, request, render_template, redirect
app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    search.reset_last_search_query()
    return render_template("index.html")

@app.route("/search")
def my_form():
    return search.search()
@app.route("/search", methods=["POST"])
def post_form():
    # when user pressed database toggle button
    if "db_toggle" in request.form:
        search.toggle_db()
        return search.search()
    # when user enters a search
    if "searchbar" in request.form:
        query = request.form["searchbar"]
        return search.search(query)
    # when user presses next page button
    elif "next_page" in request.form:
        return search.move_page(increment=True)
    # when user presses previous page button
    elif "prev_page" in request.form:
        return search.move_page(increment=False)
    # when user clicks on product
    elif "product" in request.form:
        search.reset_last_search_query()
        return render_template("item.html", code=request.form["product"])
    else:
        return search.search()

@app.route("/item/<product_code>")
@app.route("/<db>/item/<product_code>")
def product(product_code, db="openfoodfacts"):
    db_bool = search.OPENFOODFACTS_DB
    if db == "myfoodfacts":
        db_bool = not db_bool
    return search.get_product_page(product_code, default_db=db_bool)

@app.route("/create")
def render_add_item():
    return render_template("create.html")
@app.route("/create/generic")
def render_add_generic():
    return render_template("create-generic.html")
@app.route("/create", methods=["POST"])
@app.route("/create/generic", methods=["POST"])
def create_item():
    request_dict = request.form.to_dict(flat=False)
    print(request_dict)
    is_product = True if "code" in request_dict.keys() else False
    
    for key in list(request_dict):
        item = request_dict[key][0]
        if item == '':
            request_dict.pop(key)
        else:
            request_dict[key] = item
    
    if myfoodfacts.add(request_dict, is_product) == 0:
        return redirect("/index")
    else:
        return render_template("create.html", error_message="Invalid input (make sure the nutrition values are numbers)")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)