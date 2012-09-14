import ldap
from flask import Flask, render_template, request, make_response
from time import sleep
app = Flask('auth')
app.config.from_object(__name__)
app.config.from_pyfile('auth.cfg')

@app.route('/', methods=['GET'])
def form():
    return render_template('login.html')

@app.route('/', methods=['POST'])
def login():
    conn = ldap.initialize(app.config['LDAP_URL'])
    conn.start_tls_s()
    res,code = 'OK', 200
    try:
        conn.simple_bind_s(app.config['DN_STRING'] % request.form['login'],
                request.form.get('password', ''))
    except ldap.LDAPError:
        sleep(app.config['FAIL_DELAY'])
        res,code = 'ERROR', 401
    return make_response(res, code, { 'Content-Type': 'text/plain' })

if __name__ == '__main__':
    app.run('0.0.0.0', 8082, debug=True)
