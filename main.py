import datetime

from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from forms import UserForm, CreateTodoForm, DeleteTodo
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

# Successfully installed SQLAlchemy-1.4.46 flask-sqlalchemy-3.0.2 greenlet-2.0.1

app = Flask(__name__)
Bootstrap(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_port = os.getenv('DB_PORT')
db_pass = os.getenv('DB_PASS')

postgres_path = os.environ.get('DB_URL', f'postgresql://{db_user}:{db_pass}@{db_port}/{db_name}')

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_DATABASE_URI'] = postgres_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

day = date.today()
today = day.strftime("%m/%d/%Y")


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    date_reg = db.Column(db.String(50))
    todos = relationship('Todo', backref='owner')


class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    todo = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.String(50))
    completion = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def home():
    form = UserForm()
    create_form = CreateTodoForm()

    username = form.username.data
    # user = User.query.get(username)
    if form.validate_on_submit():
        if username is None or username == "":
            with app.app_context():
                user = db.session.query(User).all()
                num = len(user) + 1
                user_name = f'guest_{num}'
                new_guest = User(username=user_name, date_reg=today)
                db.session.add(new_guest)
                db.session.commit()
            user_access = User.query.filter_by(username=user_name).first()
            flash(f'Welcome!')
            return redirect(url_for('create_todo', user_id=user_access.id))
        else:
            user = User.query.filter_by(username=username).first()
            if user and user.username is not None:
                flash(f'Welcome back!')
            else:
                with app.app_context():
                    new_user = User(username=username, date_reg=today)
                    db.session.add(new_user)
                    db.session.commit()
                first_login = User.query.filter_by(username=username).first()
                flash(f'Welcome!')
                return redirect(url_for('create_todo', user_id=first_login.id))
        return redirect(url_for('create_todo', user_id=user.id))
    #     return render_template('index.html', show_form=False, name=username, create_form=create_form)

    return render_template('index.html', form=form, show_form=True, name=username, create_form=False, delete=False, day=day.year)


@app.route('/create_todo/<int:user_id>', methods=['GET', 'POST'])
def create_todo(user_id):
    form = CreateTodoForm()
    login_form = UserForm()
    delete_form = DeleteTodo()

    todo = form.todo.data
    due_date = form.due_date.data
    completed = form.completed.data

    user = User.query.get(user_id)
    user_todo = Todo.query.filter_by(user_id=user.id).all()

    if form.validate_on_submit():
        if completed == 'Done':
            completed = True
        elif completed == 'Pending':
            completed = False
        with app.app_context():
            new_todo = Todo(todo=todo, deadline=due_date, completion=completed, user_id=user_id)
            db.session.add(new_todo)
            db.session.commit()
        return redirect(url_for('create_todo', user_id=user.id))

    return render_template('index.html', show_form=False, form=login_form, name=user.username, create_form=form,
                           user_todo=user_todo, done='Done ✅', pending='Pending ⏸', edit=False, show_delete=False,
                           delete=delete_form, day=day.year)
# pending='⏸'


@app.route("/edit_todo/<int:todo_id>", methods=['GET', 'POST'])
def edit_todo(todo_id):
    todo = Todo.query.get(todo_id)
    todo_date = datetime.datetime.strptime(todo.deadline, '%Y-%m-%d')
    # todo_deadline = todo_date.strftime()

    form = CreateTodoForm(todo=todo.todo, due_date=todo_date, completed=todo.completion)
    login_form = UserForm()
    delete_form = DeleteTodo()

    user = User.query.get(todo.user_id)
    user_todo = Todo.query.filter_by(user_id=user.id).all()
    if form.validate_on_submit():
        if form.completed.data == 'Done':
            todo.completion = True
        elif form.completed.data == 'Pending':
            todo.completion = False
        todo.todo = form.todo.data
        todo.deadline = form.due_date.data
        # todo.completion = form.completed.data
        db.session.commit()
        return redirect(url_for('create_todo', user_id=todo.user_id))
    if delete_form.validate_on_submit():
        todo_to_delete = Todo.query.get(todo_id)
        db.session.delete(todo_to_delete)
        db.session.commit()
        return redirect(url_for('create_todo', user_id=user.id))
    return render_template('index.html', show_form=False, form=login_form, name=user.username, create_form=form,
                           user_todo=user_todo, done='Done ✅', pending='Pending ⏸', edit=True, show_delete=True,
                           delete=delete_form, day=day.year)


if __name__ == '__main__':
    app.run()
