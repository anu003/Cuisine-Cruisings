from time import sleep
import requests
from bs4 import BeautifulSoup
import re
from math import ceil
import pandas as pd
from pymongo import MongoClient


SCRAPING_REQUEST_STAGGER = 2.0 # in seconds
# the main link for BBC food
URL = 'http://www.bbc.co.uk/food/cuisines/'
CUISINE_URL = 'http://www.bbc.co.uk/food/recipes/search?page={}&cuisines%5B0%5D={}&sortBy=lastModified'
RECIPE_URL = 'http://www.bbc.co.uk{}'


DB_NAME = 'PROJECT_RECIPIES'
COLLECTION_NAME = 'BBC'

client = MongoClient()
db = client[DB_NAME]
coll = db[COLLECTION_NAME]


def get_content_from_url(link):
    # make request with the input link and return the content of the web link
    sleep(SCRAPING_REQUEST_STAGGER)        
    response = requests.get(link)
    
    # if the status code of response is not 200, then raise a warning
    if response.status_code != 200:
        return False
    
    return response.content


def get_number_of_recipes(cuisine):
    # calculate number of recipes for any given cuisine
    
    # create a full link using the cuisine_link and cuisine name to obtain web content from link
    cuisine_link = URL + cuisine
    cuisine_recipes = get_content_from_url(cuisine_link)
    
    # if no content is returned from the cuisine link page
    if not cuisine_recipes:
        print "no content for:", cuisine_link
        return None  
    
    # convert web content to soup to better access the content
    soup_cuisine = BeautifulSoup(cuisine_recipes)

    # remove non-alphanumeric characters from recipe-count and convert it into integer
    return int(re.sub('\W', '', soup_cuisine.                              find("span",{"class": "recipe-count"}).get_text()))


def get_cuisine_pages(cuisine, page):
    # create link for given cuisine and page number and obtain recipe links from page 
    
    link = CUISINE_URL.format(str(page), cuisine)
    cuisine_recipe_links = get_content_from_url(link)
    if not cuisine_recipe_links:
        print "no content for:", link
        return None
    
    soup_search = BeautifulSoup(cuisine_recipe_links)

    # return the list of links for the cuisine page
    return soup_search.find("div",{"id":"article-list"}).find_all("h3")


def get_recipe(r_link):
    # make web request and obtain site content for recipe page
    recipe_link = RECIPE_URL.format(r_link)
    recipe_response = get_content_from_url(recipe_link)
    if not recipe_response:
        print "no content for:", recipe_link
        return None
    
    return BeautifulSoup(recipe_response)


def get_recipe_title(soup_recipe):
    # recipe title
    return soup_recipe.find("h1",{"itemprop":"name"}).get_text()


def get_description(soup_recipe):
    # recipe description
    summary = soup_recipe.find("p",{"itemprop":"description"})
    
    # if summary is not there for the recipe
    if not summary:
        return None
    
    return summary.get_text()



def get_recipe_ingredients(soup_recipe):
    #recipe ingredients
    ingredients_list = soup_recipe.find_all("li",{"itemprop":"ingredients"})
    ingredients = []
    for ing in ingredients_list:
        ingredients.append(ing.get_text())
    return ingredients



def get_recipe_preperation(soup_recipe):
    # recipe preperation steps
    prep_steps = soup_recipe.find_all("p", {"class":"recipe-method__list-item-text"})
    prep = []
    for step in prep_steps:
        # get text for the each step and strip of new line characters at both ends
        prep.append(step.get_text().strip())
    return prep



def get_recipe_time(soup_recipe):
    # recipe preperation time
    prep_time = soup_recipe.find("p", {"class":"recipe-metadata__prep-time"}).get_text()
    # recipe cooking time
    cooking_time = soup_recipe.find("p", {"class":"recipe-metadata__cook-time"}).get_text()
    return prep_time, cooking_time



def get_servings(soup_recipe):
    # recipe servings
    return soup_recipe.find("p", {"class":"recipe-metadata__serving"}).get_text()



def get_recommendations(soup_recipe):
    # recipe recommendations
    recommendations = soup_recipe.find("p", {"class":"recipe-metadata__recommendations"})
    if not recommendations:
        return None
    
    return recommendations.get_text()



def get_image_source(soup_recipe):
    # recipe image source
    image_source = soup_recipe.find("div", {"class":"recipe-media"})
    if not image_source:
        return None
    
    return image_source.get_text()



def get_recipe_details(recipe_links):
    # obtain necessary recipe details from recipe page
    
    cuisine_recipes = {}
    
    # loop over recipe links to get recipe details for each recipe page
    for r in recipe_links:
        recipe = {}
        recipe['r_link'] = r.a["href"]
        print "recipe link: ", recipe['r_link']
        
        sleep(SCRAPING_REQUEST_STAGGER)        
        soup_recipe = get_recipe(recipe['r_link'])
        
        recipe['recipe title'] = get_recipe_title(soup_recipe)
        recipe['description'] = get_description(soup_recipe)
        recipe['ingredient list'] = get_recipe_ingredients(soup_recipe)
        recipe['preperation steps'] = get_recipe_preperation(soup_recipe)
        recipe['prep_time'], recipe['cook_time'] = get_recipe_time(soup_recipe)
        recipe['servings'] = get_servings(soup_recipe)
        recipe['recommendations'] = get_recommendations(soup_recipe)
        recipe['image_source'] = get_image_source(soup_recipe)
        
        cuisine_recipes[recipe['recipe title']] = recipe
    
    return cuisine_recipes


def get_recipe_links(cuisine, pages):
    # loop over each page in the cuisine to obtain all the recipe details
    recipe_links = []
    
    for page in xrange(1, pages + 1):
        sleep(SCRAPING_REQUEST_STAGGER)
        # recipe links from each cuisine search page
        recipe_links.extend(get_cuisine_pages(cuisine, page))
        
    cuisine_recipes = get_recipe_details(recipe_links)
    return cuisine_recipes


def get_cuisine_recipes(cuisines):
    # loop over each cuisine and store data regarding that cuisine recipies
    
    # To store the data in a pandas Dataframe
    cuisine_df = pd.DataFrame()
    
    for cuisine in cuisines:
        cuisine_dict = {}
        
        cuisine_dict['cuisine'] = cuisine
        cuisine_dict['source'] = 'BBC Food'
        
        # obtain the number of recipes for each cuisine
        cuisine_dict['num_recipes'] = get_number_of_recipes(cuisine)
        
        # convert number of recipes into pages to scrape
        cuisine_dict['pages'] = int(ceil(cuisine_dict['num_recipes'] / 15.))

        # print the cuisine details
        print '#####'
        print "Cuisine: %s \t Number of recipes: %d \t\t Number of pages: %d"                     % (cuisine, cuisine_dict['num_recipes'], cuisine_dict['pages'])
        
        cuisine_dict['recipes_details'] = get_recipe_links(cuisine, cuisine_dict['pages'])
    
        coll.insert_one(cuisine_dict)
        
        # convert the dictionary into a dataframe and append it to the final dataframe
        cuisine_df = cuisine_df.append(pd.DataFrame.from_dict(cuisine_dict, orient='columns'), ignore_index=True)
        
    return cuisine_df 



if __name__ == '__main__':
    
    # list of cuisines on BBC Food
    cuisines = ['african', 'american', 'british', 'caribbean', 'chinese', 'east_european', 'french', 'greek', 'indian', 'irish', 'italian', 'japanese', 'mexican', 'nordic', 'north_african', 'portuguese', 'south_american', 'spanish', 'thai_and_south-east_asian', 'turkish_and_middle_eastern']
    coll.delete_many({})
    cuisine_dataframe = get_cuisine_recipes(cuisines)
    