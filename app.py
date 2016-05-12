"""
Credits: This example is modified from one of the chapters in O'Reilly's
Intro to Flask books.
"""

from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import SelectField, SubmitField
#from wtforms.validators import Required, Length
import random, json, plotly
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
bootstrap = Bootstrap(app)



# The CS counts are real (counted them for each year), the others are randomly
# generated.
countsDct = {"CS":  [2, 4, 2, 12, 14, 10, 9, 4, 5, 2, 9, 1, 6, 5, 5, 20, 17, 9, 11, 16],
"ECON": [random.choice(range(1,31)) for i in range(20)], 
"MATH": [random.choice(range(1,21)) for i in range(20)],
"ART": [random.choice(range(1,21)) for i in range(10)] + [random.choice(range(1,15)) for i in range(10)]
}


# One can create more than one plot and store them in a list, which will be 
# turned into JSON to be passed to the client.
def make_bar_chart(choice):
    graphs = [
        dict(
            data=[
                dict(
                    x = range(1997,2017), # all the years from 1997 to 2016
                    y = countsDct[choice],
                    type = 'bar'
                ),
            ],
            layout=dict(
                title = choice + " students presenting at Ruhlman"
            )
        )
    ]
    # Convert the figures to JSON
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


class ChoiceForm(Form):
    #name = StringField('What is your name?', validators=[Required(), Length(1, 16)])
    
    choice = SelectField(u'Departments', choices=[("blank", "Make a choice"),
                                                  ('CS', 'Computer Science'), 
                                                  ('ECON', 'Economics'), 
                                                  ('MATH', 'Mathematics'),
                                                  ('ART', "Art Studio")])                                                    
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    
    choice = None
    ids = []
    graphJSON = []
    
    testDF = pd.DataFrame({'cs': [1,2,3]})
    
    form = ChoiceForm()
    if form.validate_on_submit():
        choice = form.choice.data
        if choice != "blank":
            graphJSON = make_bar_chart(choice)
            ids = ["Bar Chart for {}".format(choice)]
        form.choice.data = ''
    return render_template('index.html', form=form, choice=choice, 
                           graphJSON=graphJSON,
                           ids=ids, data = testDF.to_html())


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port = 9258)