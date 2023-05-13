import copy
import datetime
import logging

import httpx
from bs4 import BeautifulSoup

# Define the URL to fetch
IPLT20_URL = "https://www.iplt20.com/teams/{team}/squad"

TEAM_SLUGS = {
    "csk": "chennai-super-kings",
    "dc": "delhi-capitals",
    "kkr": "kolkata-knight-riders",
    "gt": "gujarat-titans",
    "lsg": "lucknow-super-giants",
    "mi": "mumbai-indians",
    "pbks": "punjab-kings",
    "rr": "rajasthan-royals",
    "rcb": "royal-challengers-bangalore",
    "srh": "sunrisers-hyderabad",
}

SAMPLE_PLAYER = {"team_id": "", "player_name": "", "avatar_url": "", "dob": 0}


async def fetch_players() -> dict:
    """
    Fetches the player data from iplt20.com
    """
    all_players = {}
    client = httpx.AsyncClient()

    # Fetch data from IPL website
    for team_id, url_slug in TEAM_SLUGS.items():
        team_url = IPLT20_URL.format(team=url_slug)
        response = await client.get(team_url)
        soup = BeautifulSoup(response.content, "html.parser")

        # find player cards
        player_elements = soup.find_all(
            "li",
            {"class": "dys-box-color ih-pcard1"},
        )
        logging.info(f"{team_id} : {len(player_elements)}")

        for element in player_elements:
            player_data = copy.deepcopy(SAMPLE_PLAYER)
            player_data["team_id"] = team_id

            # extract player page URL
            player_url = element.find("a")["href"].strip()

            # move to player page
            player_page = await client.get(player_url)
            player_soup = BeautifulSoup(player_page.content, "html.parser")

            # extract player avatar
            avatar_element = player_soup.find(
                "div",
                {"class": "membr-details-img position-relative"},
            )
            player_data["avatar_url"] = avatar_element.find("img")["src"]

            # extract player name
            player_name = avatar_element.find("h1").text.strip()
            player_data["player_name"] = player_name

            # extract DOB
            player_data_elements = player_soup.findAll(
                "div",
                {"class": "grid-items"},
            )
            for data_element in player_data_elements:
                if "Date of Birth" in data_element.text:
                    dob = data_element.find("p").text.strip()
                    break

            # convert DOB to milliseconds
            ts = datetime.datetime.strptime(dob, "%d %B %Y").timestamp() * 1000
            player_data["dob"] = int(ts)

            logging.info(f"Loaded data for: {player_name}")
            all_players[player_name] = player_data

    return all_players
