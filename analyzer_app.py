# Andrea Jackson and Kate Kenneally
# CS 249, Spring 2016
# Course Analyzer Final Project
# analyzer_app.py

from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import SelectField, SubmitField
import json, plotly
import plotly.graph_objs as go
from course_info import sortcounts
from course_info import descdict

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
    
@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route('/professor', methods=['POST', 'GET'])
def professor():
    return render_template('professor.html')
    
@app.route('/student', methods=['POST', 'GET'])
def student():
    graphJSON = make_heatmap()
    choice = None
    title, text, current, majreq, minreq, req200, req300, minpickone = '', '', '', '', '', '', '', ''
    form = StudentForm()
    if form.validate_on_submit():
        choice = form.choice.data
        if choice != "blank":
            title = descdict[choice].get('title','')
            text = descdict[choice].get('text','')
            current = descdict[choice].get('current','This course is NOT offered for the Fall 2016 semester.')
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