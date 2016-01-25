"""
##### Web scrape BBC Good Food website for recipes by cuisine
##### using both static and dynamic webscraping techniques
##### store recipe details for all cuisines in MongoDB and a pickle file
"""

from time import sleep
import time
from math import ceil
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from pymongo import MongoClient
import pickle


# sleep time between web requests (in seconds)
SCRAPING_REQUEST_STAGGER = 5.0
# main search link for BBC Good Food cuisines
SEARCH_URL = 'http://www.bbcgoodfood.com/search/recipes?query=#page={}&path=cuisine/{}'
# link for BBC Good Food cuisine collection
COLLECTION_URL = 'http://www.bbcgoodfood.com/recipes/collection/{}'
# recipe url
RECIPE_URL = 'http://www.bbcgoodfood.com{}'
# number of recipes per page for search results
NUMBER_OF_RECIPES_PER_SEARCH_PAGE = 15.


# create MongoDB database and collection
DB_NAME = 'PROJECT_RECIPIES'
COLLECTION_NAME = 'BBC_GOOD_FOOD'

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


def get_content_from_static_url(link):
    """
    Make web request to static url and collect webpage content
    :param  link (str): web page link
    :return  html content for web page
    """
    # sleep time before making web request
    sleep(SCRAPING_REQUEST_STAGGER)
    # header details for web request
    headers = {"User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, \
        like Gecko) Chrome/47.0.2526.80 Safari/537.36"}
    response = requests.get(link, headers=headers)
    if response.status_code != 200:
        return False
    return response.content


def get_content_from_dynamic_url(link):
    """
    Make web request to dynamic webpage url and collect webpage content.
    Required content loads in about 10 seconds, as a buffer set the page load timeout \
    to 25 seconds. If the page load timeout exception is raised, return content of page \
    (this will include required content since that loads in about 10 seconds)
    :param  link (str): web page link
    :return  html content for web page
    """
    # make web request using Selenium chrome browser driver
    browser = webdriver.Chrome("/Applications/chromedriver")
    browser.set_page_load_timeout(25)
    try:
        browser.get(link)
    except:
        page_source = browser.page_source
        browser.quit()
        return page_source
    page_source = browser.page_source
    browser.quit()
    return page_source


def get_number_of_search_recipes(cuisine):
    """
    Make web request to cuisine url and get the number of search recipes for cuisine
    :param  cuisine (str): cuisine name to make search request for
    :return  number of recipes for cuisine (int) or None (if no content for url)
    """
    cuisine_search_link = SEARCH_URL.format(0, cuisine)
    cuisine_recipes = get_content_from_dynamic_url(cuisine_search_link)
    if not cuisine_recipes:
        print "no content for:", cuisine_search_link
        return None
    soup_cuisine = BeautifulSoup(cuisine_recipes)
    # get recipe-count and convert it into integer
    return int(soup_cuisine.find("h1", {"class": "search-title"}).find("em").get_text())


def get_cuisine_search_pages(cuisine, page):
    """
    Make web request to cuisine search page and collect recipe links for page
    :params  cuisine (str): cuisine name to make search request for
             page (int): page number of search results to collect content from
    :return  list of recipe links for search page url or None (if no content)
    """
    link = SEARCH_URL.format(page, cuisine)
    cuisine_recipe_links = get_content_from_dynamic_url(link)
    if not cuisine_recipe_links:
        print "no content for:", link
        return None
    soup_search = BeautifulSoup(cuisine_recipe_links)
    return soup_search.find_all("h2", {"class": "node-title"})


def get_cuisine_collection_page(cuisine):
    """
    Make web request to cuisine collection page and collect recipe links for first page
    :param  cuisine (str): cuisine name to make search request for
    :return  list of recipe links for colelction first page url or None (if no content)
    """
    cuisine_link = COLLECTION_URL.format(cuisine)
    cuisine_recipes = get_content_from_static_url(cuisine_link)
    if not cuisine_recipes:
        print "no content for:", cuisine_link
        return None
    soup_cuisine = BeautifulSoup(cuisine_recipes)
    return soup_cuisine.find_all("h2", {"class": "node-title"})


def get_recipe(r_link):
    """
    Make web request to recipe page and get the recipe content
    :param  r_link (str): recipe link
    :return  html content for the web page in beautifulsoup format
                    or None (if no content)
    """
    recipe_link = RECIPE_URL.format(r_link)
    recipe_response = get_content_from_static_url(recipe_link)
    if not recipe_response:
        print "no content for: ", recipe_link
        return None
    return BeautifulSoup(recipe_response)


def get_recipe_title(soup_recipe):
    """
    Get recipe title from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe title
    """
    return soup_recipe.find("h1", {"itemprop": "name"}).get_text()


def get_recipe_chef(soup_recipe):
    """
    Get recipe chef name from recipe content.
    If chef name is not given for the recipe, get submitter name as the chef name
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe chef name or None for no content
    """
    chef_name = soup_recipe.find("div",
        {"class": "recipe-header__chef recipe-header__chef--first"}).find("a")
    if not chef_name:
        chef_name = soup_recipe.find("div",
            {"class": "recipe-header__chef recipe-header__chef--first"}).find("span")
    if not chef_name:
        return None
    return chef_name.get_text()


def get_description(soup_recipe):
    """
    Get recipe description from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe description / summary
    """
    description = soup_recipe.find("div", {"itemprop": "description"}).find("div",
        {"class": "field-items"}).find("div")
    if not description:
        return None
    return description.get_text()


def get_recipe_ingredients(soup_recipe):
    """
    Get recipe ingredients from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe ingredient list
    """
    ingredients_list = soup_recipe.find_all("li", {"itemprop": "ingredients"})
    ingredients = []
    for ing in ingredients_list:
        ingredients.append(ing.get_text().split('\n')[0])
    return ingredients


def get_recipe_preperation(soup_recipe):
    """
    Get recipe preperation steps from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe preperation steps as a list
    """
    prep_steps = soup_recipe.find_all("li", {"itemprop": "recipeInstructions"})
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
    prep_time_check = soup_recipe.find("span", {"class": "recipe-details__cooking-time-prep"})
    prep_time, cooking_time = None, None
    if prep_time_check:
        prep_time = prep_time_check.get_text().split(":")[1].strip()
    cooking_time_check = soup_recipe.find("span", {"class": "recipe-details__cooking-time-cook"})
    if cooking_time_check:
        cooking_time = cooking_time_check.get_text().split(":")[1].strip()
    return prep_time, cooking_time


def get_servings(soup_recipe):
    """
    Get recipe servings/yield from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe servings/yield or None if content not available
    """
    servings = soup_recipe.find("span", {"itemprop": "recipeYield"})
    if not servings:
        return None
    return servings.get_text().strip()


def get_skill_level(soup_recipe):
    """
    Get recipe skill level from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe skill level or None if content not available
    """
    skill_level = soup_recipe.find("section",
        {"class": "recipe-details__item recipe-details__item--skill-level"}).find("span",
        {"class": "recipe-details__text"})
    if not skill_level:
        return None
    return skill_level.get_text().strip()


def get_recommendations(soup_recipe):
    """
    Get recipe recommendation score and number of recommendations from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe recommendation score and number of recommendations \
                or None if content not available
    """
    ratings = soup_recipe.find("meta", {"itemprop": "ratingValue"})["content"]
    ratings_count = soup_recipe.find("meta", {"itemprop": "ratingCount"})["content"]
    if ratings == 0:
        return None, None
    return ratings, ratings_count


def get_nutrition_per_serving(soup_recipe):
    """
    Get nutritional values per serving for recipe from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  dictionary of (nutrition name, value) as (key, value) pairs \
                or None if content not available
    """
    nutritional_info = soup_recipe.find_all("span", {"class": "nutrition__value"})
    if not nutritional_info:
        return None
    nutrition_name, nutrition_value = [], []
    for nutrition in nutritional_info:
        if nutrition.get_text() != '-':
            nutrition_name.append(nutrition["itemprop"])
            nutrition_value.append(nutrition.get_text())
    return dict(zip(nutrition_name, nutrition_value))


def get_image_source(soup_recipe):
    """
    Get recipe image source from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe image source or None if content not available
    """
    image_source = soup_recipe.find("img", {"itemprop": "image"})
    if not image_source:
        return None
    return image_source["src"]


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
        recipe_link = r.a["href"]
        print "recipe link: ", recipe_link
        soup_recipe = get_recipe(recipe_link)
        if soup_recipe:
            recipe['r_link'] = recipe_link
            recipe['recipe title'] = get_recipe_title(soup_recipe)
            recipe['chef'] = get_recipe_chef(soup_recipe)
            recipe['description'] = get_description(soup_recipe)
            recipe['ingredient list'] = get_recipe_ingredients(soup_recipe)
            recipe['preperation steps'] = get_recipe_preperation(soup_recipe)
            recipe['prep_time'], recipe['cook_time'] = get_recipe_time(soup_recipe)
            recipe['servings'] = get_servings(soup_recipe)
            recipe['skill_level'] = get_skill_level(soup_recipe)
            recipe['rating'], recipe['rating count'] = get_recommendations(soup_recipe)
            recipe['nutritional_info'] = get_nutrition_per_serving(soup_recipe)
            recipe['image_source'] = get_image_source(soup_recipe)
            cuisine_recipes[recipe['recipe title']] = recipe
    return cuisine_recipes


def get_recipe_links(cuisine, pages, collection):
    """
    Get recipe details from cuisine search pages \
    and cuisine colections first page (if cuisine has a collection)
    :params  cuisine (str): cuisine name
             pages (int): number of search result pages for cuisine
             collection (boolean): True if cuisine has collection, else False
    :return  recipe details in dictionary format
    """
    recipe_links = []
    for page in xrange(0, pages):
        sleep(SCRAPING_REQUEST_STAGGER)
        recipe_links.extend(get_cuisine_search_pages(cuisine, page))
    if collection:
        recipe_links.extend(get_cuisine_collection_page(cuisine))
    cuisine_recipes = get_recipe_details(list(set(recipe_links)))
    return cuisine_recipes


def get_cuisine_recipes(search_cuisisnes, cuisines):
    """
    Get recipe details for cuisines, store in mongoDB,
    and convert details dictionary into pandas dataframe
    convert number of recipes into pages to scrape, which will be number search pages \
    and one page for cuisine collection (if there is collection)
    :params  search_cuisines (list): cuisines under BBC Good Food search
             cuisines (list): cuisines under BBC Good Food collections
    :return  recipe details in pandas dataframe
    """
    cuisine_df = pd.DataFrame()
    for cuisine in search_cuisisnes:
        cuisine_dict = {}
        cuisine_dict['cuisine'] = cuisine
        cuisine_dict['source'] = 'BBC Good Food'
        cuisine_no_space = cuisine.lower().replace(' & ', '-').replace(' ', '-')
        recipes_cuisine_search = get_number_of_search_recipes(cuisine_no_space)
        cuisine_dict['pages'] = int(ceil(recipes_cuisine_search /
            NUMBER_OF_RECIPES_PER_SEARCH_PAGE))
        collection = False
        if cuisine in cuisines:
            cuisine_dict['pages'] += 1
            collection = True
        cuisine_dict['recipes_details'] = get_recipe_links(cuisine_no_space,
            cuisine_dict['pages']-1, collection)
        cuisine_dict['num_recipes'] = len(cuisine_dict['recipes_links'])
        print '#####'
        print "Cuisine: %s \t Number of recipes: %d \t\t Number of pages: %d" \
            % (cuisine, cuisine_dict['num_recipes'], cuisine_dict['pages'])
        coll.insert_one(cuisine_dict)
    cuisine_df = cuisine_df.append(pd.DataFrame.from_dict(cuisine_dict, orient='columns'),
            ignore_index=True)
    return cuisine_df


if __name__ == '__main__':

    # list of cuisines under BBC Good Food collections
    cuisines = ['American', 'British', 'Caribbean', 'Chinese', 'French', 'Greek', 'Indian',
    'Italian', 'Japanese', 'Mediterranean', 'Mexican', 'Moroccan', 'Spanish', 'Thai',
    'Turkish', 'Vietnamese']
    # list of cuisines under BBC Good Food search
    search_cuisisnes = ['African', 'American', 'Asian', 'Australian', 'Austrian', 'Balinese',
    'Belgian', 'Brazilian', 'British', 'Cajun & Creole', 'Caribbean', 'Chilean', 'Chinese',
    'Cuban', 'Danish', 'Eastern European', 'English', 'French', 'German', 'Greek',
    'Hungarian', 'Indian', 'Irish', 'Italian', 'Japanese', 'Jewish', 'Korean',
    'Latin American', 'Mediterranean', 'Mexican', 'Middle Eastern', 'Moroccan',
    'North African', 'Portuguese', 'Scandinavian', 'Scottish', 'Southern & Soul',
    'Spanish', 'Swedish', 'Swiss', 'Thai', 'Tunisian', 'Turkish', 'Vietnamese']
    cuisine_dataframe = get_cuisine_recipes(search_cuisisnes, cuisines)
    save_obj(cuisine_dataframe, "recipes_data_bbc_good_food")
