from flask import Flask, render_template, request
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import SelectField, SubmitField
import random, json, plotly
import plotly.graph_objs as go
import pandas as pd
from pandas import DataFrame, Series
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
bootstrap = Bootstrap(app)

sortcounts = [('110', [21, 15, 15, 3, 3, 2, 1, 0]),
    ('111', [38, 65, 55, 25, 14, 5, 0, 0]),
    ('112', [0, 0, 0, 5, 0, 0, 0, 2]),
    ('114', [3, 0, 2, 0, 1, 0, 0, 0]),
    ('117', [4, 0, 3, 0, 2, 0, 0, 0]),
    ('118', [0, 4, 0, 0, 0, 0, 0, 0]),
    ('215', [0, 0, 4, 2, 18, 1, 9, 0]),
    ('220', [0, 2, 0, 28, 0, 16, 0, 17]),
    ('230', [6, 41, 80, 49, 29, 18, 6, 0]),
    ('231', [0, 0, 4, 38, 21, 65, 19, 20]),
    ('232', [0, 0, 4, 0, 15, 0, 14, 0]),
    ('235', [0, 0, 8, 7, 29, 9, 66, 22]),
    ('240', [1, 0, 35, 11, 63, 19, 41, 8]),
    ('242', [0, 0, 2, 13, 10, 8, 8, 7]),
    ('249', [0, 2, 0, 21, 0, 9, 0, 11]),
    ('251', [0, 1, 1, 34, 6, 50, 14, 40]),
    ('301', [0, 0, 0, 1, 0, 6, 0, 8]),
    ('304', [0, 0, 0, 11, 10, 48, 15, 43]),
    ('307', [0, 0, 4, 2, 22, 3, 26, 3]),
    ('310', [0, 0, 0, 0, 0, 6, 0, 5]),
    ('313', [0, 0, 0, 0, 6, 0, 15, 0]),
    ('315', [0, 0, 2, 9, 1, 16, 0, 12]),
    ('320', [0, 0, 10, 0, 15, 0, 37, 0]),
    ('322', [0, 0, 0, 0, 1, 0, 6, 0]),
    ('332', [0, 0, 0, 0, 12, 0, 5, 0]),
    ('342', [0, 0, 1, 0, 20, 7, 21, 10]),
    ('349', [0, 0, 0, 18, 0, 18, 0, 34])]

def make_heatmap():
    semesters = ['Semester '+str(num+1) for num in range(8)]
    cs_courses = ['CS'+str(tup[0]) for tup in sortcounts]
    zarray = [tup[1] for tup in sortcounts]
    colorscale = [[0, '#FFFFFF'], [1, '#5D00FF']]
        
    data = [
        go.Heatmap(
            x=semesters,
            y=cs_courses,
            z=zarray,
            colorscale=colorscale
        )
    ]
    
    layout = go.Layout(
        title = 'Timeline of Wellesley CS Course Enrollment (Majors/Minors)',
        yaxis = dict(dtick=1),
        height = 800,
        width = 800
    )
    
    fig = go.Figure(data=data, layout=layout)

    # Convert the figures to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
    
# professor section

class ChoiceForm(Form):    
    choice = SelectField(u'CS Courses', choices=[("blank", "Choose a CS course"),
                                                  ('CS111', 'CS 111'), 
                                                  ('CS230', 'CS 230')]) 
                                                                                                
    submit = SubmitField('Submit')
  
#creates a dataframe from a pickle and prepares the data
def prepareData(dataPkl):
    csCoursesDF = pd.read_pickle(dataPkl)
    csCoursesDF = csCoursesDF.replace(['S','F'],[-0.1,0.1])
    return csCoursesDF

#generates a dataframe containing the inputted cs course
def generateCourseDF(df, course):
    courseDF = df[df.courseid == course]
    courseDF = courseDF.sort_values(by = ['year', 'term'])
    return courseDF

#returns a list of Fall and Spring strings 
#to be used as labels for the data points
def getTerm(df):
    b = df.term > 0
    blist = ["Fall" if x > 0 else "Spring" for x in b]
    return blist
    
#generates a graph of CS course enrollments
def generateGraph(csDF, choice):
    graph = [ 
        dict( 
            data = [ 
            go.Scatter(
                x = csDF.year+csDF.term,
                y = csDF.enrollment,
                mode = 'markers+lines',
                marker=dict(
                size='16',
                color = 'rgb(67,129,179)',
                line = dict(
                width = 1,
                color = 'rgb(0, 0, 0)'
                    )
                ),
            text = "Prof. " + csDF.instructor + "<br>" + getTerm(csDF),
            textposition='left',
            line=dict(
                shape='vhv' # or linear
            )
        ) 
    ],

          layout = go.Layout( 
            title = "{} Course Enrollments, 2010-2016".format(choice),           
            xaxis = dict(                 
                title="Year"        
            ),
            yaxis = dict(                 
                title="Course enrollment"        
            )
        )  
      )
    ]
    graphJSON = json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
    
@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route('/professor', methods=['POST', 'GET'])
def professor():
    choice = None
    ids = []
    graphJSON = []
    form = ChoiceForm()
    if form.validate_on_submit():
        choice = form.choice.data
        if choice != "blank":
            csCoursesDF = prepareData('csCoursesDF.pkl') 
            csDF = generateCourseDF(csCoursesDF,choice)
            graphJSON = generateGraph(csDF, choice)
            ids = ["Timeline of Enrollments for course {}".format(choice)]
        form.choice.data = ''
    return render_template('professor.html', form=form, choice=choice, 
    graphJSON=graphJSON, ids=ids)

      
@app.route('/student', methods=['POST', 'GET'])
def student():
    graphJSON = make_heatmap()
    return render_template('student.html', graphJSON=graphJSON)

if __name__ == '__main__':
    app.run()