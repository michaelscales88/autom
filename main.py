from automated_sla_tool.bin import generic_ui
from flask import Flask, render_template, request


app = Flask(__name__)


@app.route('/')
def my_form():
    return render_template('my-form.html')


@app.route('/', methods=['POST'])
def main():
    text = request.form['date']
    return text
    # return generic_ui.main()

# @app.route("/")
# def test():
#     return "Test Success"


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)






