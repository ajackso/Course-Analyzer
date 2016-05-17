# Andrea Jackson and Kate Kenneally
# CS 249, Spring 2016
# Course Analyzer Final Project
# analyzer_app.py

from flask import Flask, render_template, request
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import SelectField, SubmitField, IntegerField
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

class ProfessorForm(Form):
    menu = [('blank', 'Choose a course!')]
    course_tups = [('CS'+str(tup[0]), 'CS'+str(tup[0])) for tup in sortcounts]
    menu.extend(course_tups)   
    choice = SelectField('', choices=menu)  
    enrollment = IntegerField(render_kw={"placeholder": "Enter course enrollment i.e. 25"})    
    year = IntegerField(render_kw={"placeholder": "Enter course year i.e. 2016"})                                                                                  
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
    
#generates a line graph of CS course enrollments
def generateLineGraph(csDF, choice): 
       data = go.Scatter(
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
                    shape='linear' # or vhv
                )
            )
            
       layout = go.Layout( title = "{} Course Enrollments, 2010-2016".format(choice),           
                xaxis = dict(                 
                title="Year"        
                ),
                yaxis = dict(                 
                title="Course enrollment"        
                )
            )  

       graph = go.Figure(data = [data], layout = layout)
       graphJSON = json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)
       return graphJSON
    
def getYearListStr(csDF):
    yearList = csDF.year.tolist()
    return [str(yr) for yr in yearList]
def generateBarGraph(csDF, choice):
    yearListStr = getYearListStr(csDF)
    data = [
            go.Bar(
            x = csDF.year.sum(),
            y = csDF.enrollment,
            text = "Prof. " + csDF.instructor + "<br>" + getTerm(csDF)+ " " + yearListStr,
            name = 'enrollment',
            marker=dict(
                color='rgb(121,186,233)'
            )
        ), #(15,117,188)
            go.Scatter(
                x = csDF.year.sum(),
                y=csDF.max_enrollment,
                name = "max enrollment",
                marker=dict(
                    color='rgb(15,117,188)'
                )
            ) 
        ]
        
    layout = go.Layout(          
                title = "{} course enrollments, 2010-2016".format(choice),  
                xaxis = dict( 
                    title="Year",
                    ticktext = yearListStr,
                    tickvals = range(len(yearListStr)),
                    tickangle=-45
                ),
                yaxis = dict(                 
                    title="Course enrollment"        
                )
            )
    graph = go.Figure(data = data, layout = layout)
    graphJSON = json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def generateStack(csDF, choice):
    csSpringDF = csDF[csDF.term == -0.1]
    csFallDF = csDF[csDF.term == 0.1]

    csDataSpring = go.Bar(
        x = csSpringDF.year,
        y = csSpringDF.enrollment,
        text = "Prof. " + csSpringDF.instructor,
        name = 'Spring Enrollment',
        marker=dict(
            color='rgb(15,117,188)'
        )
    )

    csDataFall = go.Bar(
        x = csFallDF.year,
        y = csFallDF.enrollment,
        text = "Prof. " + csFallDF.instructor,
        name = 'Fall Enrollment',
        marker=dict(
            color='rgb(121,186,233)'
        )
    )

    layout = go.Layout(          
        title = "{} course enrollments, 2010-2016".format(choice), 
        barmode = 'stack',
        xaxis = dict( 
            title="Year"
        ),
        yaxis = dict(                 
            title="Course enrollment"        
        ),
        bargap=0.1,
    )

    graph = go.Figure(data=[csDataFall, csDataSpring], layout=layout)
    graphJSON = json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
    
@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route('/professor', methods=['POST', 'GET'])
def professor():        
    choice = None
    enrollment = 0
    year = 0

    csCoursesDF = prepareData('csCoursesDF.pkl')
    csDF = generateCourseDF(csCoursesDF,"CS111")
    MIN = csDF.enrollment.min()
    MAX = csDF.enrollment.max()
    mean = csDF.enrollment.mean()
    lineGraphJSON = generateLineGraph(csDF, "CS111")
    barGraphJSON = generateBarGraph(csDF,"CS111")
    stackedBarJSON = generateStack(csDF,"CS111")
    
    form = ProfessorForm()
    if request.method == 'POST' and form.validate_on_submit():
        
        choice = form.choice.data
        enrollment = form.enrollment.data
        year = form.year.data

        if choice != "blank" and enrollment != 0 and year in csDF.year.unique().tolist():
            csDF = generateCourseDF(csCoursesDF,choice)
            MIN = csDF.enrollment.min()
            MAX = csDF.enrollment.max()
            mean = csDF.enrollment.mean()
            lineGraphJSON = generateLineGraph(csDF,choice)
            barGraphJSON = generateBarGraph(csDF,choice)
            stackedBarJSON = generateStack(csDF,choice)
            
    return render_template('professor.html', form=form, 
    choice=choice, enrollment = enrollment, year=year, lineGraphJSON=lineGraphJSON, 
    barGraphJSON = barGraphJSON, stackedBarJSON=stackedBarJSON, MIN = MIN, MAX = MAX, mean = mean)

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
    app.run(host = '0.0.0.0',port =8000, debug=True)