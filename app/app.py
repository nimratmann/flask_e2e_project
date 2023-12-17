from datetime import datetime, timedelta
from functools import wraps
import os
import pathlib
import requests
from flask import Flask, abort, flash, redirect, session,request,render_template
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import logging



logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

load_dotenv()
db = SQLAlchemy()

class Prescription(db.Model):
    __tablename__ = 'prescription' 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    medicine_name = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(150),nullable=False)
    instructions = db.Column(db.String(250),nullable=False)
    createdAt=db.Column(db.DateTime(timezone=True), default=func.now())
    doctor=db.Column(db.String(150),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='prescriptions')


class User(db.Model):
    __tablename__ = 'user' 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150),nullable=False)
    last_name = db.Column(db.String(150),nullable=False)
    age = db.Column(db.Integer)
    prescriptions = db.relationship("Prescription", back_populates='user')


app=Flask(__name__)
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
DB_USERNAME=os.getenv('DB_USERNAME')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_HOST=os.getenv('DB_HOST')
DB_NAME=os.getenv('DB_NAME')
ssl_ca = os.path.join(pathlib.Path(__file__).parent,"DigiCertGlobalRootCA.crt.pem")
try:
    db_uri = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?ssl_ca={ssl_ca}"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    app.permanent_session_lifetime=timedelta(minutes=5)
    db.init_app(app)
    with app.app_context():
        db.create_all()

except Exception as e:
    print(f"Error setting up the database connection: {e}")
    raise
    



app.secret_key="THISISASECRET"
#temporary disable hhtps check
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
# OAuth
client_secrets_file = os.path.join(pathlib.Path(__file__).parent,"client_secret.json")

# Create a Flow instance from the client secrets file
flow = Flow.from_client_secrets_file(
    client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid", "https://www.googleapis.com/auth/user.gender.read", "https://www.googleapis.com/auth/user.birthday.read"],
    redirect_uri= 'https://5000-cs-60048718044-default.cs-us-east1-pkhd.cloudshell.dev/callback'  
)

def login_is_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        return function()
    return wrapper

@app.route("/")
def home():
   return render_template("home.html")
 
 
@app.route("/login")
def login():
    if "google_id" not in session:
        authorization_url, state = flow.authorization_url()
        session["state"] = state
        return redirect(authorization_url)
    else:
        return redirect("/prescription")

def calculate_age(birthdate):
    if birthdate:
        # Calculate age based on birthdate
        birthdate = datetime.strptime(birthdate, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age
    else:
        # Handle the case where birthdate is None (you can choose an appropriate default value)
        return 23


# Helper function to get the user's profile picture URL
def get_user_profile_picture(access_token):
    profile_pic_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        params={"access_token": access_token}
    )
    profile_pic_data = profile_pic_response.json()
    return profile_pic_data.get("picture")

@app.route("/callback", methods=['GET', 'POST'])
def callback():
    try:
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        request_session = requests.session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(session=cached_session)

        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID
        )
   
        # Check if the user already exists in the database
        user = User.query.filter_by(email=id_info.get("email")).first()  # Use .first() to get the first result
        
        app.logger.info('failed to log in: %s', user)
        # If the user does not exist, create a new user
        if not user:
            new_user = User(
                email=id_info.get("email"),
                first_name=id_info.get("given_name"),
                last_name=id_info.get("family_name"),
                age=calculate_age(id_info.get("birthdate")))           
            db.session.add(new_user)
            db.session.commit()
        profile_pic_url = get_user_profile_picture(credentials.token)
        session["google_id"] = id_info.get("sub")
        session["name"] = id_info.get("name")
        session["email"] = id_info.get("email")
        session["profile_pic"] = profile_pic_url
        flash("Login successful!",category="success")
        
        # Redirect to the prescription route
        return redirect("/prescription")
    except Exception as e:
        print(f"Error setting up the database connection: {e}")
        raise

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
 
 
@app.route("/prescription",methods=['GET','POST'])
@login_is_required
def renderPresciption():
    if "google_id" in session:
        name=session["name"]
        email=session["email"]
        profile_pic =session["profile_pic"]
        user = User.query.filter_by(email=email).first()
        prescriptions = Prescription.query.filter(Prescription.user.has(id=user.id)).all()
        return render_template("prescription.html",prescriptions=prescriptions,name=name,profile_pic=profile_pic)
    else:
        flash("You are not logged in!",category="error")
        return redirect("/")
    
@app.route("/aboutus",methods=['GET','POST'])
def renderAboutus():
    return render_template("about.html")
       
    
@app.route("/services",methods=['GET','POST'])
def renderServices():
    return render_template("services.html")
    
@app.route("/contactUs",methods=['GET','POST'])
def renderContactUs():
    return render_template("contactUs.html")
    
   

@app.route("/prescription/add",methods=['GET','POST'])
@login_is_required
def addPrescription():
    if "google_id" in session:
        email = session["email"]
        profile_pic =session["profile_pic"]
        name=session["name"]
        user = User.query.filter_by(email=email).first()
        if request.method=="POST":
            medicine_name = request.form.get('medicineName')
            instructions = request.form.get('instructions')
            dosage = request.form.get('dosage')
            doctor = request.form.get('doctor')
            
            new_prescription = Prescription(
                medicine_name=medicine_name,
                dosage=dosage,
                instructions=instructions,
                doctor=doctor,
                user=user
            )
            db.session.add(new_prescription)
            db.session.commit()

            flash("Prescription added successfully!",category="success")
            return redirect('/prescription')

        else:
            return render_template("addPrescription.html",name=name,profile_pic=profile_pic)
    else:
        flash("You are not logged in!",category="error")
        return redirect("/login")
    
@app.route('/delete_prescription/<int:prescription_id>', methods=['POST'])
def delete_prescription(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)

    # Delete the prescription
    db.session.delete(prescription)
    db.session.commit()

    # Redirect to the main page or wherever you want after deletion
    return redirect('/prescription')


@app.route("/update_prescription/<int:prescription_id>", methods=['GET', 'POST'])
@login_is_required
def updatePrescription():
    if "google_id" in session:
        name=session["name"]
        profile_pic =session["profile_pic"]
        if request.method == "POST" and request.form.get('prescription_id'):
            prescription_id = request.form.get('prescription_id')
            # Store prescription_id in the session
            session["prescription_id"] = prescription_id
            existing_prescription = Prescription.query.get(prescription_id)
            return render_template("updatePrescription.html", prescription=existing_prescription,name=name,profile_pic=profile_pic)
        
        elif request.method == "POST":
            prescription_id = session["prescription_id"]
            existing_prescription = Prescription.query.get(prescription_id)
            existing_prescription.medicine_name = request.form.get('medicineName')
            existing_prescription.instructions = request.form.get('instructions')
            existing_prescription.dosage = request.form.get('dosage')
            existing_prescription.doctor = request.form.get('doctor')

            db.session.commit()

            flash("Prescription updated successfully!",category="success")
            return redirect('/prescription')

    else:
        flash("You are not logged in!",category="error")
        return redirect("/login")




if __name__=='__main__':
  app.run(host="0.0.0.0",debug=True)

