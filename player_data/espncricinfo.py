import copy
import logging

import httpx
from bs4 import BeautifulSoup


SAMPLE_PLAYER = {
    "player_type": "batsman",
    "bowling_type": "Right Arm Fast",
    "batting_type": "Right Hand Batsman",
}

PLAYER_TYPE_MAP = {
    "middle order batter": "batsman",
    "bowling allrounder": "all-rounder",
    "opening batter": "batsman",
    "bowler": "bowler",
    "batter": "batsman",
    "allrounder": "all-rounder",
    "wicketkeeper batter": "batsman",
    "top order batter": "batsman",
    "batting allrounder": "all-rounder",
}

ESPN_BASE_URL = "https://www.espncricinfo.com"
IPL_SQUAD_URL = "/series/indian-premier-league-2023-1345038/squads"


async def fetch_players() -> dict:
    """
    Fetches the player data from espncricinfo.com
    """
    all_players = {}
    client = httpx.AsyncClient()

    # Fetch data from ESPN website
    response = await client.get(ESPN_BASE_URL + IPL_SQUAD_URL)
    soup = BeautifulSoup(response.content, "html.parser")

    # find team pages
    team_elements = soup.find_all(
        "div",
        {
            "class": "ds-flex lg:ds-flex-row sm:ds-flex-col lg:ds-items-center lg:ds-justify-between ds-py-2 ds-px-4 ds-flex-wrap odd:ds-bg-fill-content-alternate",
        },
    )

    for element in team_elements:
        team_url = ESPN_BASE_URL + element.find("a")["href"].strip()

        # move to team page
        team_page = await client.get(team_url)
        team_soup = BeautifulSoup(team_page.content, "html.parser")

        # find player cards
        player_elements = team_soup.find_all(
            "div",
            {
                "class": "ds-relative ds-flex ds-flex-row ds-space-x-4 ds-p-4 lg:ds-px-6",
            },
        )

        for player in player_elements:
            player_data = copy.deepcopy(SAMPLE_PLAYER)
            player_name = player.find(
                "span",
                {
                    "class": "ds-text-title-m ds-font-bold ds-text-typo ds-underline ds-decoration-ui-stroke hover:ds-text-typo-primary hover:ds-decoration-ui-stroke-primary ds-block",
                },
            ).text.strip()

            # extract player style and attributes
            type_text = (
                player.find("p", {"class": "ds-text-tight-l ds-mb-2 ds-mt-1"})
                .text.lower()
                .strip()
            )
            player_type = PLAYER_TYPE_MAP.get(type_text.lower(), None)
            if player_type is None:
                logging.error(f"Unknown player type: {type_text}")
                logging.error(f"{player_name} : {team_url}")
                player_type = "bowler"
            player_data["player_type"] = player_type

            player_styles = player.find_all(
                "p",
                {"class": "ds-text-tight-m ds-font-regular"},
            )
            for style in player_styles:
                if "Batting:" in style.text:
                    batting_style = style.text.strip().replace("Batting: ", "")
                    if "Left" in batting_style:
                        batting_style = "Left Hand Batsman"
                    else:
                        batting_style = "Right Hand Batsman"

                elif "Bowling:" in style.text:
                    bowling_style = style.text.strip().replace("Bowling: ", "")

            player_data["batting_type"] = batting_style
            player_data["bowling_type"] = bowling_style
            all_players[player_name] = player_data
            logging.info(f"Loaded data for: {player_name}")

    return all_players
