from automated_sla_tool.bin.generic_ui import main
from flask import Flask
app = Flask(__name__)

#
# @app.route("/")
# def main():
#     main()

@app.route("/")
def test():
    return "Test Success"


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)






