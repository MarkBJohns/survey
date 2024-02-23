from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret"

dubug = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return render_template('index.html')

from surveys import satisfaction_survey

# responses = []

@app.route('/questions/0')
def init_survery():
    session['survey_questions'] = [q.question for q in satisfaction_survey.questions]
    session['responses'] = []
    return redirect(url_for('ask_questions', num = 1))

@app.route('/questions/<int:num>', methods=['GET'])
def ask_questions(num):
    responses = session.get('responses', [])
    if num != len(responses) + 1:
        flash(f"You must answer question {len(responses) + 1} before proceeding.")
        return redirect(url_for('ask_questions', num=len(responses) + 1))
    question = session['survey_questions'][num-1]
    choices = satisfaction_survey.questions[num-1].choices
    return render_template('questions.html', question=question, num=num, choices=choices)

@app.route('/questions/answer', methods=['POST'])
def log_answer():
    answer = request.form['answer']
    num = int(request.form['num'])
    responses = session.get('responses', [])
    responses.append(answer)
    session['responses'] = responses
    session.modified = True
    if num < len(session['survey_questions']):
        return redirect(url_for('ask_questions', num=num+1))
    else:
        return redirect(url_for('survey_thank_you'))
    
@app.route('/thanks')
def survey_thank_you():
    qa_pairs = zip(session['survey_questions'], session['responses'])
    return render_template('thanks.html', qa_pairs=qa_pairs)

# account for manually trying to move through the survery (typing questions/7 or whatever in the url bar) by redirecting to the
#   approprite page, use the length of survery_questions:

#       if len(survey_questions) is 4, then the num in questions/num should depend on the length of 'results' in relation to 4

#       for example, if you've answered one question, the length of 'results' will be 1, so if you try to move to questions/5,
#           it redirects to len(results)+1 

# add flash messages to account for trying to skip a question, explaining to the user that you can't