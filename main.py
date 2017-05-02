from flask import Flask, render_template, request


from automated_sla_tool.src.utilities import valid_dt
from automated_sla_tool.bin import generic_ui


app = Flask(__name__)


@app.route('/')
def my_form():
    return render_template('my-form.html')


# TODO I want to stop using the terminal and switch to entirely browser based cmd line esque
@app.route('/', methods=['POST'])
def main():
    # This does not pipe the input/output to the browser but to a terminal instead
    date_time = valid_dt(request.form['date'])
    return generic_ui.main(report_date=date_time.date())


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)






