import ldap
import re
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

@app.route('/irc', methods=['GET'])
def irc_form():
    return render_template('irc.html')

@app.route('/irc', methods=['POST'])
def irc_nick():
    conn = ldap.initialize(app.config['LDAP_URL'])
    conn.start_tls_s()
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

if __name__ == '__main__':
    app.run('0.0.0.0', 8082, debug=True)
