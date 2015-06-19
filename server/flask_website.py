from flask import Flask
app = Flask(__name__)

@app.route("/")
@app.route("/index")
def hello():
    return "Hello World!"

@app.route("/api/<month>/")
def api(month):
        return "This is data for " + month



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
