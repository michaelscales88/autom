from time import sleep
from subprocess import Popen, PIPE
from flask import Flask, render_template, request, Response
from queue import Queue


from automated_sla_tool.src.utilities import valid_dt


app = Flask(__name__)


@app.route('/')
def my_form():
    return render_template('my-form.html')


@app.route('/', methods=['POST'])
def main():
    date_time = request.form['date']
    return index(date_time)


# This is wehre I invoke scripting
def index(string_date=None):
    def inner():
        proc = Popen(
            ['python', 'manual_main.py', string_date],  # call something with a lot of output so we can see it
            shell=True,
            stdout=PIPE,
            stdin=PIPE
        )

        for line in iter(proc.stdout.readline, ''):
            sleep(.5)  # Don't need this just shows the text streaming
            yield '{}{}'.format(line.rstrip().decode('utf-8'), '<br/>\n')

    return Response(inner(), mimetype='text/html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)






