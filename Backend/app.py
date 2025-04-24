import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__, template_folder="templates", static_folder="statics")
CORS(app)
load_dotenv()
#configurations
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance.db"
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
app.config["JWT_SECRET_KEY"] = "your_jwt_secret"

db = SQLAlchemy(app)
jwt = JWTManager(app)

#database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship("User", backref=db.backref("transactions", lazy=True))

class Categroy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=False)


#routes
@app.route('/')
def home():
  return render_template('index.html')  

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
      data = request.get_json()

      if not data or not all(k in data for k in ["email", "password"]):
          return jsonify({"error": "Missing email or password"}), 400

      user = User.query.filter_by(email=data['email']).first()

      if not user or not check_password_hash(user.password, data['password']):
          return jsonify({"error": "Invalid credentials"}), 401

      access_token = create_access_token(identity=user.id)
      return jsonify({"access_token": access_token, "user_id": user.id}), 200
    return render_template('login.html')

#POST new user creation and GET redirect
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
      
      data = request.get_json()
      hashed_pw = generate_password_hash(data['password'])
      new_user = User(
          username=data["username"], 
          email=data["email"], 
          password=hashed_pw
     )
      db.session.add(new_user)
      db.session.commit()
      return jsonify({"message": "User registered!"})
    return render_template('register.html')

# Show all transactions
@app.route('/transactions', methods=['GET'])
def transactions_page():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template('transactions.html', transactions=transactions)

# Add new transaction (form)
@app.route('/transactions/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        description = request.form['description']

        new_tx = Transaction(
            user_id=1, 
            amount=amount,
            category=category,
            description=description
        )
        db.session.add(new_tx)
        db.session.commit()
        return redirect(url_for('transactions_page'))

    return render_template('add_transaction.html')

# View a single transaction
@app.route('/transactions/<int:transaction_id>', methods=['GET'])
def view_transaction(transaction_id):
    tx = Transaction.query.get_or_404(transaction_id)
    return render_template('view_transaction.html', transaction=tx)

# Edit a transaction
@app.route('/transactions/<int:transaction_id>/edit', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    tx = Transaction.query.get_or_404(transaction_id)
    if request.method == 'POST':
        tx.amount = request.form['amount']
        tx.category = request.form['category']
        tx.description = request.form['description']
        db.session.commit()
        return redirect(url_for('transactions_page'))
    return render_template('edit_transaction.html', transaction=tx)

# Delete a transaction
@app.route('/transactions/<int:transaction_id>/delete', methods=['POST'])
def delete_transaction(transaction_id):
    tx = Transaction.query.get_or_404(transaction_id)
    db.session.delete(tx)
    db.session.commit()
    return redirect(url_for('transactions_page'))


if __name__ == "__main__":
    app.run(debug=True)