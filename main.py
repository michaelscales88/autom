from time import sleep
from subprocess import Popen, PIPE
from flask import Flask, render_template, request, Response
from queue import Queue


from automated_sla_tool.src.utilities import valid_dt


app = Flask(__name__)


@app.route('/')
def homepage():
    return """<h1>SLA REPORT</h1>"""


@app.route('/')
def my_form():
    return render_template('my-form.html')


@app.route('/main', methods=['POST'])
def main_page():
    date_time = request.form['date']
    return call('manual_main.py', date_time)


@app.route('/test_main')  #
def test_page():
    date_time = request.form['date']
    return call('test_main.py', date_time)


# This is wehre I invoke scripting
def call(file, string_date=None):
    def inner():
        proc = Popen(
            ['python', file, string_date],  # call something with a lot of output so we can see it
            shell=True,
            stdout=PIPE,
            stdin=PIPE
        )

        for line in iter(proc.stdout.readline, ''):
            sleep(.5)  # Don't need this just shows the text streaming
            yield '{}{}'.format(line.rstrip().decode('utf-8'), '<br/>\n')

    return Response(inner(), mimetype='text/html')


@app.route('/', methods=['POST'])
def main():
    date_time = valid_dt(request.form['date'])
    return str(date_time)
    # return generic_ui.main(report_date=date_time.date())


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000, use_reloader=True)






