from flask import Flask, render_template, request, url_for, redirect, session
from flask_pymongo import PyMongo
from watchlist import *
import bcrypt

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'connect_test'
app.config['MONGO_URI'] = 'mongodb://Albert:stocksstocksstocks@ds161016.mlab.com:61016/financewebapp' # figure out how to hide username and password

app.secret_key = 'mysecret'

mongo = PyMongo(app)

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'username':request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            session['watchlist'] = [Stock(symbol).__dict__ for symbol in login_user['watchlist']]
        else:
            return 'Invalid username/password combination'
    else:
        return 'Invalid username/password combination'

    session['watchlist'] = sorted(session['watchlist'], key=lambda x: x['week_percent_change'], reverse=True)

    return redirect(url_for('watchlist'))

@app.route('/watchlist')
def watchlist():
    session['watchlist'] = sorted(session['watchlist'], key=lambda x: x['week_percent_change'], reverse=True)
    wlist = session['watchlist']
    best = session['watchlist'][0:5]
    worst = reversed(session['watchlist'][-5:])

    return render_template('watchlist.html', watchlist=wlist, fiveBest=best, fiveWorst=worst)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/confirm_registration', methods=['POST'])
def confirm_registration():
    users = mongo.db.users
    existing_user = users.find_one({'username' : request.form['username']})

    if existing_user is None:
        hashed_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
    else:
        return 'That username already exists'

    if request.form['password'] == request.form['confirm']:
        users.insert({
            'name': request.form['name'],
            'email': request.form['email'],
            'username': request.form['username'],
            'password': hashed_password,
            'watchlist': []
        })
    else:
        return 'The passwords did not match'

    return redirect(url_for('home_page')) # get the user back to the homepage to log in

@app.route('/addStock', methods=['POST'])
def add_stock():
    # add stock to session watchlist
    symbol = request.form['symbol'].upper()
    newStock = Stock(symbol)

    if newStock.week_percent_change is None:
        return symbol.upper() + " is either not a valid stock symbol or is not available"

    currentList = session['watchlist']

    # make sure the stock is not already on the user's watchlist
    for stock in currentList:
        if stock['companySymbol'] == symbol:
            return symbol + " is already on your watchlist"

    currentList.append(newStock.__dict__)
    session['watchlist'] = currentList

    # add stock to mongodb watchlist
    users = mongo.db.users
    current_user = users.find_one({'username' : session['username']})
    users.update({'_id' : current_user['_id']}, {'$push': {'watchlist': symbol}})

    return redirect(url_for('watchlist'))

@app.route('/removeStock', methods=['POST'])
def remove_stock():
    # add stock to session watchlist
    symbol = request.form['symbol'].upper()
    currentList = session['watchlist']
    for stock in currentList:
        if stock['companySymbol'] == symbol:
            currentList.remove(stock)

    session['watchlist'] = currentList

    # remove stock from mongodb watchlist
    users = mongo.db.users
    current_user = users.find_one({'username' : session['username']})
    users.update({'_id' : current_user['_id']}, {'$pull': {'watchlist': symbol}})

    return redirect(url_for('watchlist'))

if __name__ == '__main__':
    app.run()
