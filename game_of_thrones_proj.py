# copev
# Victoria Cope

# Add imports

from bs4 import BeautifulSoup
import requests
import json
import plotly.graph_objs as go
import sqlite3

DB_NAME = 'game_of_thrones.sqlite'
#  Add baseurl for API of Ice and Fire
baseurl_api = "https://anapioficeandfire.com/api/characters?"

#  CREATE CACHE
CACHE_FILE_NAME = "got_cache.json"
CACHE_DICT = {}

def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and
    repeatably identify an API request by its baseurl and params

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs

    Returns
    -------
    string
        the unique key as a string
    '''
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector +  connector.join(param_strings)
    return unique_key

def make_request_with_api_cache(baseurl, params):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new
    request, save it, then return it.

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs

    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    request_key = construct_unique_key(baseurl, params)

    if request_key in CACHE_DICT.keys():
        print("Using cache")
        return CACHE_DICT[request_key]
    else:
        print("Fetching")
        response = requests.get(baseurl, params)
        CACHE_DICT[request_key] = response.json()
        save_cache(CACHE_DICT)
        return CACHE_DICT[request_key]

def load_cache(): # called only once, when we run the program
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache): # called whenever the cache is changed
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache, params=None):
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]     # we already have it, so return it
    else:
        print("Fetching")
        response = requests.get(url) # gotta go get it
        cache[url] = response.text # add the TEXT of the web page to the cache
        save_cache(cache)          # write the cache to disk
        return cache[url]          # return the text, which is now in the cache


# PHASE 1 - ACCESSING IMDb
class EpisodeAttributes:
    '''
    '''

    def __init__(self, season='no season', episode_number='no episode #', episode_name='no episode name', rating='no rating', ep_length='no length'):
        self.season = season
        self.episode_number = episode_number
        self.episode_name = episode_name
        self.rating = rating
        self.ep_length = ep_length

    def info(self):
        return self.episode_number + " - " + self.season + ": '" + self.episode_name + "' is " + self.ep_length + " in length," + " rated " + self.rating + "/10 stars."


def select_season():
    ''' Make a dictionary of season #'s to their respective episodes list url from "https://www.imdb.com/title/tt0944947", the Game of Thrones home page

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is season # and value is the url
        e.g. {'3': 'https://www.imdb.com/title/tt0944947/episodes?season=3', ...}
    '''

    url = 'https://www.imdb.com/title/tt0944947/'
    response = make_url_request_using_cache(url, load_cache())
    soup = BeautifulSoup(response, 'html.parser')

    keys = []
    values = []

    baseurl = 'https://www.imdb.com'
    for div in soup.find_all('div', {'class': 'seasons-and-year-nav'}):
        for season_number in div.find_all('a'):
            if season_number['href'][:32] == '/title/tt0944947/episodes?season':
                key = season_number.text.lower()
                keys.append(int(key))
                values.append(f"{baseurl}{season_number['href']}")
                season_url_dict = dict(zip(keys, values))

    l=list(season_url_dict.items())   #convert the given dict. into list

    l.sort()
    l=list(season_url_dict.items())
    l.sort(reverse=False) #sort in reverse order

    season_url_dict_ordered=dict(l)

    return season_url_dict_ordered

def make_episode_instance(season_url):
    '''
    '''
    response = make_url_request_using_cache(season_url, load_cache())
    soup = BeautifulSoup(response, 'html.parser')

    try:
        find_season = soup.find('div', class_='bp_heading').text.strip()
        season = find_season[:8]
    except:
        season = "no season # found"

    try:
        find_episode_number = soup.find('div', class_='bp_heading').text.strip()
        episode_number = find_episode_number[11:]
    except:
        episode_number = "no episode # found"

    try:
        episode_name = soup.find('h1').text.strip()
    except:
        episode_name = "no episode name found"

    try:
        rating = soup.find("span", itemprop="ratingValue").text.strip()
    except:
        rating = "no rating found"

    try:
        ep_length = soup.find("time").text.strip()
    except:
        ep_length = "no length found"

    return EpisodeAttributes(season=season, episode_number=episode_number, episode_name=episode_name, rating=rating, ep_length=ep_length)

def get_episode_urls_for_season(season_url):
    '''Make a list of episode urls for the detailed episode information page.

    Parameters
    ----------
    episode_url: string
        The URL for a state page in imdb.com

    Returns
    -------
    list
        a list of episode instances
    '''
    baseurl = "https://www.imdb.com"

    episode_link_list = []

    by_season = requests.get(season_url)
    soup = BeautifulSoup(by_season.text, 'html.parser')

    episode_by_season = soup.find_all("div", class_="list_item")

    for episode in episode_by_season:
        for ref in episode.find_all('strong'):
            for anch in ref.find_all('a'):
                val = anch['href']
                new_base = baseurl+val
                episode_link_list.append(new_base)

    return episode_link_list

def create_instances_from_url(episode_url_list):
    '''
    creates instances of episodes based on the urls in the list
    '''

    episode_detail_list = []

    for item in episode_url_list:
        instance = make_episode_instance(item)
        episode_detail_list.append(instance)

    return episode_detail_list

def format_episode_list(item_list):
    '''
    '''
    format_list = []
    count = 0

    for items in item_list:
        x = items.info()
        count += 1
        format_list.append(x)
        print(f"[{count}] {x}")

def view_characters_in_episode(episode_url):
    '''
    '''
    response = requests.get(episode_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    character_names = []

    cast_list = soup.find_all('td', class_="character")

    for names in cast_list:
        info = names.text.strip()
        character_names.append(info)

    character_names = [m.replace('Melisandre \n  \n  \n  (as Carice Van Houten)', 'Melisandre') for m in character_names]
    character_names = [n.replace("Eddard 'Ned' Stark \n  \n  \n  (credit only)", 'Eddard Stark') for n in character_names]
    character_names = [n.replace("Eddard 'Ned' Stark", 'Eddard Stark') for n in character_names]
    character_names = [n.replace("Lord Varys", 'Varys') for n in character_names]
    character_names = [n.replace("Izembaro \n  \n  \n  (voice)", 'Izembaro') for n in character_names]
    character_names = [n.replace("Gregor 'The Mountain' Clegane", 'Gregor Clegane') for n in character_names]
    character_names = [n.replace("Sandor 'The Hound' Clegane", 'Sandor Clegane') for n in character_names]
    character_names = [n.replace("Brynden 'Blackfish' Tully", 'Brynden Tully') for n in character_names]
    character_names = [n.replace("Maester Aemon", "Aemon Targaryen") for n in character_names]
    character_names = [p.replace("Petyr 'Littlefinger' Baelish", 'Petyr Baelish') for p in character_names]

    return character_names

def format_character_names(item_list):
    '''
    '''
    count = 0

    for items in item_list:
        count += 1
        print(f"[{count}] {items}")


# PHASE 2 - ACCESSING API OF ICE AND FIRE


def json_character(query):
    '''
    '''
    # note to self, it needs to be the full name, first names only will not work
    response = requests.get(baseurl_api, params={'name': query}).json()
    return response

def get_character_info(response):
    '''
    '''
    character_dict = {}

    for x in response:
        character_dict['name'] = x.get('name')
        character_dict['aliases'] = x.get('aliases')[:3]
        house_info = x.get('allegiances')
        for url in house_info:
            y = requests.get(url).json()
            character_dict['house'] = y.get('name')
            character_dict['words'] = y.get('words')
        character_dict['played by'] = x.get('playedBy')[0]

    return character_dict

def format_character_dict(character_dict):
    '''
    '''
    try:
        name = character_dict['name']
    except:
        name = f"Character could not be found in the database. In some cases, original names given by George R.R. Martin were changed for the production of the TV series, and may not match the database listing. Please try another character."

    try:
        played_by = character_dict['played by']
    except:
        played_by = ''

    try:
        alias = character_dict['aliases']
    except:
        alias = ''

    try:
        house = character_dict['house']
    except:
        house = ''

    try:
        words = character_dict['words']
    except:
        words = ''

    if played_by != '':
        act = f"is played by {played_by}"
    else:
        act = ''

    if alias == ['']:
        names = ''
    elif alias != '':
        names = f", otherwise known as {', '.join(str(x) for x in alias)}"
    else:
        names = ''

    if house != '':
        home = f", member of {house}"
    else:
        home = ''

    if words != '':
        w = f", whose words are {words}"
    else:
        w = ''

    return f"{name} {act}{names}{home}{w}"


def check_character_exceptions():
    ''' function to handle known errors between the API of Ice and Fire and IMDb
    #  Cersei: Cersei the Lioness, The mother of madness
    #  Ramsay has no listing
    #  Tormund
    #  Bran is listed under Brandon Stark and the 3 dictionary returned
    Gregor 'The Mountain' Clegane"
    Izembaro \n  \n  \n  (voice)
    Sandor 'The Hound' Clegane
    Yara Greyjoy
    Maester Aemon
    Ramsay 'Bolton'
    # maester pycelle = pycelle
    '''
    pass

#  PLOTLY Functions

def get_second_to_last_difference_plot():
    '''
    '''
    z = select_season()
    seasons_list = []

    for seasons in z.values():
        seasons_list.append(seasons)

    # for k, v in z.items():
    #     seasons = k

    x1 = []
    x2 = []
    for a in seasons_list:
        x = get_episode_urls_for_season(a)[-2:]
        y = create_instances_from_url(x)
        for items in y:
            r = items.rating
            x1.append(r)
            x2.append(r)
    second_ep = x1[0::2]
    last_ep = x2[1::2]

    seasons=['Season 1', 'Season 2', 'Season 3', 'Season 4', 'Season 5', 'Season 6', 'Season 7', 'Season 8']

    fig = go.Figure(data=[
        go.Bar(name='Penultimate Episode', x=seasons, y=second_ep),
        go.Bar(name='Last Episode', x=seasons, y=last_ep)
    ])
    # Change the bar mode
    fig.update_layout(barmode='group', title=f"Penultimate and Last Episode Rating of Game of Thrones by Season", xaxis_title="Season", yaxis_title="Rating")

    return fig.show()

def get_average_season_rating():
    '''
    '''
    z = select_season()

    seasons_list = []

    seasons_graph=['Season 1', 'Season 2', 'Season 3', 'Season 4', 'Season 5', 'Season 6', 'Season 7', 'Season 8']
    # for k, v in z.items():
    #     seasons_graph = k

    for seasons in z.values():
        seasons_list.append(seasons)

    season_ratings = []
    avg_season_rating = []

    for a in seasons_list:
        x = get_episode_urls_for_season(a)
        y = create_instances_from_url(x)
        sum_list = []
        season_ratings.append(sum_list)
        for items in y:
            r = float(items.rating)
            sum_list.append(r)

    for indiv in season_ratings:
        sums = 0
        for ele in indiv:
            sums += ele
        res = sums / len(indiv)
        avg_season_rating.append(round(res, 1))

    scatter_data = go.Scatter(x=seasons_graph, y=avg_season_rating)
    basic_layout = go.Layout(title=f"Average Episode Rating per Season", xaxis_title="Season Number", yaxis_title="Average Rating")
    fig = go.Figure(data=scatter_data, layout=basic_layout)

    return fig.show()

#  Create Database

# get foreign key ready
def get_ep_first_appearance():
    ''' get the episode of first (or maybe last?) appearance
    '''
    count = 0

    count_dict = {}

    z = select_season()
    seasons_list = []
    episode_list = []

    for seasons in z.values():
        seasons_list.append(seasons)

    for a in seasons_list:
        x = get_episode_urls_for_season(a)
        for items in x:
            episode_list.append(items)
    for item in episode_list:
        count += 1
        count_dict[count] = item

    all_characters = []
    character_appearance_dict = {}

    for k, v in count_dict.items():
        g = view_characters_in_episode(v)
        for q in g:
            if q not in all_characters:
                all_characters.append(q)
                character_appearance_dict[q] = k

    return character_appearance_dict

def create_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    drop_episodes_sql = 'DROP TABLE IF EXISTS "episodes"'
    drop_characters_sql = 'DROP TABLE IF EXISTS "characters"'

    create_episodes_sql = '''CREATE TABLE IF NOT EXISTS "episodes" ( 'EpisodeId' INTEGER PRIMARY KEY AUTOINCREMENT, 'SeasonNumber' TEXT NOT NULL, 'EpisodeNumber' TEXT NOT NULL, 'EpisodeName' TEXT NOT NULL, 'Length' TEXT NOT NULL, 'Rating' TEXT NOT NULL)'''

    create_characters_sql = '''CREATE TABLE IF NOT EXISTS "characters" ('CharacterId' INTEGER PRIMARY KEY AUTOINCREMENT,'CharacterName' TEXT, 'PlayedBy' TEXT, 'House' TEXT, 'Words' TEXT, 'FirstEpisodeId' INTEGER)'''

    cur.execute(drop_episodes_sql)
    cur.execute(drop_characters_sql)
    cur.execute(create_characters_sql)
    cur.execute(create_episodes_sql)
    conn.commit()
    conn.close()

def load_episode_sql():
    '''assign the episode class to the table
    '''

    insert_ep_sql = '''
        INSERT INTO episodes
        VALUES (NULL, ?, ?, ?, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    z = select_season()
    seasons_list = []

    for seasons in z.values():
        seasons_list.append(seasons)

    for a in seasons_list:
        x = get_episode_urls_for_season(a)
        y = create_instances_from_url(x)

        for episode in y:
            cur.execute(insert_ep_sql, [
                episode.season, # Season
                episode.episode_number, # Episode Number
                episode.episode_name, # Episode Name
                episode.ep_length, # Length
                episode.rating, # Rating
            ])

    conn.commit()
    conn.close()

def load_characters_sql():
    '''assign characetr information to the table
    '''

    insert_char_sql = '''
        INSERT INTO characters
        VALUES (NULL, ?, ?, ?, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    f = get_ep_first_appearance()

    for k, v in f.items():
        almost = json_character(k)
        done = get_character_info(almost)

        try:
            act = done['played by']
        except:
            act = ''

        try:
            house = done['house']
        except:
            house = ''

        try:
            words = done['words']
        except:
            words = ''

        cur.execute(insert_char_sql, [
            k, # char name
            act, # played by
            house, # house
            words, # words
            v # foreign key
        ])

    conn.commit()
    conn.close()


# COMMAND LINE

if __name__ == "__main__":

    create_db()
    load_episode_sql()
    load_characters_sql()

    count = 0
    test_count = 0

    get_average_season_rating()
    get_second_to_last_difference_plot()

    while count >= 0:

        count += 1
        test_count += 1

        ask_season = input("Enter Season # (1-8) of Game of Thrones to view episodes (e.g. 1), or 'exit' \n")
        # str(ask_season.lower()
        if ask_season == "exit":
            exit()

        if ask_season.isnumeric():
            for k, v in select_season().items():
                if ask_season.lower() == str(k):
                    print(f"\n------------------------------\nList of Episodes in Season {ask_season.capitalize()}\n------------------------------\n")
                    # x = get_episodes_for_season(v)
                    x = get_episode_urls_for_season(v)
                    y = create_instances_from_url(x)
                    xlist = []
                    ylist = []
                    for items in y:
                    #     print(items.episode_name)

                        xvals = [items.episode_name][0]
                        yvals = [items.rating][0]
                        xlist.append(xvals)
                        ylist.append(yvals)

                    scatter_data = go.Scatter(x=xlist, y=ylist, mode='markers', marker={'symbol':'star', 'size': 30, 'color':'#FFD700'})
                    basic_layout = go.Layout(title=f"Episode Ratings in Season {ask_season} of Game of Thrones", xaxis_title="Episode Name", yaxis_title="Rating")
                    fig = go.Figure(data=scatter_data, layout=basic_layout)
                    fig.show()

                    char_season_count = []
                    for eps in x:
                        char_names = view_characters_in_episode(eps)
                        for i in char_names:
                            char_season_count.append(i)
                    d = {x:char_season_count.count(x) for x in char_season_count}
                    character_name, frequency_of_appearance = d.keys(), d.values()

                    xvals = tuple(character_name)
                    yvals = tuple(frequency_of_appearance)

                    bar_data = go.Bar(x=xvals, y=yvals, marker_color='crimson')
                    basic_layout = go.Layout(title=f"Frequency of Character Appearances in Season {ask_season}", xaxis_title="Character Name", yaxis_title="Number of Episodes")
                    fig = go.Figure(data=bar_data, layout=basic_layout)
                    fig.show()

                    format_episode_list(y)
                    break

            else:
                print('[Error] Enter a proper Season selection')
        else:
            print('[Error] Enter a proper Season selection')

    # add interactivity to view character per episode
        while ask_season == str(k):

            test_count += 1

            choose_ep = input("Choose a number to view a list of characters in the episode, or 'exit', or 'back' \n")

            if choose_ep == "exit":
                exit()
            if choose_ep == 'back':
                break
            if choose_ep.isalpha():
                print ('[Error] Invalid Input')

            if choose_ep.isnumeric():
                if int(choose_ep) == 0:
                    print('[Error] Invalid Input')
                elif int(choose_ep) in range(len(x)+1):
                    print(f"\n--------------------------------\nCharacters in Episode {choose_ep}\n--------------------------------\n* shows only first-billed characters per IMDb\n")
                    # print(f"\n--------------------------------\nCharacters in Episode {x[int(choose_ep) - 1]}\n--------------------------------")
                    dany = view_characters_in_episode(x[int(choose_ep)-1])
                    format_character_names(dany)
                    print('\n')

                    # format_episode_list(y)
                    break
                else:
                    print('[Error] Invalid Input')

        while test_count >= 2:

            choose_character = input("Select a character to learn more information (eg. 6), or 'exit', or 'back' \n")
            # while choose_character.isnumeric():

                # choose_character = input("Select a character to learn more information (eg. 6), or 'exit', or 'back' \n")

            if choose_character == "exit":
                exit()
            if choose_character == 'back':
                test_count -= 1
                break
            if choose_character.isalpha():
                print ('[Error] Invalid Input')

            if choose_character.isnumeric():
                if int(choose_character) == 0:
                    print('[Error] Invalid Input')
                elif int(choose_character) in range(len(dany)+1):
                    print(f"\n--------------------------------\nInformation on {dany[int(choose_character) - 1]}\n--------------------------------\n* shows only first-billed characters per IMDb\n")
                    arya = json_character(dany[int(choose_character)-1])
                    jon = get_character_info(arya)
                    print(format_character_dict(jon))
                    print('\n')
                else:
                    print('[Error] Invalid Input')

                # format_character_dict(get_character_info(json_character(dany[int(choose_character)-1])))

            format_character_names(dany)
            print('\n')



### CODE SNIPPETS ###

# def get_episodes_for_season(season_url):
#     '''Make a list of episode site instances from a url to the episode description page.

#     Parameters
#     ----------
#     episode_url: string
#         The URL for a state page in imdb.com

#     Returns
#     -------
#     list
#         a list of episode instances
#     '''
#     baseurl = "https://www.imdb.com"

#     episode_detail_list = []
#     episode_link_list = []

#     by_season = requests.get(season_url)
#     soup = BeautifulSoup(by_season.text, 'html.parser')

#     episode_by_season = soup.find_all("div", class_="list_item")

#     for episode in episode_by_season:
#         for ref in episode.find_all('strong'):
#             for anch in ref.find_all('a'):
#                 val = anch['href']
#                 episode_link_list.append(val)

#     for item in episode_link_list:
#         new_base = baseurl+item
#         instance = make_episode_instance(new_base)
#         episode_detail_list.append(instance)

#     return episode_detail_list


# while choose_character == dany:

#     another = input("Select another character, or 'back' to view episodes in the season, or 'exit' \n")

#     if another == "exit":
#         exit()
#     if another == 'back':
#         break
#     if another.isalpha():
#         print ('[Error] Invalid Input')

#     if another.isnumeric():
#         if int(another) == 0:
#             print('[Error] Invalid Input')
#         elif int(another) in range(len(dany)+1):
#             print(f"\n--------------------------------\nInformation on {dany[int(another) - 1]}\n--------------------------------\n* shows only first-billed characters per IMDb\n")
#             arya = json_character(dany[int(another)-1])
#             jon = get_character_info(arya)
#             print(format_character_dict(jon))
#             print('\n')
#             print(dany)
#         else:
#             print('[Error] Invalid Input')

# return fig.show()

            # second = items.rating[0]
#         first = items.rating[1]
#         diff = float(first) - float(second)
#         xlist.append(diff)
#         # this = items.info()
# print(xlist)

# xvals = [this.rating][0] - [this.rating][1]
# yvals = [this.season][0]
# xlist.append(xvals)
# ylist.append(yvals)
# print(xlist)
# print(ylist)


# bar_data = go.Bar(x=xvals, y=yvals)
# basic_layout = go.Layout(title="A Bar Graph")
# fig = go.Figure(data=bar_data, layout=basic_layout)



    # print(done)


    #call the shit i need to here to construct the character shit and then the foreign key(first app)
    # for names in names_list:
    #     almost = json_character(names)
    #     done = get_character_info(almost)
    #     print(done)
    #     for nums in first_app:
    #         cur.execute(insert_char_sql, [
    #             names, # char name
    #             done['played by'], # played by
    #             done['house'], # house
    #             done['words'],# words
    #             nums # foreign key
    #         ])
