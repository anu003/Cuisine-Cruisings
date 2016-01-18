# CuisineCruising

### Cuisine similarity analysis between various internaltional cuisines

Why do people like some cuisines and not so much some others, is this because of similarity in flavour profiles for different cuisisnes?

## Project Summary
The inspiration for this project comes from my motivation to answer the following questions using data-driven and quantitative methods:
- How can various international cuisines be compared to each other based on the ingredients used, in other words, how similar or dissimilar are cuisines?
- Also, given a person’s interest in a cuisine, how can a valid recommendation be made for other similar cuisines?

Using a database of recipes obtained from online recipe repositories, I have investigated the similarity of various cuisines in terms of ingredient combinations, number of ingredients.  Finally, for any given cuisine, using the findings from this analysis, I will recommend recipes of the most similar cuisine.

## Table of Contents
* Data Collection and Storage
* EDA and Feature engineering
* Model development
* [Visualization and web development](#Project-Summary)

## Data Collection and Storage
###### [data collection and storage](https://github.com/prathi019/CuisineCruising/tree/master/code/web_scrape) & [data cleaning and merging](https://github.com/prathi019/CuisineCruising/tree/master/code/data_cleaning_and_eda)

Using Python, BeautifulSoup and AWS EC2, web scrape [data scources]() to collect raw text, lists, and other information from html.
Details for each recipe include the following information:
*	Recipe Source (Non-Null) - Epicurious, BBC Food, Chowhound, BBD Good Food, Saveur
*	Recipe Cuisine - 45 different cuisines
*	Recipe Link (Non-Null) - url to recipes
*	Recipe Name (Non-Null) - title of recipe
*	Recipe Author/Chef - author/chef who put up the recipe
*	Recipe Rating/Recommendations - ratings and/or recommendations for recipe
*	Recipe Description - short description/summary of recipe
*	Recipe Ingredients List (Non-Null) - list of ingredients and amounts used in recipe
*	Recipe Preparation Steps (Non-Null) - preperation steps involved in recipe
*	Recipe Prep Time - prep time required for recipe
*	Recipe Cooking Time - cooking time required for recipe
*	Total Nutrition - nutrtional value of recipe
* Recipe Image Source - url to recipe image

Data from all sources is cleaned to replace all non-ascii content with their corresponding values and merged into one database of 30K recipes. Scraped data and cleaned data is stored in MongoDB, pandas dataframe in pickled file and S3 for backup.

## EDA and Feature engineering
###### [ingredient vectorizer]()
For balanced distribution of number of recipes per cuisine and better signal, the cuisines were grouped together, based on geographical closeness of cuisines, into 22 unique cuisines.

This step is quite possibly the most time-consuming, challenging, and rewarding part of the project. Using NLTK tokennization, lemmatizing, stop-words, bi-gram model and a custom built n-gram model, a list of unique ingredient names was extracted from the list of ingredients for each recipe. From these ingredient names, generate a bag of unique ingredients for all the recipes in the database.

## Model development
#### Classification Model
In the 30K recipe dataset, about 80% of recipes have cuisine labels and the remaining 20% do not have any labels. To classify these unlabled data, a classifier model was built to classify the 
#### Similarity Analysis

## Visualization and web development

![Wolrd map](https://github.com/prathi019/CuisineCruising/blob/master/images/World_map.png)


## Possible Next Steps


## Toolkit + Credits
data sources:
* [Epicurious](http://www.epicurious.com/recipesmenus)
* [BBC Food](http://www.bbc.co.uk/food/recipes)
* [Chowhound](http://www.chowhound.com/recipes)
* [BBC Good Food](http://www.bbcgoodfood.com/recipes)
* [Saveur](http://www.saveur.com/recipes)

langugages used:
* python
* bash
* html / javascript / css

python libraries used:
* [pandas](http://pandas.pydata.org/pandas-docs/version/0.17.1/index.html)
* [nltk](http://www.nltk.org/)
* [requests](http://docs.python-requests.org/en/latest/)
* [beautifulsoup](http://www.crummy.com/software/BeautifulSoup/)
* [selenium](http://selenium-python.readthedocs.org/)
* [pymongo](https://docs.mongodb.org/getting-started/python/client/) - Chosen because my database operations involve more dumping recipe details in and pulling details out than creating complex queries.
* [matplotlib](http://matplotlib.org/)
* [sklearn](http://scikit-learn.org/stable/)
* [scipy](http://www.scipy.org/), [numpy](http://www.scipy.org/)
* [pickle](https://docs.python.org/2/library/pickle.html)
* [flask](http://flask.pocoo.org/)
* [math](https://docs.python.org/2/library/math.html), [string](https://docs.python.org/2/library/string.html), [re](https://docs.python.org/2/library/re.html)
* [collections](https://docs.python.org/2/library/collections.html), [itertools](https://docs.python.org/2/library/itertools.html)

other tools used:
* [bootstrap](http://getbootstrap.com/) - for web-app
* [EC2](https://aws.amazon.com/ec2/) - for web scraping and model running
* [S3](https://aws.amazon.com/s3/) - for data back-up
* [Ammap](https://www.amcharts.com/javascript-maps/) - interactive javascript maps for visualization

## Glossary of Fancy Terms
TFIDF - [Term Frequency - Inverse Document Frequency](http://scikit-learn.org/stable/modules/feature_extraction.html)

