#http://127.0.0.1/
#http://127.0.0.1/search

import data

from flask import Flask, request, render_template
app = Flask(__name__)

@app.route("/")
def index():
    return "index"

@app.route("/search")
def my_form():
    return render_template("search.html")
@app.route("/search", methods=["POST"])
def post_form():
    if "searchbar" in request.form:
        query = request.form["searchbar"]
        results = data.initiate_search(query, "product_name,generic_name,brands,quantity,countries,categories")
        if results == -1:
            return render_template("search.html", error_message="No Search Results")
        
        return render_template("search.html", products=results[0], images=results[1], next_btn_enabled="enabled")
    if "next_page" in request.form:
        print("incr")
        results = data.increment_page()
        prev_enabled = "enabled" if data.current_page > 1 else "disabled"
        return render_template("search.html", products=results[0], images=results[1], prev_btn_enabled=prev_enabled, next_btn_enabled="enabled")
    if "prev_page" in request.form:
        print("decr")
        results = data.decrement_page()
        prev_enabled = "enabled" if data.current_page > 1 else "disabled"
        return render_template("search.html", products=results[0], images=results[1], prev_btn_enabled=prev_enabled, next_btn_enabled="enabled")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)