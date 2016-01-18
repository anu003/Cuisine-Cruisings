"""
##### Define all non-ascii content to be replaced in the dataset and \
##### the cooking and recipe related stop-word to be considered for possible\
##### ingredients
"""


def non_ascii_elements():
    """
    Map all non-ascii content to corresponding ascii value
    Also brackets that need to be removed from the data ('[]{}()')
    :param  none
    :return  replaced ascii encodable text content in string format
    """

    # dictionary mapping of all the observed non-ascii html characters with \
    # their ascii encodable value, as well as the brackets
    vulgar_fraction_puctuation={u'\u0101':'a', u'\u0103':'a', u'\u010d':'c',
    u'\u0113':'e', u'\u012b':'I', u'\u0137':'k', u'\u013c':'I', u'\u0146':'n',
    u'\u014d':'o', u'\u0151':'o', u'\u0153':'o', u'\u015f':'s', u'\u0161':'s',
    u'\u016b':'u', u'\u016f':'u', u'\u017b':'Z', u'\u01b0':'u', u'\u02d8':'',
    u'\u0300':'', u'\u0302':'', u'\u0308':'', u'\u0327':'', u'\u1ea5':'a',
    u'\u1eaf':'a', u'\u1ecf':'o', u'\u1edb':'o', u'\u2009':' ', u'\u200a':'',
    u'\u2013':'-', u'\u2014':'-', u'\u2018':'\'', u'\u2019':'\'',
    u'\u201a':'\'', u'\u201c':'"', u'\u201d':'"', u'\u2028':'',u'\u2031':'%..',
    u'\u2033':'"', u'\u2036':'"', u'\u2044':'/', u'\u2153':'.33',
    u'\u2154':'.66', u'\u2159':'.166', u'\u215b':'.125', u'\u215c':'.375',
    u'\u215d':'.625', u'\u2217':'*', u'\u25fe':' ', u'\u3000':' ',
    u'\u30ab':'KATAKANA ', u'\u30c3':'TU ', u'\u30d7':'PU ', u'\u5869':'salt ',
    u'\u59dc':'ginger ', u'\u62bd':'sprout ', u'\u65b0':'fresh ',
    u'\u751f':'born ', u'\u7802':'gritty ', u'\u7cbe':'', u'\u7cd6':'sugar ',
    u'\u7d39':'to join ', u'\u8001':'aged ', u'\u8208':'thrive ',
    u'\u9069':'just ', u'\u9152':'wine ' u'\u9162':'juice ', u'\u91cf':'measure ',
    u'\u9e21':'', u'\uf0a7':'1', u'\ufb01':'fi', u'\ufb02':'fl', u'\uff0c':', ',
    u'\uff10':'0', u'\uff12':'2', u'\uff15':'5', u'\uff47':'g', u'\x80':'',
    u'\x85':' ', u'\x92':'\'', u'\x99':'', u'\xa0':' ', u'\xa3':'Pound',
    u'\xa7':'z', u'\xa8':'A', u'\xa9':' ', u'\xad':'-', u'\xae':'', u'\xb0':'',
    u'\xb4':'\'', u'\xb6':'|', u'\xba':'', u'\xbb':'', u'\xbc':'.25',
    u'\xbd':'.5', u'\xbe':'.75', u'\xc0':'A', u'\xc1':'A', u'\xc2':'A',
    u'\xc3':'E', u'\xc4':'A', u'\xc9':'E', u'\xce':'I', u'\xd1':'N', u'\xd7':'X',
    u'\xde':'p', u'\xe0':'a', u'\xe1':'a', u'\xe2':'a', u'\xe3':'a', u'\xe4':'a',
    u'\xe5':'a', u'\xe6':'a', u'\xe7':'c', u'\xe8':'e', u'\xe9':'e', u'\xea':'e',
    u'\xeb':'e', u'\xec':'i', u'\xed':'i', u'\xee':'i', u'\xef':'i', u'\xf0':'o',
    u'\xf1':'n', u'\xf2':'o', u'\xf3':'o', u'\xf4':'o', u'\xf5':'o', u'\xf6':'o',
    u'\xf8':'o', u'\xf9':'u', u'\xfa':'u', u'\xfb':'u', u'\xfc':'u', u'\xfd':'y',
    u'[':'', u']':'', u'(':'', u')':'', u'{':'', u'}':''}

    return vulgar_fraction_puctuation


def recipe_stop_words_cooking():
    """
    Define stop words related to cooking methods and chemical techniques
    :param  none
    :return  set of all cooking method related stopwords
    """
    # initialize the recipe stop words and combine cooking method related \
    # stop words into one set

    # dry heating methods
    cooking_dry_heating_methods=set(['bake', 'barbecue', 'broil', 'deep fry',
        'double boiler', 'fry', 'grill', 'pan fry', 'roasted', 'sautee',
        'slow cooker', 'smoke', 'stir fry', 'sweat', 'torch', 'toast'])
    # moist heating methods
    cooking_moist_heating_methods=set(['blanch', 'boil', 'braise', 'poach',
        'scald', 'simmer', 'steam', 'stew'])
    # chemical techniques used in cooking
    chemical_techniques=set(['acidulate', 'fermente', 'marinade', 'rub',
        'brine', 'cure', 'glaze'])
    # combined set of all the cooking related stop words
    return cooking_dry_heating_methods | cooking_moist_heating_methods | \
        chemical_techniques


def recipe_stop_words_processing():
    """
    Define stop words related to food processing techniques
    :param  none
    :return  set of all food processing related stop words
    """

    # food processing techniques used in cooking
    food_processing_techniques=set(['bashed', 'beaten', 'broken', 'chopped',
        'cored', 'crumbled', 'crushed', 'cut', 'cubed', 'deseeded', 'de-seeded',
        'diced', 'fillet', 'flaked', 'floret', 'grated', 'grind', 'ground',
        'halved', 'julienned', 'juiced', 'mandoline', 'minced', 'paste', 'peeled',
        'pounded', 'pricked', 'pureed', 'quartered', 'scrubbed', 'seeded',
        'shaving', 'shelled', 'shredded', 'shucked', 'sliced', 'smashed',
        'snipped', 'skewer', 'skinned', 'squeezed', 'strip', 'trimmed', 'torn',
        'unsliced', 'zested'])
    # other techniques used for handeling food
    other_techniques=set(['brushing', 'canned', 'clean', 'coating', 'cooked',
        'cooled', 'defrosted', 'dipping', 'discarded', 'drained', 'dried', 'dry',
        'dusting', 'frozen', 'garnish', 'greasing', 'heaped', 'melted',
        'microwave', 'mixed', 'packed', 'pitted', 'refrigerate', 'removed',
        'rinsed', 'separated', 'serving', 'sifted', 'sieved', 'soaked',
        'softened', 'taste', 'thinned', 'unpeeled', 'washed', 'wiped'
    # combined set of all the food processing techniques
    return food_processing_techniques | other_techniques


def recipe_stop_words_sizes():
    """
    Define stop words related to sizes and measurements
    :param  none
    :return  set of all sizes and measurements related stopwords
    """

    # words that indicate size of of ingredient or amount of heat
    sizes=set(['approximate', 'assembling', 'bag', 'batch', 'baton', 'bottle',
        'box', 'bunches', 'can', 'carton', 'chunk', 'coarsely', 'dash',
        'drizzle', 'equivalent', 'finely', 'halves', 'handful', 'heaped',
        'jar', 'kernel', 'knob', 'large', 'lengthways', 'lightly', 'little',
        'loaf', 'medium', 'medium-large', 'package', 'packet', 'piece', 'pod',
        'roughly', 'rounded', 'scattering', 'season', 'segment', 'size', 'small',
        'sprig', 'splash', 'square', 'squirt', 'stick', 'temperature', 'thickly',
        'thinly', 'tin', 'tub', 'wedge', 'weight', 'whole'])
    # units used to measure food, heat or time
    measurements=set(['centimeter', 'cm', 'celsius', 'centigrade', 'c', 'cup',
        'drop', 'fahrenheit', 'f', 'fluid ounce', 'fl oz', 'gallon', 'gal', 'gill',
        'gram', 'g', 'inch', 'in', 'kilogram', 'kg', 'liter', 'l', 'milliliter',
        'ml', 'minute', 'min', 'ounce', 'oz', 'pinch', 'pint', 'pt', 'pound', 'lb',
        'quart', 'qt', 'second', 'sec', 'tablespoon', 'tbsp', 'teaspoon', 'tsp'])
    # combined set of all sizes and measurements related stop words
    return sizes | measurements


def recipe_stop_words_other():
    """
    Define stop words related to sizes and measurements
    :param  none
    :return  set of all sizes and measurements related stopwords
    """

    # words indicating the quality and kind of ingredients and some instruments
    other_food_related_stopwords=set(['back', 'breast', 'boneless', 'bone-in',
        'calorie', 'cocktail', 'cold', 'controlled', 'crusty', 'fat', 'fat-free',
        'firm', 'flesh', 'fore', 'fork', 'free-range', 'freshly', 'full-fat',
        'good-quality', 'head', 'lean', 'leg', 'extra', 'long-grain', 'low-fat',
        'middle', 'mortar', 'natural', 'optional', 'ordinary', 'organic',
        'overnight', 'pestle', 'rack', 'raw', 'ready-made', 'recipe', 'rib',
        'rind', 'ripe', 'room', 'seasonally', 'seed', 'skinless', 'stalk', 'stem',
        'stone', 'thigh', 'topside', 'uncooked', 'wholegrain'])
    # other words seen in recipes that are not ingredients \
    # but do not belong to any other groups
    other_stopwords=set(['according', 'add', 'aka', 'also', 'alternatively',
        'aside', 'available', 'bought', 'brand', 'butcher', 'choice',
        'confectionery', 'controlled', 'divided', 'divine', 'horizontally',
        'imagine', 'instruction', 'jointed', 'keep', 'known', 'like', 'look',
        'made', 'may', 'much', 'new', 'need', 'online', 'placed', 'preferably',
        'preferred', 'quality', 'scatter', 'similar', 'spare', 'specialist',
        'store-bought', 'stunning', 'substitte', 'together', 'used', 'well',
        'work'])
    # combined set of all the other stopwords
    return other_food_related_stopwords | other_stopwords


