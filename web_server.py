#http://127.0.0.1/
#http://127.0.0.1/search

import search

from flask import Flask, request, render_template
app = Flask(__name__)

@app.route("/")
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
        next_enabled = "enabled" if search.get_is_last_page() == False else "disabled"
        return render_template("search.html", products=results[0], images=results[1], next_btn_enabled=next_enabled)
    # when user presses next page button
    if "next_page" in request.form:
        results = search.increment_page()
        prev_enabled = "enabled" if search.get_current_page_number() > 1 else "disabled"
        next_enabled = "enabled" if search.get_is_last_page() == False else "disabled"
        return render_template("search.html", products=results[0], images=results[1], prev_btn_enabled=prev_enabled, next_btn_enabled=next_enabled)
    # when user presses previous page button
    if "prev_page" in request.form:
        results = search.decrement_page()
        prev_enabled = "enabled" if search.get_current_page_number() > 1 else "disabled"
        return render_template("search.html", products=results[0], images=results[1], prev_btn_enabled=prev_enabled, next_btn_enabled="enabled")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)