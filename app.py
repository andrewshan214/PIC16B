from flask import Flask, render_template, request
from flask import redirect, url_for, abort
from flask import g
import sqlite3

app = Flask(__name__)
DATABASE = 'messages_db.sqlite'

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'message_db'):
        g.message_db.close()


@app.route('/')
def base():
    return render_template('base.html')


@app.route('/insert_msg/', methods=['POST'])
def insert_message(request):
    # get message and handle from request
    try:
        message = request.form['message']
        handle = request.form['name']

        db = get_message_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO messages (handle, message) VALUES (?, ?)", (handle, message))
        db.commit()

        return redirect('/submit/')
    except Exception as e:
        return render_template('submit.html', error=True)


@app.route('/submit/', methods=['GET', 'POST'])
def submit_message():
    #different methods for diff request methods
    if request.method == 'GET':
        #if 'GET' just render the template
        return render_template('submit.html')
    
    else:
        try:
            handle, message = insert_message(request)
            #render the template with a thank you note
            return render_template('submit.html', thank_you = True, message = message, handle = handle)
        except:
            return render_template('submit.html', error=True)
    
@app.route('/random_messages/<int:n>')
def random_message(n):
    db = get_message_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM messages ORDER BY RANDOM() LIMIT ?", (n,))
    messages = cursor.fetchall()
    return render_template('view.html', messages=messages)


@app.route('/random_messages/')
def render_view_template():
    messages = random_message(5)

    return render_template('view.html', messages = messages)


@app.route('/getmsg/', methods=['GET'])
def get_message_db():

    #try to retrieve database connection from global g object
    try:
        db = g.message_db
    except AttributeError:
        db = g.message_db = sqlite3.connect(DATABASE)
        db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                handle TEXT,
                message TEXT
            )
        ''')
    return db

if __name__ == '__main__':
    app.run(debug=True)
