# final-proj

## Getting Started (Installs)

from bs4 import BeautifulSoup
import requests
import json
import plotly.graph_objs as go
import sqlite3

### Running the Code: 

Run the code to get started! The project does take a little bit to get started in order to produce the database and introductory graphs that are provided before the command line begins issuing prompts, so don’t panic if it does not start right away. Once the graphs are launched, it should be relatively soon after that the interactive commands will start. The intention here is to inform you of some basic information about the series before you start your selections.

### Program Interactions: 

Interacting with the program will ask you to primarily input numbers that correspond to the supplied item. To start, begin by selecting a season of Game of Thrones to view detailed Episode information. 

From the supplied list, select an item to view the characters in an episode, or ‘back’ to select another season. 

You can now select a character to view detailed personal information available on this selection. You can also continue selecting characters in the same episode. 

Occasionally, some named characters may not return information due to a key error from the API as the IMDb listing may not match. Entering ‘back’ will return you to episode listings in the selected season.

***BEWARE the API listing for Cersei Lannister does return a rather unsavoury response for 'Aliases'. (NSFW)***
