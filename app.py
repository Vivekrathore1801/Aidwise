import secrets
from bson import ObjectId
from flask import Flask,render_template,request,redirect,url_for,session
from flask_pymongo import PyMongo
from werkzeug.security import check_password_hash, generate_password_hash
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = secrets.token_hex(16)

app.config["MONGO_URI"] = "mongodb://localhost:27017/my_database"
mongo = PyMongo(app)


@app.route('/')
def welcome():
     
    return render_template('welcome.html')

@socketio.on('message')
def handle_message(msg):
    # Save message to MongoDB
    mongo.db.chat_messages.insert_one({'message': msg})
    # Broadcast the message to all connected clients
    socketio.emit('message', msg)



@app.route('/login.html',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the email exists in the database
        user= mongo.db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            # If the user exists and the password is correct, log them in
            session['user_id'] = str(user['_id'])
            return render_template('chat.html')
        else:
            return "Invalid email or password. Please try again."

    # Handle GET requests
    return render_template('login.html')
    
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        # Get user data from the database based on the session user_id
        user = mongo.db.user.find_one({'_id': ObjectId(session['user_id'])})

        if user:
            # Display user's dashboard
            return f"Welcome, {user['email']}! This is your dashboard."
        else:
            return "User not found."
    else:
        return redirect(url_for('welcome'))

@app.route('/signup.html', methods=['GET','POST'])
def signup():
 if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # # Check if the email already exists in the database
        if mongo.db.users.find_one({'email': email}):
            return "Email already exists. Please choose another email."
        
         # Hash the password before storing it
        hashed_password = generate_password_hash(password)


        # Insert the user data into MongoDB
        user_data = {'email': email, 'password': hashed_password}
        mongo.db.users.insert_one(user_data)

        return "Signup successful! You can now log in."
        
  # Handle GET requests
 return render_template('signup.html')

@app.route('/chat')
def chat():
   return render_template('msg.html')


  
if __name__=="__main__":
    socketio.run(app,debug=True,port=5001)