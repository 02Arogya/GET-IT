
import os
from flask import Flask,render_template,url_for,redirect,request,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import Form, StringField, PasswordField, SubmitField, IntegerField,TextAreaField, validators,BooleanField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'DEMO/static'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///database1.db"
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'Login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Tables #

class User(db.Model,UserMixin):
    __tablename__ = "User"
    def get_id(self):
           return (self.User_id)
    User_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable = False,unique = True)
    password=db.Column(db.String(30), nullable = False, unique = False)

    def delete_to_cart(self,User_email):
        item_to_delete = Cart(User_email=User_email, User_id=self.id)
        db.session.delete(item_to_delete)
        db.session.commit()
        flash('Your item has been delete to your cart!', 'success')


    def add_to_cart(self,Prod_id):
        item_to_add = Cart(Prod_id=Prod_id, user_id=self.User_id)
        db.session.add(item_to_add)
        db.session.commit()
        flash('Your item has been added to your cart!', 'success')

# Forms #

class RegisterForm(FlaskForm):
    username = StringField("Username",validators=[InputRequired(), Length(min=4, max=20)])
    Email = StringField("Email",validators=[InputRequired()])
    Mobile = StringField("Mobile No", validators=[InputRequired(), Length(min=10,max=10)])
    password = PasswordField('Password',validators=[InputRequired(), Length(min=8, max=20)])
    Confirm_password = PasswordField('Confrim Password',validators=[InputRequired(), Length(min=8, max=20)])
    Address = StringField("Address",validators=[InputRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            flash('That username already exists. Please choose a different one.')
            raise ValidationError('That username already exists. Please choose a different one.')
    
   
class LoginForm(FlaskForm):
    username = StringField("Username",validators=[InputRequired(), Length(min=4, max=20)])

    password = PasswordField('Password',validators=[InputRequired(), Length(min=8, max=20)])

    submit = SubmitField('Login')

# class Employee(db.Model):
#    employee_id = db.Column(db.Integer, primary_key = True),
#    employee_name = db.Column(db.String, nullable = False)


################# Routes  ########################################################################################################################
@app.route('/')
def home():
    prod = Prod.query.all()
    return render_template('Home.html',prod=prod)


@app.route('/Register',methods=['GET','POST'])
def Register():
    form=RegisterForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash("Username not available")
        
        hashed_password= bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("You have registered Succesfully ")
        return redirect(url_for('Login'))
    
    return render_template('Register.html',form=form)

@app.route('/Login', methods =['GET','POST'])
def Login():
    form= LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash(f' Welcome {form.username.data}, You Logged In Successfully')
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid username or password")        
    return render_template('Login.html',form=form)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Prod_id = db.Column(db.Integer, db.ForeignKey('Prod.Prod_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    Carte= Cart.query.all()
    return render_template('dashboard.html',Carte=Carte)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('Login'))




### Add Product ####################################################################################################################################

class Prod(db.Model):
    __tablename__ = "Prod"
    def get_id(self):
           return (self.Prod_id)
    Prod_id = db.Column(db.Integer, primary_key = True)
    Prod_name = db.Column(db.String(20), nullable = False)
    Prod_Cost=db.Column(db.Integer, nullable = False)

class category(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    Category = db.Column(db.String(20),unique=True, nullable = False)
   


@app.route('/Category',methods=['GET','POST'])
def AddCategory():
    if request.method == 'POST':
        id = request.form["id"]
        category_name= request.form["category"]
        newcat = category(id = id, Category= category_name)
        db.session.add(newcat)
        db.session.commit()
        flash(f'Category Added success','success') 
        
    return render_template('Addcategory.html')

@app.route('/<string:Prod_id>/delete',methods=['GET','POST'])
def Delete(Prod_id):
    prod =Prod.query.filter_by(Prod_id=Prod_id).first()
    if request.method == 'POST':
        if prod:
            db.session.delete(prod)
            db.session.commit()
        flash(f'Product Deleted success','success')
        return redirect(url_for('Update'))


    return render_template('Delete.html',prod=prod)


@app.route('/<string:Prod_id>/Edit',methods=['GET','POST'])
def Edit(Prod_id):
    prod =Prod.query.filter_by(Prod_id=Prod_id).first()
    if request.method == 'POST':
        Data = Prod.query.filter_by(Prod_id=Prod_id).first()
        Data.Prod_name = request.form["ProdName"]
        Data.Prod_Cost = request.form["Prod_Cost"] 
        db.session.commit()
        file = request.files['file']    
            
        if file.filename != '': 
            file.filename = "product"+ Prod_id+ ".jpg"
            file.save(f'static/{file.filename}')
        
        flash(f'Product Updated success','success') 
        return redirect(url_for('Update'))
    
    return render_template('Edit.html',prod=prod)

@app.route('/Update',methods=['GET','POST'])
def Update():
    prod =Prod.query.all()
    Category = category.query.all()       
    if request.method == 'POST':
        file = request.files['file']
        Prod_id =   request.form["Name"]
        file.filename = "product"+ Prod_id+ ".jpg"
        file.save(f'static/{file.filename}')
        Prod_id =   request.form["Name"]
        Prod_name =  request.form["Prod_name"]
        Prod_Cost=   request.form["Prod_Cost"]
        newprod = Prod(Prod_id=Prod_id, Prod_name=Prod_name, Prod_Cost=Prod_Cost)
        db.session.add(newprod)
        db.session.commit()
        flash(f'Product Added success','success') 
        return redirect(url_for('Update'))

    
    return render_template('Update.html',Category=Category,prod=prod)


######## CART #############################################################################################################

##class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('Prod.Prod_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    

def getLoginDetails():
    if current_user.is_authenticated:
        noOfItems = Cart.query.filter_by(user_id =(current_user.User_id)).count()
    else:
        noOfItems = 0
    return noOfItems


  

@app.route("/addToCart/<string:Prod_id>/")
@login_required
def addToCart(Prod_id):
    # check if product is already in cart
    
    row = Cart.query.filter_by(Prod_id=Prod_id, user_id =(current_user.User_id)).first()
   
    
    if row:
        # if in cart update quantity : +1
        row.quantity += 1
        db.session.commit()
        flash('This item is already in your cart, 1 quantity added!', 'success')
        return redirect(url_for('cart'))
        # if not, add item to cart
    else:
       
        user = User.query.get((current_user.User_id))
        user.add_to_cart(Prod_id)
        return redirect(url_for('home'))



@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    noOfItems = getLoginDetails()
    # display items in cart
    cart = Prod.query.join(Cart).add_columns(Cart.quantity, Prod.Prod_Cost, Prod.Prod_name, Prod.Prod_id).filter_by(user_id =(current_user.User_id)).all()
    subtotal = 0
    for item in cart:
        subtotal+=int(item.Prod_Cost)*int(item.quantity)

    if request.method == "POST":
        qty = request.form.get("qty")
        idpd = request.form.get("idpd")
        cartitem = Cart.query.filter_by(Prod_id=idpd).first()
        cartitem.quantity = qty
        db.session.commit()
        cart = Prod.query.join(Cart).add_columns(Cart.quantity, Prod.Prod_Cost, Prod.Prod_name, Prod.Prod_id).filter_by(user_id =(current_user.User_id)).all()
        subtotal = 0
        for item in cart:
            subtotal+=int(item.price)*int(item.quantity)
    return render_template('dashboard.html', Carte=cart, noOfItems=noOfItems, subtotal=subtotal)

@app.route("/removeFromCart/<string:Prod_id>")
@login_required
def removeFromCart(Prod_id):
    item_to_remove = Cart.query.filter_by(Prod_id=Prod_id, user_id =(current_user.User_id)).first()

    if item_to_remove.quantity >1:
        # if in cart update quantity : +1
        item_to_remove.quantity -= 1
        db.session.commit()
        flash('This item is removed in your cart, 1 quantity deleted!', 'success')
    ###for item in item_to_remove:
    else:
        db.session.delete(item_to_remove)
        db.session.commit()    
        flash('Your item has been removed from your cart!', 'success')
    return redirect(url_for('cart'))

###Search####
@app.route("/Search")
def Search():
    if request.method == "POST":
        product=request.form["product"]
        prod = Prod.query.filter_by(Prod_name=product).all()
        

    return render_template('Home.html',prod=prod )
        

if __name__=='__main__':
    app.run(debug=True)

