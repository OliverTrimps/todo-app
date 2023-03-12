from flask_wtf import FlaskForm
from wtforms import BooleanField, TextAreaField, SubmitField, StringField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, InputRequired
from datetime import date

# Successfully installed WTForms-3.0.1 flask-wtf-1.1.1

day = date.today()
today = day.strftime("%m/%d/%Y")


class UserForm(FlaskForm):
    # guest_user = HiddenField(label="guest user")
    username = StringField(label=' Enter Username')
    submit = SubmitField("Let's Begin")


class CreateTodoForm(FlaskForm):
    todo = TextAreaField(label='What to do?', validators=[DataRequired()])
    due_date = DateField(label="Due Date", validators=[InputRequired(), DataRequired()], format='%m-%d-%Y', default=today)
    # completed = BooleanField(label='Completed?', default=False, render_kw={'checked': ''})
    completed = SelectField(label='Todo Status', choices=['Done', 'Pending'], default='Pending')
    submit = SubmitField(label='Finish')


class DeleteTodo(FlaskForm):
    # id_todo = HiddenField(validators=[DataRequired()])
    submit = SubmitField('Delete Todo')
