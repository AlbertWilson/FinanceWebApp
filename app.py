from flask import Flask, render_template, request, url_for, redirect, session
from flask_pymongo import PyMongo
from watchlist import *
import bcrypt

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'connect_test'
app.config['MONGO_URI'] = 'mongodb://Albert:stocksstocksstocks@ds161016.mlab.com:61016/financewebapp' # figure out how to hide username and password

mongo = PyMongo(app)

user = None

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name':request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
            global user
            user = User(request.form['username'])
            user.watchlist = [Stock(symbol) for symbol in login_user['watchlist']]
        else:
            return 'Invalid username/password combination'
    else:
        return 'Invalid username/password combination'

    user.sort_watchlist()
    return redirect(url_for('watchlist'))

@app.route('/watchlist')
def watchlist():
    global user
    return render_template('watchlist.html', watchlist=user.watchlist, fiveBest=user.five_best_performers(), fiveWorst=user.five_worst_performers())

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/confirm_registration', methods=['POST'])
def confirm_registration():
    users = mongo.db.users # create a new collection called users
    existing_user = users.find_one({'name' : request.form['username']})

    if existing_user is None:
        hashed_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
    else:
        return 'That username already exists'

    if request.form['password'] == request.form['confirm']:
        users.insert({'name' : request.form['username'], 'password': hashed_password, 'watchlist': []})
    else:
        return 'The passwords did not match'

    print('successfully created')

    return redirect(url_for('home_page')) # get the user back to the homepage to log in

@app.route('/addStock', methods=['POST'])
def add_stock():
    symbol = request.form['symbol']
    global User
    user.insert_stock(symbol)
    user.sort_watchlist()

    # add stock to mongodb watchlist
    users = mongo.db.users

    current_user = users.find_one({'name' : user.username})
    users.update({'_id' : current_user['_id']}, {'$push': {'watchlist': symbol}})


    return redirect(url_for('watchlist'))

@app.route('/removeStock', methods=['POST'])
def remove_stock():
    symbol = request.form['symbol']
    global user
    user.remove_stock(symbol)

    # remove stock from mongodb watchlist
    users = mongo.db.users

    current_user = users.find_one({'name' : user.username})
    users.update({'_id' : current_user['_id']}, {'$pull': {'watchlist': symbol}})

    return redirect(url_for('watchlist'))


if __name__ == '__main__':
    app.run()
