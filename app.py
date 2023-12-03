import os

import datetime 

import sqlite3 
from flask import Flask, flash, request, render_template, redirect, jsonify, session
from flask_session import Session 
from tempfile import mkdtemp
# from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
# from helpers import apology, login_required, lookup, usd 
from helpers import login_required, lookup

#Configure application 
app = Flask(__name__)

# Ensure templates are auto-reloaded 
app.config["TEMPLATES_AUTO_RELOAD"] = True 

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#Custom filter

# app.jinja_env.filters["usd"] = usd !

# Configure session to use filesystem (instead of signed cookies)
app.config ["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)  

# Connecting out database

con = sqlite3.connect("finance.db")
cur = con.cursor()

# for guests


# Make sure API is set !
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY isn't set")

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    con = sqlite3.connect("finance.db")
    cur = con.cursor()
    id = session["user_id"]
    userdata = cur.execute("SELECT * FROM user WHERE id = :id", [id]).fetchall()
    userCash = userdata[0][3]
    userShares = [userdata[0][4]]

    if userShares[0] is None:
        return render_template("main.html", userdata=userdata, cash=userCash)
    else: 

        resUserFilteredShares = userShares[0].split(",")

        moneyOfAllShares = userCash

        check = []

        for share in resUserFilteredShares:
                if len(share) > 4:
                    symbol = share.split(" ")[3]
                    count = share.split("?")[1]
                    if lookup(symbol) is None:
                        return render_template("apology.html", message="Our data server is broken, please wait a few minutes", userdata=userdata)
                    dataOfShare = lookup(symbol)
                    price = dataOfShare["price"]
                    moneyOfAllShares = moneyOfAllShares + (float(price) * float(count))
            

        return render_template("main.html", userdata=userdata, cash=userCash, shares= resUserFilteredShares, moneyOfAllShares = moneyOfAllShares, check = check)

        # zalupa
        # |
        # ↓
        # resUserFilteredShares = []
        # for j in range(len(userShares[0].split(","))):
        #     c = [i.split(",")[j] for i in userShares]
        # for share in c:
        #     resUserFilteredShares.append(share)


        # return render_template("main.html", userdata=userdata, cash=userCash, shares= resUserFilteredShares)
        
        # resUserFilteredShares = []
        # for j in range(len(userShares[0].split(","))):
        #     c = [i.split(",")[j] for i in resUserFilteredShares]
        # for share in c:
        #     resUserFilteredShares.append(share)
        # return render_template("main.html", userdata=userdata, cash=userCash, shares= resUserFilteredShares)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():

    # Forget any user_id
    session.clear()

    if request.method == "GET":
        return render_template("login.html")
    else: 
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", message="Please, write a username")
        
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", message="Please, write a password")
        
        con = sqlite3.connect("finance.db")
        cur = con.cursor()

        rows = cur.execute("SELECT * FROM user WHERE username = :username", [request.form.get("username")]).fetchall()

        # return render_template("info.html", rows=rows)

        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return render_template("invalUSER.html", message="Invalid username or password")
        
        session["user_id"] = rows[0][0]

        return redirect("/")
        




@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        #checking is username input incorrect
        if not request.form.get("username"):
            return render_template("apology.html", message="Write a username")
        #checking is password input incorrect
        if not request.form.get("reg-password1") or not request.form.get("reg-password2"):
            return render_template("apology.html", message="Write a password")
        
        con = sqlite3.connect("finance.db")
        cur = con.cursor()
        
        rows = cur.execute("SELECT * FROM user WHERE username = :username", [request.form.get("username")]).fetchall()

        if len(rows) != 0:
            return render_template("apology.html", message="This name is already taken")
        
        username = request.form.get("username")
        if check_password_hash(request.form.get("reg-password1"), request.form.get("reg-password2")):
            return render_template("apology.html", message="Your passwords are not match")
        else:
            data = {"username": username, "hash": generate_password_hash(request.form.get("reg-password1"))}
            cur.execute("INSERT INTO user(username,hash) VALUES (:username, :hash)", data)
            con.commit()
            return redirect("/login")
        
@app.route("/quote", methods=["GET","POST"])
@login_required
def quote():
    
    con = sqlite3.connect("finance.db")
    cur = con.cursor()
    id = session["user_id"]
    userdata = cur.execute("SELECT * FROM user WHERE id = :id", [id]).fetchall()
    if request.method == "GET":
        return render_template("quote.html", userdata=userdata, symbol=[])
    else: 
        symbol = request.form.get("symbol")
        if lookup(symbol) is None:
            return render_template("apology.html", message="You have written a wrong share", userdata=userdata)
        symdata  = lookup(symbol)
        return render_template("quoteRes.html", userdata=userdata, symdata=symdata, name=symdata["name"], price=symdata["price"], symbol=symdata["symbol"])
        return render_template("quote.html", userdata=userdata, symdata=symdata, name=symdata["name"] or "", price = symdata["price"] or "", symbol=symdata["symbol"] or "")

@app.route("/buy", methods=["GET","POST"])
@login_required
def buy():

    
    con = sqlite3.connect("finance.db")
    cur = con.cursor()
    id = session["user_id"]
    userdata = cur.execute("SELECT * FROM user WHERE id = :id", [id]).fetchall()

    if request.method == "GET":
        return render_template("buy.html", userdata=userdata)
    else:
        shareSym = request.form.get("shareName")
        shareCount = request.form.get("shareCount")
        if not shareSym or not shareCount or int(shareCount) < 1:
            return render_template("apology.html", message="You have written a wrong name or incorrect value", userdata=userdata)
        # if int(shareCount) < 1:
        #     return render_template("apology.html", message="You have written zero value OR negative", userdata=userdata)
        symdata  = lookup(shareSym)

        if lookup(shareSym) is None:
            return render_template("apology.html", message="You have written a wrong share", userdata=userdata)
        
        shareCost = symdata["price"]
        cash = userdata[0][3]
        totalCostOfShares = (float(shareCost) * float(shareCount))
        remainingMoney = float(cash) - totalCostOfShares
        timeOfBuyingOfShare = datetime.datetime.now()

        previousDataShares = userdata[0][4]
        data = {"cash": remainingMoney, "shares": f"{previousDataShares}, %{timeOfBuyingOfShare}% {shareSym} !{symdata["name"]}! ?{shareCount}? /{shareCost}/ ^{totalCostOfShares}^", "id": id}
        
        # cur.execute("INSERT INTO user(cash, shares) WHERE id = :id VALUES (:cash, :shares)", data)
        cur.execute("UPDATE user SET cash = :cash, shares = :shares WHERE id = :id", data)
        con.commit()
        return redirect("/")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    # connecting the database
    con = sqlite3.connect("finance.db")
    cur = con.cursor()
    id = session["user_id"]
    userData = cur.execute("SELECT * FROM user WHERE id = :id", [id]).fetchall()
    userShares = userData[0][4]

    #loading the page
    if request.method == "GET":
        userShares = [userData[0][4]]
        userFilteredShares = userShares[0].split(",")

        return render_template("sell.html", userdata= userData, shares = userFilteredShares)
    
    else:
        sellCount = request.form.get("sellCount")
        # If the user wrote the correct value of the shares 
        if sellCount == "" or int(sellCount) < 1:
            return render_template("apology.html", message="You have written the wrong number of shares!", userdata = userData)


        selectedShare = request.form.get("shares")
        
        if selectedShare == "Please, choose your shares":
            render_template("apology.html", message="You have chosen the share!", userdata = userData)

        selectedShareSymbol = selectedShare.split(" ")[3]
        selectedShareCount = selectedShare.split("?")[1]
        # sueta = int(selectedShareCount) - int(sellCount)
        # return render_template("info.html", check = sueta)
        
        # If user want sell more shares than he has & How many shares are left after the sale
        newCountOfShares = int(selectedShareCount) - int(sellCount)
        if newCountOfShares < 0:
            return render_template("apology.html", message="You can't sell more shares than you have", userdata = userData)
        
        # Checking how much share is cost right now
        dataOfSymbol = lookup(selectedShareSymbol)
        price = dataOfSymbol["price"]
  
        # Calculating how much money the user will have after the sell
        userCash = userData[0][3]
        moneyFromSoldShares = float(price) * int(sellCount)
        currentCountOfMoney = userCash + moneyFromSoldShares

        # Creating var which hold the edited count of share
        changedCountOfShares = selectedShare.replace(f"?{selectedShareCount}?", f"?{newCountOfShares}?")
        newShareData = userShares.replace(selectedShare, changedCountOfShares)

        # Adding the edited share to database
        changeDbShares = {"cash": currentCountOfMoney, "shares": newShareData}
        
        
        # userSharesSplitted = userShares.split(",")
        # for share in userSharesSplitted:
        #     if share == f" {selectedShare}":
        #        return

        # return render_template("info.html", check = changeDbShares, something = userShares)
    
        cur.execute("UPDATE user SET cash = :cash, shares = :shares", changeDbShares)
        con.commit()
        return redirect("/")
    
