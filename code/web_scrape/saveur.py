"""
##### Web scrape Saveur website for recipes by cuisine
##### using both static and dynamic webscraping techniques
##### store recipe details for all cuisines in MongoDB and a pickle file
"""

from time import sleep
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from math import ceil
import pandas as pd
from pymongo import MongoClient
import pickle


# sleep time between web requests (in seconds)
SCRAPING_REQUEST_STAGGER = 5.0
# main url for Saveur cuisine recipes
CUISINE_URL = 'http://www.saveur.com/recipes-search?filter[2]={}'
# recipe url for Saveur recipes
RECIPE_URL = 'http://www.saveur.com{}'
# number of recipes per page for search results
NUMBER_OF_RECIPES_PER_PAGE = 48.


# create MongoDB database and collection
DB_NAME = 'PROJECT_RECIPIES'
COLLECTION_NAME = 'Saveur'

# connect to mongodb to store scraped data
client = MongoClient()
db = client[DB_NAME]
coll = db[COLLECTION_NAME]


def save_obj(obj, name):
    """
    Dump object in pickel file in data folder
    :params  obj (object): object to be saved (can be in any form)
             name (str): file-name to save object with
    """
    with open('../../data/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    """
    Load object from pickel file in data folder
    :param  name (str): file-name to load object from
    :return  object in original format
    """
    with open('../../data/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def get_content_from_url(link):
    """
    Make web request and collect webpage content
    :param  link (str): web page link
    :return  html content for web page
    """
    # sleep time before making web request
    sleep(SCRAPING_REQUEST_STAGGER)
    response = requests.get(link)
    if response.status_code != 200:
        return False
    return response.content


def get_content_from_dynamic_url(link):
    """
    Make web request to dynamic webpage url and collect webpage content
    Required content loads in about 30-40 seconds as a buffer set the page \
    load timeout to 60 seconds. If the page load timeout exception is \
    raised, return content of page (this will include required content \
    since that loads in about 30-40 seconds)
    :param  link (str): web page link
    :return  html content for web page 
    """
    # make web request using Selenium chrome browser driver
    browser = webdriver.Chrome("/Applications/chromedriver")  
    browser.set_page_load_timeout(60)
    try:
        browser.get(link)
    except:
        page_source = browser.page_source
        browser.quit()
        return page_source
    page_source = browser.page_source
    browser.quit()
    return page_source


def get_number_of_recipes(filter2_value):
    """
    Make web request to cuisine url and get the number of search recipes for cuisine
    :param  cuisine (str): cuisine name to make search request for
    :return  number of recipes for cuisine (int) or None (if no content for url)
    """
    cuisine_link = CUISINE_URL.format(filter2_value)
    cuisine_recipes = get_content_from_dynamic_url(cuisine_link)
    if not cuisine_recipes:
        print "no content for:", cuisine_link
        return None
    soup_cuisine = BeautifulSoup(cuisine_recipes)
    # select required characters from phrase and convert it into integer
    return int(soup_cuisine.find("div", {"class": "results_label"}).get_text().split()[0].replace(",", ""))


def get_recipe(r_link):
    """
    Make web request to recipe page and get the recipe content
    :param  r_link (str): recipe link
    :return  html content for the web page in beautifulsoup format
                    or None (if no content)
    """
    recipe_link = RECIPE_URL.format(r_link)
    recipe_response = get_content_from_url(recipe_link)
    if not recipe_response:
        print "no content for:", recipe_link
        return None
    return BeautifulSoup(recipe_response)


def get_recipe_title(soup_recipe):
    """
    Get recipe title from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe title
    """
    return soup_recipe.find("div", {"class": "content-onecol one-col"}).find("h1").get_text().strip()


def get_recipe_chef(soup_recipe):
    """
    Get recipe chef name from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe chef name or None for no content
    """
    chef_name = soup_recipe.find("span", {"class": "author"})
    if not chef_name:
        return None
    return chef_name.find("a").get_text()


def get_description(soup_recipe):
    """
    Get recipe description from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe description / summary
    """
    summary = soup_recipe.find("div", {"property": "description"})
    if not summary:
        return None
    return summary.get_text().strip()


def get_recipe_ingredients(soup_recipe):
    """
    Get recipe ingredients from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe ingredient list
    """
    ingredients_list = soup_recipe.find_all("div", {"class": "ingredient"})
    ingredients = []
    for ing in ingredients_list:
        ingredients.append(ing.get_text().strip())
    return ingredients


def get_recipe_preperation(soup_recipe):
    """
    Get recipe preperation steps from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe preperation steps as a list
    """
    prep_steps = soup_recipe.find_all("div", {"class": "instruction"})
    prep = []
    for step in prep_steps:
        prep.append(step.get_text().strip())
    return prep


def get_recipe_time(soup_recipe):
    """
    Get recipe prep and cooking times from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe preperation time and recipe cooking time 
                or None if content not available
    """
    prep_time = soup_recipe.find("div", {"class": "prep-time"})
    if prep_time:
        prep_time = prep_time.get_text().strip()
    else:
        prep_time = None
    cooking_time = soup_recipe.find("div", {"class": "cook-time"})
    if cooking_time:
        cooking_time = cooking_time.get_text().strip()
    else:
        cooking_time = None
    return prep_time, cooking_time


def get_servings(soup_recipe):
    """
    Get recipe servings/yield from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe servings/yield or None if content not available
    """
    servings = soup_recipe.find("div", {"class": "yield"})
    if not servings:
        return None
    return servings.get_text().strip()


def get_recommendations(soup_recipe):
    """
    Get recipe ratings score and number of recommendations from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe ratings score and number of recommendations
                or None if content not available
    """
    ratings = soup_recipe.find("span", {"class": "rating"})
    if not ratings:
        ratings = None
    else:
        ratings = ratings.get_text()
    recommendations = soup_recipe.find("div", {"class": "prepare-again-rating"})
    if not recommendations:
        recommendations = None
    else:
        recommendations = recommendations.find("span").get_text()
    return ratings, recommendations


def get_nutrition_per_serving(soup_recipe):
    """
    Get nutritional values per serving for recipe from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  nutrition information in string format or None if content not available
    """
    nutritional_info = soup_recipe.find("div", {"class": "nutritional-info"})
    if not nutritional_info:
        return None
    return nutritional_info.get_text()


def get_image_source(soup_recipe):
    """
    Get recipe image source from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe image source or None if content not available
    """
    image_source = soup_recipe.find("div", {"class": "field-image-inner"})
    if not image_source:
        return None
    return image_source.find("img")["src"]


def get_recipe_details(recipe_links):
    """
    Get necessary recipe details from all recipe links and store in dictionary
    with (key, value) pairs as (recipe title, corresponding details dictionary)
    :param  recipe_links (list): recipe links for each cuisine
    :return  recipe details in dictionary format
    """
    cuisine_recipes = {}

    for r in recipe_links:
        recipe = {}
        recipe['r_link'] = r.a["href"]
        print "recipe link: ", recipe['r_link']
        soup_recipe = get_recipe(recipe['r_link'])
        if soup_recipe:
            recipe['recipe title'] = get_recipe_title(soup_recipe)
            recipe['chef'] = get_recipe_chef(soup_recipe)
            recipe['description'] = get_description(soup_recipe)
            recipe['ingredient list'] = get_recipe_ingredients(soup_recipe)
            recipe['preperation steps'] = get_recipe_preperation(soup_recipe)
            recipe['prep_time'], recipe['cook_time'] = get_recipe_time(soup_recipe)
            recipe['servings'] = get_servings(soup_recipe)
            recipe['rating'], recipe['recommendation'] = get_recommendations(soup_recipe)
            recipe['nutritional_info'] = get_nutrition_per_serving(soup_recipe)
            recipe['image_source'] = get_image_source(soup_recipe)
        cuisine_recipes[recipe['recipe title']] = recipe
    return cuisine_recipes


def get_recipe_links(filter2_value, pages):
    """
    Make web request to cuisine search webpage url and collect webpage content \
    by clicking on the next page button for each search page
    Required content loads in about 30-40 seconds as a buffer set the page \
    load timeout to 60 seconds. If the page load timeout exception is raised, \
    continue from that page with increased sleep time per page request
    :params  filter2_value (int): filter value for cuisine (unique for each cuisine)
             pages (int): number of search result pages for cuisine
    :return  recipe details for cuisine in dictionary format
    """
    recipe_links = []
    # make web request using Selenium chrome browser driver
    browser = webdriver.Chrome("/Applications/chromedriver")  
    browser.set_page_load_timeout(60)
    link = CUISINE_URL.format(filter2_value)
    try:
        browser.get(link)
        for page in xrange(1, pages+1):
            recipes_links_per_page = BeautifulSoup(browser.page_source).find_all("div",
                {"class": "result_title"})
            recipe_links.extend(recipes_links_per_page)
            # sleep time before clicking on the next page button
            sleep(SCRAPING_REQUEST_STAGGER)
            # if not last search page, using browser console click next page button
            if page < pages:
                query = ("document.querySelector('li.pager-next').click();")
                browser.execute_script(query)
            sleep(SCRAPING_REQUEST_STAGGER)
    except:
        for page_continue in xrange(page, pages+1):
            sleep(SCRAPING_REQUEST_STAGGER + 20)
            recipes_links_per_page = BeautifulSoup(browser.page_source).find_all("div",
                {"class": "result_title"})
            recipe_links.extend(recipes_links_per_page)
            sleep(SCRAPING_REQUEST_STAGGER)
            if page_continue < pages:
                query = ("document.querySelector('li.pager-next').click();")
                browser.execute_script(query)
            sleep(SCRAPING_REQUEST_STAGGER)
    browser.quit()
    cuisine_recipes = get_recipe_details(recipe_links)
    return cuisine_recipes


def get_cuisine_recipes(cuisines, filter2_values):
    """
    Get recipe details for cuisines, store in mongoDB,
    and convert details dictionary into pandas dataframe
    :params  cuisines (list): cuisines under Epicurious search
             filter2_values (list): corresponding filter2 values for the cuisines
    :return  recipe details in pandas dataframe
    """
    cuisine_df = pd.DataFrame()
    for cuisine, filter2_value in zip(cuisines, filter2_values):
        cuisine_dict = {}
        cuisine_dict['cuisine'] = cuisine
        cuisine_dict['source'] = 'Saveur'
        cuisine_dict['num_recipes'] = get_number_of_recipes(filter2_value)
        cuisine_dict['pages'] = int(ceil(cuisine_dict['num_recipes'] /
            NUMBER_OF_RECIPES_PER_PAGE))
        print '#####'
        print "Cuisine: %s \t Number of recipes: %r \t\t Number of pages: %r" %
            (cuisine, cuisine_dict['num_recipes'], cuisine_dict['pages'])
        cuisine_dict['recipes_details'] = get_recipe_links(filter2_value,
            cuisine_dict['pages'])
        coll.insert_one(cuisine_dict)
        cuisine_df = cuisine_df.append(pd.DataFrame.from_dict(cuisine_dict,
            orient='columns'), ignore_index=True)
    return cuisine_df


if __name__ == '__main__':

    # dictionary of cuisines on Saveur with their respective filter[2] values
    cuisines_dict = {'African':1000489, 'American':1000490, 'Asian':1000491,
    'Cajun/Creole':1000493, 'Caribbean':1000494, 'Chinese':1000496,'Cuban':1000497,
    'Eastern European/Russian':1000498, 'English/Scottish':1000499, 'French':1000500,
    'German':1000501, 'Greek':1000503, 'Indian':1000506, 'Indonesian':1000932,
    'Italian':1000508, 'Japanese':1000509, 'Jewish':1000510, 'Mediterranean':1000512,
    'Mexican':1000513, 'Middle Eastern':1000514, 'Moroccan':1000515,
    'Scandinavian':1000517, 'Southwestern/Soul Food':1000518, 'Tex-Mex':1000521,
    'Spanish/Portuguese':1000520, 'Thai':1000522, 'Vietnamese':1000525}
    cuisines = cuisines_dict.keys()
    filter2_values = cuisines_dict.values()
    cuisine_links_dataframe = get_cuisine_recipes(cuisines, filter2_values)
    save_obj(cuisine_dataframe, "recipes_data_saveur")
