# -*- coding: utf-8 -*-
from flask import render_template, session

# local import
from webapp import app
from webapp.api.v1.Pricing import Pricing

@app.before_first_request
def startup():
    # load the pricing data - the position of the json file is in the config.py
    Pricing.load_from_json()


@app.route('/')
def index():
    session['user_locale'] = 'en'
    return render_template('index.html')
