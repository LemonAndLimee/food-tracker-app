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
    text = request.form["searchbar"]
    result = data.search(text, "image_url,product_name,generic_name,brands,quantity,countries", 20)
    if result == -1:
        print("No Search Results")
        return render_template("search.html")
    images = []
    for i in range(len(result)):
        images.append(result[i][0][11:])
        result[i].pop(0)
    return render_template("search.html", products=result, images=images)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)