import io
import json
import os

from flask import Flask, request, send_from_directory

import pg_logger

app = Flask(__name__)


@app.route('/web_exec_<name>.py')
@app.route('/LIVE_exec_<name>.py')
@app.route('/viz_interaction.py')
@app.route('/syntax_err_survey.py')
@app.route('/runtime_err_survey.py')
@app.route('/eureka_survey.py')
@app.route('/error_log.py')
def dummy_ok(name=None):
    return 'OK'


@app.route('/<path:filepath>')
def index(filepath):
    return send_from_directory('.', filepath)


@app.route('/web_exec_py2.py')
@app.route('/web_exec_py3.py')
@app.route('/LIVE_exec_py2.py')
@app.route('/LIVE_exec_py3.py')
def get_py_exec():
    out_s = io.StringIO()

    def json_finalizer(input_code, output_trace):
        ret = dict(code=input_code, trace=output_trace)
        json_output = json.dumps(ret, indent=None)
        out_s.write(json_output)

    options = json.loads(request.args.get('options_json'))

    pg_logger.exec_script_str_local(request.args.get('user_script'),
                                    request.args.get('raw_input_json'),
                                    options['cumulative_mode'],
                                    options['heap_primitives'],
                                    json_finalizer)

    return out_s.getvalue()


if __name__ == "__main__":
    if os.environ.get('APP_LOCATION') == 'heroku':
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        app.run(host='0.0.0.0', port=19528)
