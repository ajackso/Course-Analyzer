# Andrea Jackson and Kate Kenneally
# CS 249, Spring 2016
# Course Analyzer Final Project
# analyzer_app.py

from flask import Flask, render_template, request
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import SelectField, SubmitField
import json, plotly
import plotly.graph_objs as go
from course_info import sortcounts
from course_info import descdict
import pandas as pd
from pandas import DataFrame, Series
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
bootstrap = Bootstrap(app)

def make_heatmap():
    semesters = ['Semester '+str(num+1) for num in range(8)]
    cs_courses = ['CS'+str(tup[0]) for tup in sortcounts]
    zarray = [tup[1] for tup in sortcounts]
    colorscale = [[0, '#FFFFFF'], [1, '#0052fa']]
        
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
        height = 550,
        width = 550
    )
    
    fig = go.Figure(data=data, layout=layout)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
    
def make_custom_heatmap(choice): 
    semesters = ['Semester '+str(num+1) for num in range(8)]
    cs_courses = ['CS'+str(tup[0]) for tup in sortcounts]
    colorscale = [[0, '#FFFFFF'], [1, descdict[choice]['color']]]
    
    zarray = []
    
    for i in range(len(cs_courses)):
        if cs_courses[i]==choice:
            zarray.insert(i,sortcounts[i][1])
        else:
            zarray.append([0 for i in range(8)])
    
    data = [
        go.Heatmap(
            x=semesters,
            y=cs_courses,
            z=zarray,
            colorscale=colorscale
        )
    ]
    
    layout = go.Layout(
        title = 'Timeline of ' + choice + ' Enrollment (Majors/Minors)',
        yaxis = dict(dtick=1),
        height = 550,
        width = 550
    )
    
    fig = go.Figure(data=data, layout=layout)
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
    
class StudentForm(Form):
    menu = [('blank', 'Choose a course!')]
    course_tups = [('CS'+str(tup[0]), 'CS'+str(tup[0])) for tup in sortcounts]
    menu.extend(course_tups)
    choice = SelectField('', choices=menu)
    submit = SubmitField('Submit')

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
    choice = None
    text = 'The graph to the left is a heatmap containing data for all CS \
        courses offered at Wellesley between Fall 2010 and Spring 2016. \
        The deeper the color, the more students took the course during that \
        particular semester (as displayed on the x-axis). Semester 4, for \
        example, means the course was taken during the Spring semester of \
        sophomore year.'     
    current = 'This data is pretty overwhelming when viewed all at once, \
        so we invite you to select a course from the drop-down menu to view \
        its data alone. You\'ll also receive a brief description (from \
        Wellesley\'s course browser), as well as some helpful information \
        about major/minor requirements, Fall 2016 offerings, etc.'       
    majreq = 'Navigating the CS major or minor at Wellesley can be intimidating, \
        but we hope this application makes things a little easier!'    
    title, minreq, req200, req300, minpickone = '', '', '', '', ''
    form = StudentForm()
    if form.validate_on_submit():
        choice = form.choice.data
        if choice != "blank":
            title = descdict[choice].get('title','')
            text = descdict[choice].get('text','')
            current = descdict[choice].get('current','This course is NOT offered \
            for the Fall 2016 semester.')
            majreq = descdict[choice].get('majreq','')
            minreq = descdict[choice].get('minreq','')
            req200 = descdict[choice].get('req200','')
            req300 = descdict[choice].get('req300','')
            minpickone = descdict[choice].get('minpickone','')
            graphJSON = make_custom_heatmap(choice)
            form.choice.data = ''
    return render_template('student.html', form=form, choice=choice, title=title, 
        text=text, current=current, majreq=majreq, minreq=minreq, req200=req200,
        req300=req300, minpickone=minpickone, graphJSON=graphJSON)

if __name__ == '__main__':
    app.run()