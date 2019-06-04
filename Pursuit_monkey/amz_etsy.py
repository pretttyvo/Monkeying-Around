# import libraries
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import pymongo
from splinter import Browser
from selenium import webdriver
import urllib.request
from selenium.webdriver.chrome.options import Options
import urllib.request
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
import time
import locale
# from config import email, password
# Import SQL Alchemy
from sqlalchemy import create_engine

# Import and establish Base for which classes will be constructed 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base

# Import modules to declare columns and column data types
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import Session

# Create class for scraping
class scrape():
    def __init__(self, search):
        print("scraping")
    def all_test(self, search):
        # Create an engine for the chinook.sqlite database
        engine = create_engine("sqlite:///static/db/top_trends.db", echo=False)
        # Declare a Base using `automap_base()`
        Base = automap_base()
        # Use the Base class to reflect the database tables
        Base.prepare(engine, reflect=True)
        # Base.metadata.create_all(engine)
        # create conn
        conn = engine.connect()
        # To push the objects made and query the server we use a Session object
        session = Session(bind=engine)
        search_df = pd.read_sql("SELECT * FROM search", conn)
        searched_terms = search_df.search_term.unique()
        new_terms = search
        old_terms = []
        # check to see if data is already in database
        list_len = int(len(search))
        search_len = int(len(searched_terms))
        print(len(search)-1)
        print(len(searched_terms)-1)
        # check to see if data is already in database
        for i in range(0, list_len):
            for j in range(0, search_len):
                if search[i] == searched_terms[j]:
                    old_terms.append(searched_terms[j])
                    x = search[i]
                else:
                    pass
        for n in old_terms:
            new_terms.remove(n)
        if len(new_terms) > 0:
            amz = amazon_h10(old_terms)
            list_df = amz.mix(new_terms, old_terms)
            print(list_df)
            return list_df
        else:
            print(old_terms)
            amz = amazon_h10(old_terms)
            list_df = amz.old(old_terms)
            return list_df


class amazon_h10():
    def __init__(self, search):
        print(f'You searched for {search}')

    def complete_scrape(self, search):
        print('you are scraping amazon')
        amazon_url = "https://www.amazon.com"
        # open the driver
        options = Options()
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(30)
        # scrape amazon      
        search_df = pd.DataFrame()
        search_df1 = pd.DataFrame()
        amazon_df = pd.DataFrame()  
        for word in search:
            search_df1['search_term'] = [word]
            search_df = search_df.append(search_df1)
            try:
                search_url = f'https://www.amazon.com/s?k={word}&ref=nb_sb_noss_1'
                driver.get(search_url)
                html = driver.page_source
                search_beautify = BeautifulSoup(html, 'html.parser')
                data = search_beautify.findAll('div', class_="a-section a-spacing-none")
                try:
                    link = [link.a['href'] for link in data]
                except:
                    pass

                data2 = search_beautify.findAll('span', class_="a-offscreen")
                time.sleep(3)
                try:
                    amz_prod_price = [x.text.split('$')[1] for x in data2]
                except:
                    pass
                amz_prod_price = amz_prod_price[:10]
                amz_prod_name = []

                for i in range(12,22):
                    product_link = amazon_url + link[i]
                    break_link = product_link.split('/')
                    title = break_link[3].replace('-', ' ')
                    amz_prod_name.append(title)
                amazon_df1 = pd.DataFrame()  
                amazon_df1['product_name'] = amz_prod_name
                amazon_df1['product_price'] = amz_prod_price
                amazon_df1['search_term'] = [f'{word}' for count in amz_prod_name]
                amazon_df = amazon_df.append(amazon_df1)
            except:
                pass
#     ==================================
        print('you are scraping helium')
        # sign into Helium 10
        driver.get('https://members.helium10.com/user/signin')
        login = driver.find_element_by_id('loginform-email')
        login.send_keys(email)
        password_route = driver.find_element_by_id('loginform-password')
        password_route.send_keys(password)
        login_button = driver.find_elements_by_xpath("//button[contains(text(), 'Log In')]")
        login_button[0].click()
        time.sleep(3)
        
        # create global data frame
        overview_data_df = pd.DataFrame()
        top5_monthly_revenue_df = pd.DataFrame()
        overview_data_df1 = pd.DataFrame()
        top5_monthly_revenue_df1 = pd.DataFrame()
        
        # type in the key words search
        for words in search:
            #  link for niche
            h_10_niche = "https://members.helium10.com/black-box/niche"
            # visit link
            driver.get(h_10_niche)
            search_bar = driver.find_element_by_id('filter-asin')
            search_bar.clear()
            search_bar.send_keys(words)
            
            try:
                # click on search button
                time.sleep(1)
                search_button = driver.find_elements_by_xpath("//button[contains(text(), 'Search')]")
                search_button[0].click()
            except:
                time.sleep(2)
                search_button = driver.find_elements_by_xpath("//button[contains(text(), 'Search')]")
                search_button[0].click()

            # Scrape overview data    
            try: 
                overview_data = driver.find_elements_by_xpath("//div[@class='col-xs-12 col-sm-6 col-md-2']")

                col1 = []
                col2 = []
                time.sleep(1)
                for i in range(0,5):
                    h_10_data = overview_data[i].text
                    h_data = h_10_data.split('\n')
                    col1.append(h_data[0].strip())
                    value = h_data[1].split('$')
                    if len(value) > 1:
                        value = value[1]
                        col2.append(value)
                    else:
                        col2.append(value[0])
                # pull data from 20-24
                overview_data_df1['revenue_specs'] = col1
                overview_data_df1['revenue_value'] = col2
                overview_data_df1['search_term'] = [f'{words}' for x in col1]
                overview_data_df = overview_data_df.append(overview_data_df1)

                # Pull revenue data  
                sort_product_list = Select(driver.find_element_by_id('sort'))
                driver.find_element_by_xpath("//select[@name='sort']/option[text()='Monthly Revenue High To Low']").click()

                # pull in data
                # product title
                time.sleep(1)
                product_name = driver.find_elements_by_class_name('media-heading')
                product_names = [name.text for name in product_name]

                # price
                product_price = driver.find_elements_by_class_name('price-chart')
                product_prices = [price.text.split('$')[1] for price in product_price]

                # monthly sales
                product_sales_monthly = driver.find_elements_by_class_name('monthlySales-column')
                product_sales_monthly_s = [sales.text for sales in product_sales_monthly]

                # monthly revenue 
                product_revenue_monthly = driver.find_elements_by_class_name('monthlyRevenue-column')
                product_revenue_monthly_s = [rev.text.split('$')[1] for rev in product_revenue_monthly]

                # put into a df
                top5_monthly_revenue_df1['monthly_product'] = product_names[:5]
                top5_monthly_revenue_df1['monthly_price'] = product_prices[:5]
                top5_monthly_revenue_df1['monthly_sales'] = product_sales_monthly_s[:5]
                top5_monthly_revenue_df1['monthly_revenue'] = product_revenue_monthly_s[:5]
                top5_monthly_revenue_df1['search_term'] = [f'{words}' for x in product_names[:5]]
                top5_monthly_revenue_df = top5_monthly_revenue_df.append(top5_monthly_revenue_df1)
            except:
                pass

#     ====================
        etsy_df = pd.DataFrame()
        etsy_df1 = pd.DataFrame()
        print("you are scraping etsy")
        # loop over search words        
        for word in search:
            # visit url
            search_url = f'https://www.etsy.com/search?q={word}&explicit=1&order=most_relevant'
            driver.get(search_url)
            
            # product name
            try:
                product = driver.find_elements_by_class_name("v2-listing-card__info")
                product_name = [link.text.strip() for link in product]

                # produce price
                price = driver.find_elements_by_class_name("n-listing-card__price")
                product_price = [x.text.strip() for x in price]
                # clean data 
                n = [x.split('\n') for x in product_price]
                product_price = [y[0] for y in n]
                b = [x.split('$') for x in product_price]
                locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 
                try:
                    product_price = [locale.atof(y[1]) for y in b]
                except:
                    product_price = [y[1] for y in b]

                # df to hold the data    
                etsy_df1['product_name'] = product_name[:5]
                etsy_df1['product_price'] = product_price[:5]
                etsy_df1['search_term'] = [f'{word}' for x in product_name[:5]]
                etsy_df = etsy_df.append(etsy_df1)
            except:
                pass
        driver.close()
        print("scraping complete")
        search_df = search_df.set_index(['search_term'])
        amazon_df = amazon_df.set_index(['search_term'])
        overview_data_df = overview_data_df.set_index(['search_term'])
        top5_monthly_revenue_df = top5_monthly_revenue_df.set_index(['search_term'])
        etsy_df = etsy_df.set_index(['search_term'])
        return [search_df, amazon_df, overview_data_df, top5_monthly_revenue_df, etsy_df]

    def mix(self, new_terms, old_terms):
        # Create an engine for the chinook.sqlite database
        engine = create_engine("sqlite:///static/db/top_trends.db", echo=False)
        # Declare a Base using `automap_base()`
        Base = automap_base()
        # Use the Base class to reflect the database tables
        Base.prepare(engine, reflect=True)
        # Base.metadata.create_all(engine)
        # create conn
        conn = engine.connect()
        # To push the objects made and query the server we use a Session object
        session = Session(bind=engine)
        search_df = pd.read_sql("SELECT * FROM search", conn)
        amazon_df = pd.read_sql("SELECT * FROM amazon", conn)
        total_df = pd.read_sql("SELECT * FROM total_revenue_h10", conn)
        monthly_df = pd.read_sql("SELECT * FROM monthly_revenue_h10", conn)
        etsy_df = pd.read_sql("SELECT * FROM etsy", conn)

        search_df = search_df.set_index(['search_term'])
        amazon_df = amazon_df.set_index(['search_term'])
        total_df = total_df.set_index(['search_term'])
        monthly_df = monthly_df.set_index(['search_term'])
        etsy_df = etsy_df.set_index(['search_term'])
        # scrape for new material
        list_df = self.complete_scrape(new_terms)
        # separate returned df
        search_df_scrape = list_df[0]
        amazon_df_scrape = list_df[1]
        revenue_df_scrape = list_df[2]
        product_data_df_scrape = list_df[3]
        etsy_df_scrape = list_df[4]
#         search_df_scrape = search_df_scrape.set_index(['search_term'])
#         amazon_df_scrape = amazon_df_scrape.set_index(['search_term'])
#         revenue_df_scrape = revenue_df_scrape.set_index(['search_term'])
#         product_data_df_scrape = product_data_df_scrape.set_index(['search_term'])
#         etsy_df_scrape = etsy_df_scrape.set_index(['search_term'])
        # put into db
        try:
            search_df_scrape.to_sql('search', engine, if_exists='append')
            amazon_df_scrape.to_sql('amazon', engine, if_exists='append')
            revenue_df_scrape.to_sql('total_revenue_h10', engine, if_exists='append')
            product_data_df_scrape.to_sql('monthly_revenue_h10', engine, if_exists='append')
            etsy_df_scrape.to_sql('etsy', engine, if_exists='append')
        except:
            pass
            print('there was an error when trying to save')
        # pull in old material
        for word in old_terms:
            search_df_scrape = search_df_scrape.append(search_df.loc[word]).reset_index()
            amazon_df_scrape = amazon_df_scrape.append(amazon_df.loc[word]).reset_index()
            revenue_df_scrape = revenue_df_scrape.append(total_df.loc[word]).reset_index()
            product_data_df_scrape = product_data_df_scrape.append(monthly_df.loc[word]).reset_index()
            etsy_df_scrape = etsy_df_scrape.append(etsy_df.loc[word]).reset_index()
        # parse data into lists
#         search_data = {}
#         amazon_data = {}
#         total_rev_data = {}
#         monthly_rev_data = {}
#         etsy_data = {}
#         terms = old_terms + new_terms
#         for phrase in terms:
#             # search
#             search_data['search_term'] = search_df_scrape['search_term'].values.tolist()
#             # amazon
#             amazon_data['search_term'] = amazon_df_scrape['search_term'].values.tolist()
#             amazon_data['product_name'] = amazon_df_scrape['product_name'].values.tolist()
#             amazon_data['product_price'] = amazon_df_scrape['product_price'].values.tolist()
#             # helium total revenue
#             total_rev_data['search_term'] = revenue_df_scrape['search_term'].values.tolist()
#             total_rev_data['revenue_specs'] = revenue_df_scrape['revenue_specs'].values.tolist()
#             total_rev_data['revenue_value'] = revenue_df_scrape['revenue_value'].values.tolist()
#             # helium monthly revenure by product
#             monthly_rev_data['search_term'] = product_data_df_scrape['search_term'].values.tolist()
#             monthly_rev_data['monthly_product'] = product_data_df_scrape['monthly_product'].values.tolist()
#             monthly_rev_data['monthly_price'] = product_data_df_scrape['monthly_price'].values.tolist()
#             monthly_rev_data['monthly_sales'] = product_data_df_scrape['monthly_sales'].values.tolist()
#             monthly_rev_data['monthly_revenue'] = product_data_df_scrape['monthly_revenue'].values.tolist()
#             # etsy
#             etsy_data['search_term'] = etsy_df_scrape['search_term'].values.tolist()
#             etsy_data['product_name'] = etsy_df_scrape['product_name'].values.tolist()
#             etsy_data['product_price'] = etsy_df_scrape['product_price'].values.tolist()
        return [amazon_df_scrape, revenue_df_scrape, product_data_df_scrape, etsy_df_scrape]
    def old(self, old_terms):
        # Create an engine for the chinook.sqlite database
        engine = create_engine("sqlite:///static/db/top_trends.db", echo=False)
        # Declare a Base using `automap_base()`
        Base = automap_base()
        # Use the Base class to reflect the database tables
        Base.prepare(engine, reflect=True)
        # Base.metadata.create_all(engine)
        # create conn
        conn = engine.connect()
        # To push the objects made and query the server we use a Session object
        session = Session(bind=engine)
        search_df = pd.read_sql("SELECT * FROM search", conn)
        amazon_df = pd.read_sql("SELECT * FROM amazon", conn)
        total_df = pd.read_sql("SELECT * FROM total_revenue_h10", conn)
        monthly_df = pd.read_sql("SELECT * FROM monthly_revenue_h10", conn)
        etsy_df = pd.read_sql("SELECT * FROM etsy", conn)
        search_df = search_df.set_index(['search_term'])
        amazon_df = amazon_df.set_index(['search_term'])
        total_df = total_df.set_index(['search_term'])
        monthly_df = monthly_df.set_index(['search_term'])
        etsy_df = etsy_df.set_index(['search_term'])
        
#         .set_index(['search_term'])
        search_req = pd.DataFrame()
        amazon_req = pd.DataFrame()
        revenue_req = pd.DataFrame()
        product_data_req = pd.DataFrame()
        etsy_req = pd.DataFrame()
        for word in old_terms:
            search_req = search_req.append(search_df.loc[word])
            amazon_req = amazon_req.append(amazon_df.loc[word])
            revenue_req = revenue_req.append(total_df.loc[word])
            product_data_req = product_data_req.append(monthly_df.loc[word])
            etsy_req = etsy_req.append(etsy_df.loc[word])
#         search_data = {}
#         amazon_data = {}
#         total_rev_data = {}
#         monthly_rev_data = {}
#         etsy_data = {}
#         for phrase in old_terms:
#             # search
# #             search_data['search_term'] = search_req['search_term'].values.tolist()
#             # amazon
#             amazon_data['search_term'] = amazon_req['search_term'].values.tolist()
#             amazon_data['product_name'] = amazon_req['product_name'].values.tolist()
#             amazon_data['product_price'] = amazon_req['product_price'].values.tolist()
#             # helium total revenue
#             total_rev_data['search_term'] = revenue_req['search_term'].values.tolist()
#             total_rev_data['revenue_specs'] = revenue_req['revenue_specs'].values.tolist()
#             total_rev_data['revenue_value'] = revenue_req['revenue_value'].values.tolist()
#             # helium monthly revenure by product
#             monthly_rev_data['search_term'] = product_data_req['search_term'].values.tolist()
#             monthly_rev_data['monthly_product'] = product_data_req['monthly_product'].values.tolist()
#             monthly_rev_data['monthly_price'] = product_data_req['monthly_price'].values.tolist()
#             monthly_rev_data['monthly_sales'] = product_data_req['monthly_sales'].values.tolist()
#             monthly_rev_data['monthly_revenue'] = product_data_req['monthly_revenue'].values.tolist()
#             # etsy
#             etsy_data['search_term'] = etsy_req['search_term'].values.tolist()
#             etsy_data['product_name'] = etsy_req['product_name'].values.tolist()
#             etsy_data['product_price'] = etsy_req['product_price'].values.tolist()
        return [amazon_req, revenue_req, product_data_req, etsy_req]