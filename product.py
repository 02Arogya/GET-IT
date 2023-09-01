from app import *
from flask_wtf 
class Prod(db.Model,UserMixin):
    def get_id(self):
           return (self.Prod_id)
    Prod_id = db.Column(db.Integer, primary_key = True)
    Prod_name = db.Column(db.String(20), nullable = False)
    Prod_Cost=db.Column(db.Integer, nullable = False)

class UpdateForm(Form):
    Prod_id = StringField("Prod_id",validators=[InputRequired(), Length(min=4, max=20)])
    Prod_name =  StringField("Prod_name",validators=[InputRequired(), Length(min=4, max=20)])
    Prod_Cost=   StringField("Prod_Cost",validators=[InputRequired(), Length(min=4, max=20)])

   
    submit = SubmitField('Update ')

@app.route('/Update',methods=['GET','POST'])
def Update():
    form=UpdateForm()
    newprod = Prod(Prod_id=form.Prod_id.data, Prod_name=form.Prod_name.data, Prod_Cost=form.Prod_Cost.data)
    db.session.add(newprod)
    db.session.commit()
   
    
    return render_template('Update.html',form=form)