from flask import render_template, make_response
from email_validator import validate_email, EmailNotValidError

from ..utils.auth import create_jwt_token, hash_password
from ..db.users import email_exists_in_database, insert_user, check_login

@app.route("/login", methods = ["GET", "POST"])
def login():
    if (request.method == "GET"):
        return render_template("login.html")
    elif (request.method == "POST"):
        # Error checking 
        try:
            # Get the form data
            request_data = request.form
            email_address = request_data["email-address"].strip()
            password = request_data["password"].strip()

            if (email_address == "" or password == ""):
                #return render_template("login.html", incorrect_login=False, login_error=True), 400
                return {"error": "empty_email_or_password"}, 400
            
            # Check if the user is in the database with the given email and password
            user_id = check_login(email_address, password)
            if (user_id != -1):
                # If the user exists, create a new JWT token
                token = create_jwt_token(user_id)

                # Create a HTTP response
                response = make_response({"token": token}, 200)

                # Set the response headers
                response.headers["Content-Type"] = "application/json"
                response.headers["Access-Control-Allow-Credentials"] = "true"
                
                response.set_cookie("token", token, domain="192.168.1.162", httponly=True, secure=False, samesite='Lax', expires=time.time() + COOKIE_EXPIRY_TIME)  # Cookie expires in 48 hours

                # Use make_response here to use cookies
                return response
            
            else:
                #return render_template("login.html", incorrect_login=True, login_error=False), 401
                return {"error": "incorrect_email_or_password"}, 401

        except Exception as e:
            print(f"An error occurred during login: {str(e)}")
            #return render_template("login.html", incorrect_login=False, login_error=True), 500
            return {"error": "server_error"}, 500

@app.route("/signup", methods = ["GET", "POST"])
def signup():
    if (request.method == "GET"):
        return render_template("signup.html")
    
    elif (request.method == "POST"):
        # Error checking
        try:

            # Get request data from the form
            request_data = request.form
            email_address = request_data["email-address"].strip()
            password = request_data["password"].strip()

            if (not validateSignupData(email_address, password)):
                # Do something
                #return render_template("signup.html", email_exists_error=False, signup_error=True), 400
                return {"error": "invalid_email_or_password"}, 400
        
            # Check if the email is valid and can receive messages
            try:
                email_info = validate_email(email_address, check_deliverability=True)
                email_address = email_info.normalized

            except EmailNotValidError as e:
                print(str(e))
                #return render_template("signup.html", email_exists_error=False, signup_error=True), 400
                return {"error": "invalid_email"}, 400

            # Check for duplicate emails
            if (email_exists_in_database(email_address)):
                #return render_template("signup.html", email_exists_error=True, signup_error=False), 400
                return {"error": "duplicate_email"}, 400

            hashed_password = hash_password(password)

            # Inser the user into the database and get their UserID
            user_id = insert_user(email_address, hashed_password)
            print("User signed up successfully")

            if (user_id == -1):
                print("An error occurred while signing up")
                return {"error": "server_error"}, 500
            else:
                # Create a new JWT token for the user
                token = create_jwt_token(user_id)

                # Make a HTTP response
                response = make_response({"token": token}, 200)

                # Set headers
                response.headers["Content-Type"] = "application/json"
                response.headers["Access-Control-Allow-Credentials"] = "true"

                # Add a cookie to the response
                response.set_cookie("token", token, domain="192.168.1.162", httponly=True, secure=False, samesite='Lax', expires=time.time() + COOKIE_EXPIRY_TIME)

                return response
                #return {"token": token}, 200


        except Exception as e:
            print(f"An error occurred during signup: {str(e)}")
            #return render_template("signup.html", email_exists_error=False, signup_error=True), 500
            return {"error": "server_error"}, 500