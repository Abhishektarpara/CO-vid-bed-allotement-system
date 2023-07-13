from flask import Flask,render_template,flash,request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import json
from flask.helpers import url_for

from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import logout_user,login_user,login_required,login_manager,current_user,LoginManager
from flask import Flask, json,redirect,render_template,flash,request



#database connection
local_server=True   
app=Flask(__name__)
app.secret_key="abhi"

#for unique user login
login_manager=LoginManager(app)
login_manager.login_view='login'


# app.config["SQLALCHEMY_DATABASE_URI"]='mysql://username:password@localhost/databasename'
app.config["SQLALCHEMY_DATABASE_URI"]='mysql://root:@localhost/covid'
db=SQLAlchemy(app) 
    
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) or hospitaluser.query.get(int(user_id))

class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(20),unique=True)
    email=db.Column(db.String(20),unique=True)
    password=db.Column(db.String(20))
    
class hospitaluser(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20),unique=True)
    email=db.Column(db.String(200),unique=True)
    password=db.Column(db.String(2000))
    
class Hospitaldata(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(100),unique=True)
    hname=db.Column(db.String(100))
    normalbed=db.Column(db.Integer)
    hicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)
    
class Bookingpatient(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(20),unique=True)
    bedtype=db.Column(db.String(100))
    hcode=db.Column(db.String(20))
    spo2=db.Column(db.Integer)
    pname=db.Column(db.String(100))
    pphone=db.Column(db.String(100))
    paddress=db.Column(db.String(100))

class Trig(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20))
    normalbed=db.Column(db.Integer)
    hicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)
    querys=db.Column(db.String(20))
    date=db.Column(db.String(20))

with open('backend\config.json','r') as c:
    params = json.load(c)["params"]
    
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/usersignup")
def usersignup(): 
    return render_template("usersignup.html")

@app.route("/userlogin")
def userlogin(): 
    return render_template("userlogin.html")

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=='POST':
        srfid=request.form.get('srf')
        email=request.form.get('email')
        password=request.form.get('password')
        if len(password) < 8:
            flash("Password must be at least 8 characters long", "warning")
            return render_template("usersignup.html")
        encpass=generate_password_hash(password)
        user=User.query.filter_by(srfid=srfid).first()
        emailUser=User.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or srif is already taken","warning")
            return render_template("usersignup.html")
        # new_user=db.engine.execute(f"INSERT INTO `user` (`srfid`,`email`,`dob`) VALUES ('{srfid}','{email}','{encpassword}') ")
        new_user=User(srfid=srfid,email=email,password=encpass)
        db.session.add(new_user)
        db.session.commit()
                
        flash("SignUp Success Please Login","success")
        return render_template("userlogin.html")
        # new_user=db.engine.execute(f"INSERT INTO `user` (`srfid`,`email`,`password`) VALUES('{srfid}','{email}','{encpass}') ")
        # return 'USER ADDED' 
        
    return render_template("usersignup.html")

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        srfid=request.form.get('srf')
        password=request.form.get('password')
        user=User.query.filter_by(srfid=srfid).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")

    return render_template("userlogin.html")

@app.route('/hospitallogin',methods=['POST','GET'])
def hospitallogin():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=hospitaluser.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("hospitallogin.html")


    return render_template("hospitallogin.html")


@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if(username==params['user'] and password==params['password']):
            session['user']=username
            flash("login success","info")
            return render_template("addhospitaluser.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("admin.html")
    return render_template("admin.html")

@app.route('/addhospitaluser',methods=['POST','GET'])
def hospitalUser():
    if('user' in session and session['user']=="admin"):
        if request.method=="POST":
            hcode=request.form.get('hcode')
            email=request.form.get('email')
            password=request.form.get('password')        
            encpassword=generate_password_hash(password)  
            hcode=hcode.upper()      
            emailUser=hospitaluser.query.filter_by(email=email).first()
            if  emailUser:
                flash("Email is already taken","warning")
            # db.engine.execute(f"INSERT INTO `hospitaluser` (`hcode`,`email`,`password`) VALUES ('{hcode}','{email}','{encpassword}') ")
            query=hospitaluser(hcode=hcode,email=email,password=encpassword)
            db.session.add(query)
            db.session.commit()
            # my mail starts from here if you not need to send mail comment the below line
            # mail.send_message('COVID CARE CENTER',sender=params['gmail-user'],recipients=[email],body=f"Welcome thanks for choosing us\nYour Login Credentials Are:\n Email Address: {email}\nPassword: {password}\n\nHospital Code {hcode}\n\n Do not share your password\n\n\nThank You..." )
            flash("Data Sent and Inserted Successfully","warning")
            return redirect("/hospitallogin")
  
    else:
        flash("Login and try Again","warning")
        return redirect("/admin")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))

@app.route('/logoutadmin')
@login_required
def logoutadmin():
    session.pop('user')
    flash("you are logout admin","primary")
    return redirect('/admin') 

@app.route("/addhospitalinfo",methods=['POST','GET'])
def addhospitalinfo():
    email=current_user.email
    posts=hospitaluser.query.filter_by(email=email).first()
    code=posts.hcode
    postsdata=Hospitaldata.query.filter_by(hcode=code).first()

    if request.method=="POST":
        hcode=request.form.get('hcode')
        hname=request.form.get('hname')
        nbed=request.form.get('normalbed')
        hbed=request.form.get('hicubeds')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        hcode=hcode.upper()
        huser=hospitaluser.query.filter_by(hcode=hcode).first()
        hduser=Hospitaldata.query.filter_by(hcode=hcode).first()
        if hduser:
            flash("Data is already Present you can update it..","primary")
            return render_template("hospitaldata.html")
        if huser:            
            # db.engine.execute(f"INSERT INTO `hospitaldata` (`hcode`,`hname`,`normalbed`,`hicubed`,`icubed`,`vbed`) VALUES ('{hcode}','{hname}','{nbed}','{hbed}','{ibed}','{vbed}')")
            query=Hospitaldata(hcode=hcode,hname=hname,normalbed=nbed,hicubed=hbed,icubed=ibed,vbed=vbed)
            db.session.add(query)
            db.session.commit()
            flash("Data Is Added","primary")
            return redirect('/addhospitalinfo')
        else:
            flash("Hospital Code not Exist","warning")
            return redirect('/addhospitalinfo')
    return render_template("hospitaldata.html",postsdata=postsdata)

@app.route("/hedit/<string:id>",methods=['POST','GET'])
@login_required
def hedit(id):
    posts=Hospitaldata.query.filter_by(id=id).first()
  
    if request.method=="POST":
        hcode=request.form.get('hcode')
        hname=request.form.get('hname')
        nbed=request.form.get('normalbed')
        hbed=request.form.get('hicubeds')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        hcode=hcode.upper()
        # db.engine.execute(f"UPDATE `hospitaldata` SET `hcode` ='{hcode}',`hname`='{hname}',`normalbed`='{nbed}',`hicubed`='{hbed}',`icubed`='{ibed}',`vbed`='{vbed}' WHERE `hospitaldata`.`id`={id}")
        post=Hospitaldata.query.filter_by(id=id).first()
        post.hcode=hcode
        post.hname=hname
        post.normalbed=nbed
        post.hicubed=hbed
        post.icubed=ibed
        post.vbed=vbed
        db.session.commit()
        flash("Slot Updated","info")
        return redirect("/addhospitalinfo")

    # posts=Hospitaldata.query.filter_by(id=id).first()
    return render_template("hedit.html",posts=posts)

@app.route("/hdelete/<string:id>",methods=['POST','GET'])
@login_required
def hdelete(id):
    # db.engine.execute(f"DELETE FROM `hospitaldata` WHERE `hospitaldata`.`id`={id}")
    post=Hospitaldata.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    flash("Date Deleted","danger")
    return redirect("/addhospitalinfo")

@app.route("/pdetails",methods=['GET'])
@login_required
def pdetails():
    code=current_user.srfid
    print(code)
    data=Bookingpatient.query.filter_by(srfid=code).first()
    return render_template("details.html",data=data)


def updatess(code):
    postsdata=Hospitaldata.query.filter_by(hcode=code).first()
    return render_template("hospitaldata.html",postsdata=postsdata)


@app.route("/slotbooking",methods=['POST','GET'])
@login_required
def slotbooking():
    # query1=db.engine.execute(f"SELECT * FROM `hospitaldata` ")
    # query=db.engine.execute(f"SELECT * FROM `hospitaldata` ")
    query1=Hospitaldata.query.all()
    query=Hospitaldata.query.all()
    if request.method=="POST":
        
        srfid=request.form.get('srfid')
        bedtype=request.form.get('bedtype')
        hcode=request.form.get('hcode')
        spo2=request.form.get('spo2')
        pname=request.form.get('pname')
        pphone=request.form.get('pphone')
        paddress=request.form.get('paddress')  
        check2=Hospitaldata.query.filter_by(hcode=hcode).first()
        checkpatient=Bookingpatient.query.filter_by(srfid=srfid).first()
        if checkpatient:
            flash("already srd id is registered ","warning")
            return render_template("booking.html",query=query,query1=query1)
        
        if not check2:
            flash("Hospital Code not exist","warning")
            return render_template("booking.html",query=query,query1=query1)

        code=hcode
        # dbb=db.engine.execute(f"SELECT * FROM `hospitaldata` WHERE `hospitaldata`.`hcode`='{code}' ")  
        dbb=Hospitaldata.query.filter_by(hcode=hcode).first()   
        bedtype=bedtype
        if bedtype=="normalbed":       
            for d in dbb:
                seat=d.normalbed
                print(seat)
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.normalbed=seat-1
                db.session.commit()
                
            
        elif bedtype=="hicubed":      
            for d in dbb:
                seat=d.hicubed
                print(seat)
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.hicubed=seat-1
                db.session.commit()

        elif bedtype=="icubed":     
            for d in dbb:
                seat=d.icubed
                print(seat)
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.icubed=seat-1
                db.session.commit()

        elif bedtype=="vbed": 
            for d in dbb:
                seat=d.vbed
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.vbed=seat-1
                db.session.commit()
        else:
            pass

        check=Hospitaldata.query.filter_by(hcode=hcode).first()
        if check!=None:
            if(seat>0 and check):
                res=Bookingpatient(srfid=srfid,bedtype=bedtype,hcode=hcode,spo2=spo2,pname=pname,pphone=pphone,paddress=paddress)
                db.session.add(res)
                db.session.commit()
                flash("Slot is Booked kindly Visit Hospital for Further Procedure","success")
                return render_template("booking.html",query=query,query1=query1)
            else:
                flash("Something Went Wrong","danger")
                return render_template("booking.html",query=query,query1=query1)
        else:
            flash("Give the proper hospital Code","info")
            return render_template("booking.html",query=query,query1=query1)
            
    
    return render_template("booking.html",query=query,query1=query1)

@app.route("/trigers")
def trigers():
    query=Trig.query.all() 
    return render_template("trigers.html",query=query)




#testing whether database is connected or not
@app.route("/test")
def test():
    try:
        a=Test.query.all()
        print(a)
        return f"database is connected successfully{a}"
    except Exception as e:
        print(e)
        return f"Error{e}"


app.run(debug=True)

