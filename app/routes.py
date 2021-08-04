import os
from flask import current_app as app
from flask import render_template, Flask, request, redirect, url_for, Blueprint, render_template, redirect, url_for, session
from flask.helpers import flash
from flask_user import login_required, current_user
from flask_user.forms import RegisterForm, LoginForm
from flask import send_from_directory 
from .models import User

UserDict = dict()

@app.route("/")
def home():
    """Landing page."""
    return render_template(
        "index.jinja2",
        title="Timelogger visualisation",
        description="Timelogger visualisation using Dash embedded in Flask.",
        template="home-template",
        body="This is a homepage served with Flask.",
    )

@app.route('/dash/')
def dash():
        return render_template('dash/dash.jinja2')

@app.route('/favicon.ico') 
def favicon():     
    return app.send_static_file('favicon.ico')