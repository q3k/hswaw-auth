import ldap
import re
from flask import Flask, render_template, request, make_response
from time import sleep
app = Flask('auth')
app.config.from_object(__name__)
app.config.from_pyfile('auth.cfg')

def connect_to_ldap():
    conn = ldap.initialize(app.config['LDAP_URL'])
    conn.start_tls_s()
    conn.simple_bind(app.config['LDAP_BIND_DN'], app.config['LDAP_BIND_PASSWORD'])
    return conn

@app.route('/', methods=['GET'])
def form():
    return render_template('login.html')

@app.route('/', methods=['POST'])
def login():
    conn = ldap.initialize(app.config['LDAP_URL'])
    conn.start_tls_s()
    res,code = 'OK', 200
    # hack!
    if ' ' in request.form['login']:
        res, code = 'ERROR', 401
        return make_response(res, code, { 'Content-Type': 'text/plain' })
    try:
        conn.simple_bind_s(app.config['DN_STRING'] % request.form['login'],
                request.form.get('password', ''))
    except ldap.LDAPError:
        sleep(app.config['FAIL_DELAY'])
        res,code = 'ERROR', 401
    return make_response(res, code, { 'Content-Type': 'text/plain' })

@app.route('/irc', methods=['GET'])
def irc_form():
    if not app.config['EXTRA_HSWAW']:
        return 404
    return render_template('irc.html')

@app.route('/irc', methods=['POST'])
def irc_nick():
    if not app.config['EXTRA_HSWAW']:
        return 404

    conn = connect_to_ldap()
    login,code = '', 401
    try:
        nick = re.sub(app.config['STRIP_RE'], '', request.form['nick'])
        res = conn.search_s(app.config['IRC_BASEDN'], ldap.SCOPE_SUBTREE, 
                app.config['IRC_LDAP_FILTER'] % nick)
        if len(res) == 1:
            login = res[0][1]['uid'][0]
            code = 200
    except ldap.LDAPError as e:
        print e
        code = 500
    return make_response(login, code, { 'Content-Type': 'text/plain' })

@app.route('/mifare', methods=['POST'])
def mifare():
    if not app.config['EXTRA_HSWAW']:
        return 404

    conn = connect_to_ldap()
    login,code = '', 401
    try:
        h = re.sub(app.config['STRIP_RE'], '', request.form['hash'])
        res = conn.search_s(app.config['MIFARE_BASEDN'], ldap.SCOPE_SUBTREE, 
                app.config['MIFARE_LDAP_FILTER'] % h)
        if len(res) == 1:
            login = res[0][1]['uid'][0]
            code = 200
    except ldap.LDAPError as e:
        print e
        code = 500
    return make_response(login, code, { 'Content-Type': 'text/plain' })

if __name__ == '__main__':
    app.run('0.0.0.0', 8082, debug=True)
