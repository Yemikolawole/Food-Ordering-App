#!/usr/bin/env python3
from flask import Flask,render_template,redirect,request,url_for,flash
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import smtplib, ssl
from datetime import datetime,date
from sqlalchemy import desc


app = Flask(__name__)

## Database
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///data.db'
app.config["SECRET_KEY"] = '12345'
db = SQLAlchemy(app)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key = True,autoincrement=True)
    username = db.Column(db.String(100),nullable = False,unique = True)
    email = db.Column(db.String(100),nullable = False,unique = True)
    password = db.Column(db.String(500),nullable = False)
    
class Order(db.Model):
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    order_id = db.Column(db.Integer,nullable = False,primary_key = True)
    order_category = db.Column(db.String(90),nullable = False)
    order_price = db.Column(db.Integer,nullable = False)
    order_address = db.Column(db.String(80),nullable = False)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# landing page
@app.route('/')
def index():
    return render_template('landingPage.html')

# main page
@app.route('/home')
@login_required
def home():
    return render_template('home.html')

# login page
@app.route('/login',methods = ["POST","GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email = email).first()
        if user:
            if bcrypt.check_password_hash(user.password,password):
                login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')
    
# Signup page
@app.route('/signup',methods = ["POST","GET"])
def signup():
    if request.method == "POST":
        try:
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            hash_password = bcrypt.generate_password_hash(password)
            user = User(username = username,email = email,
                                        password = hash_password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
    return render_template("signup.html")

@app.route('/order',methods = ["POST","GET"])
@login_required
def order():
    if request.method == "POST":
        user = current_user.id
        food_category = request.form["order_name"]
        food_price = request.form["order_price"]
        food_address = request.form["order_address"]
        user_order = Order(user_id = user,order_category=food_category,
                           order_price = food_price,
                           order_address = food_address)
        db.session.add(user_order)
        db.session.commit()
        confirm_order()
        return redirect(url_for('home'))
    return render_template('order.html')

def confirm_order():
    #smtp code
    current_email = current_user.email
    #Email lists you want to send email to
    mailer_list=[current_email]
    
    #Sender email
    sender_mail='yemi.kol26@gmail.com'

    for i in mailer_list:

        #Createing a secure SSL context
        context = ssl.create_default_context()

        #SSL port
        port = 465

        #Creating SMTP session
        s = smtplib.SMTP_SSL('smtp.gmail.com', port,context=context)

        #Sender login
        s.login(sender_mail, "bhbkheemmnokasne")
        order_no = db.session.query(Order).order_by(desc(Order.order_id)).first()
        
        # for current date
        today = date.today()
        current_day = today.strftime("%B %d, %Y")
        
        # for current time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        SUBJECT =  f"Order No:{str(order_no)}"
        TEXT = f"Your order is confirmed\nDate: {current_day} Time: {current_time}"
        message = 'Subject: {}\n\n{}'.format(SUBJECT,TEXT)
        #Sending mail to the mailer list
        s.sendmail(sender_mail, i, message)
        
        #Closing the instance
        s.quit()

@app.route('/logout',methods = ["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)














