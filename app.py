import os

from pytrends.request import TrendReq

import pandas as pd
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from flask_sqlalchemy import SQLAlchemy
from flask import (
    Flask,
    session,
    render_template,
    jsonify)

from amz_etsy import scrape

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'

# Login to Google. 
# Only need to run this once,
# The rest of requests will use the same session.

pytrend = TrendReq()
countries_df = pd.read_csv("static/csv/countries.csv")


#################################################
# Database Setup
#################################################

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///static/db/top_trends.db"
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(db.engine, reflect=True)

# Save references to each table
initTime = Base.classes.time
initRegion = Base.classes.region
initCategories = Base.classes.categories
initAmz = Base.classes.amazon
initEtsy = Base.classes.etsy
initMonthRev = Base.classes.monthly_revenue_h10
initTotalRev = Base.classes.total_revenue_h10
initSearch = Base.classes.search


#################################################
# Flask Routes
#################################################

# home/landing page 
@app.route("/")
def home():
    """Render Home Page."""
    return render_template("index.html")

# route to view map
@app.route("/viewMap")
def view_map():
    return render_template("viewMap.html")

# route to local visualizations
@app.route("/local")
def local_view():
    return render_template("local.html")

# =========================================================================================== #
# ------------------------------routes to raw data in json form------------------------------ #
# =========================================================================================== #

# home route data
@app.route("/init")
def init():
    # Use Pandas to perform the sql query
    time_stmt = db.session.query(initTime).statement
    time_df = pd.read_sql_query(time_stmt, db.session.bind)
    time_data = {
        "date": time_df.date.values.tolist(),
        "taco": time_df.tacos.values.tolist(),
        "sandwich": time_df.sandwiches.values.tolist(),
        "kebab": time_df.kebabs.values.tolist()
    }

    session['keywords'] = ['tacos','sandwiches','kebabs']

    # Results
    return jsonify(time_data)

# google trends  
@app.route("/live_trends/<inputValue>")
def interest_over_time_data(inputValue):
    """Return live_trends data for the keywords"""

    # Pytrends API pull
    keywords = inputValue
    keywords = keywords.split(sep=',')
    pytrend.build_payload(kw_list=keywords)
    time_df = pytrend.interest_over_time()
    time_df.reset_index(inplace=True)
    time_data = {"date": time_df.date.tolist()}
    for phrase in keywords:
        time_data[phrase] = time_df[phrase].values.tolist()

    session['keywords'] = keywords

    return jsonify(time_data)

# region data
@app.route("/region")
def interest_by_region_data():
    keywords =  session.get('keywords', None)
    pytrend.build_payload(kw_list=keywords)
        # Interest By region
    region_df = pytrend.interest_by_region()
    region_df['total'] = region_df.sum(axis=1)
    region_filtered_df = region_df[region_df['total']>0]
    region_loc_df = pd.merge(region_filtered_df, countries_df, how="inner", left_on="geoName", right_on="name")
    region_loc_df = region_loc_df.drop(columns=['name','total'])
    region_loc_df.reset_index(inplace=True)
    region_loc_data = []
    for index, row in region_loc_df.iterrows():
        region_loc_data.append(
            row.to_dict()
        )
    return jsonify(region_loc_data)
# mass data
@app.route("/mass_data/<inputValue>")
def mass_scrape(inputValue):
    try:
        # parse input terms
        keyword = inputValue

        keywords = keyword.split(sep=',')
        keywords = [x.strip() for x in keywords]

        class_call = scrape(keywords)
        list_df = class_call.all_test(keywords)

        amazon_req = list_df[0].reset_index()
        revenue_req = list_df[1].reset_index()
        product_data_req = list_df[2].reset_index()
        etsy_req = list_df[3].reset_index()
        
        search_data = {}
        amazon_data = {}
        total_rev_data = {}
        monthly_rev_data = {}
        etsy_data = {}
        # search
        # search_data['search_term'] = search_req['search_term'].values.tolist()
        # amazon
        amazon_data['search_term'] = amazon_req['search_term'].values.tolist()
        amazon_data['product_name'] = amazon_req['product_name'].values.tolist()
        amazon_data['product_price'] = amazon_req['product_price'].values.tolist()
        # helium total revenue
        total_rev_data['search_term'] = revenue_req['search_term'].values.tolist()
        total_rev_data['revenue_specs'] = revenue_req['revenue_specs'].values.tolist()
        total_rev_data['revenue_value'] = revenue_req['revenue_value'].values.tolist()
        # helium monthly revenure by product
        monthly_rev_data['search_term'] = product_data_req['search_term'].values.tolist()
        monthly_rev_data['monthly_product'] = product_data_req['monthly_product'].values.tolist()
        monthly_rev_data['monthly_price'] = product_data_req['monthly_price'].values.tolist()
        monthly_rev_data['monthly_sales'] = product_data_req['monthly_sales'].values.tolist()
        monthly_rev_data['monthly_revenue'] = product_data_req['monthly_revenue'].values.tolist()
        # etsy
        etsy_data['search_term'] = etsy_req['search_term'].values.tolist()
        etsy_data['product_name'] = etsy_req['product_name'].values.tolist()
        etsy_data['product_price'] = etsy_req['product_price'].values.tolist()

        return jsonify(amazon_data, total_rev_data, monthly_rev_data, etsy_data)
    except:
        return redirect(url_for('catch'))
@app.route("/error")
def catch():
    # parse input terms
    return render_template("error.html")

if __name__ == "__main__":
    app.run(debug=True)

