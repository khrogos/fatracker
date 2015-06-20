import sqlite3
import pygal
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
import time

app = Flask(__name__)
app.config.from_object('settings')

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def gen_chart():
    goal_data = []

    # get database data
    cur = g.db.execute('select ts_date, weight from entries order by id asc')
    entries = [dict(date=row[0], weight=row[1]) for row in cur.fetchall()]
    if len(entries) > 60:
        entries = entries[:59]
    for i in entries:
        goal_data.append(app.config['GOAL'])

    chart = pygal.Line(disable_xml_declaration=True)
    chart.title = "Weight evolution"
    dates = ["-".join(unicode(entry['date']).split(" ")[0].split("-")[1:]) for entry in entries ]
    chart.x_labels = (map(str, dates))
    chart.add('Weight', [ entry['weight'] for entry in entries ])
    chart.add('goal', goal_data)

    return chart.render(disable_xml_declaration=True)


@app.route('/')
def show_entries():
    cur = g.db.execute('select ts_date, weight from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    cur_date = time.strftime("%Y-%m-%d")
    return render_template('index.html', entries=gen_chart(), today=cur_date)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    
    g.db.execute('insert into entries (ts_date, weight) values (?, ?)',
                 [request.form['ts_date'], request.form['weight']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')


