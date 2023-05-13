import asyncio
import json
import logging

from player_data import espncricinfo
from player_data import iplt20

# name mismatch between iplt20 and espn
ESPN_IPL_NAME_MISMATCH = {
    "Abdul Basith": "Abdul P A",
    "Shivam Singh": "Shivam singh",
    "Dasun Shanaka": "Dasun shanaka",
    "Aman Hakim Khan": "Aman Khan",
    "Vijaykumar Vyshak": "Vyshak Vijay Kumar",
    "Gurnoor Brar": "Gurnoor Singh Brar",
    "Praveen Dubey": "Pravin Dubey",
    "Matthew Short": "Matthew William Short",
    "Raj\xa0Bawa": "Raj Angad Bawa",
    "Varun Chakravarthy": "Varun Chakaravarthy",
    "Siddarth Kaul": "Siddharth Kaul",
    "M Shahrukh Khan": "Shahrukh Khan",
    "Arshad Khan": "Mohd. Arshad Khan",
    "Kumar Kartikeya": "Kumar Kartikeya Singh",
    "Akash Vasisht": "Akash Vashisht",
    "Shahbaz Ahmed": "Shahbaz Ahamad",
    "Samarth Vyas": "Samarth Vyas",
    "Suyash Prabhudessai": "Suyash S Prabhudessai",
    "Mohammed Shami": "Mohammad Shami",
    "Sai Sudharsan": "B. Sai Sudharsan",
    "Srikar Bharat": "K.S Bharat",
    "Harpreet Singh": "Harpreet Bhatia",
    "Baltej Singh": "Baltej Dhanda",
    "Tilak Varma": "N. Tilak Varma",
    "Ravisrinivasan Sai Kishore": "Sai Kishore",
    "Naveen-ul-Haq": "Naveen Ul Haq",
    "Upendra Yadav": "Upendra Singh Yadav",
    "Kunal Singh Rathore": "Kunal Rathore",
    "Josh Little": "Joshua Little",
    "Bhagath Varma": "K Bhagath Varma",
}

IPL_NAME_FIX = {"Samarth\xa0Vyas": "Samarth Vyas"}

MISSING_PLAYER_DATA = {
    "Karun Nair": {
        "player_type": "batsman",
        "bowling_type": "Right arm Offbreak",
        "batting_type": "Right Hand Batsman",
    },
}


async def main():
    """
    Fetch player data from websites and combine them
    Fix any errors in name and mismatched data
    """
    ipl_player_data = await iplt20.fetch_players()
    espn_player_data = await espncricinfo.fetch_players()

    # fix name edits
    for name, value in IPL_NAME_FIX.items():
        data = ipl_player_data.pop(name)
        ipl_player_data[value] = data

    # fix name mismatch
    for name, value in ESPN_IPL_NAME_MISMATCH.items():
        data = espn_player_data.pop(name)
        espn_player_data[value] = data

    # combine data
    for ele in ipl_player_data.keys():
        if ele in espn_player_data:
            data = espn_player_data.pop(ele)
            ipl_player_data[ele].update(data)

    # update missing player data
    for name, data in MISSING_PLAYER_DATA.items():
        ipl_player_data[name].update(data)

    # with open(file="player_data.json", mode="w", encoding="utf-8") as f:
    #     json.dump(ipl_player_data, f, indent=4)

    # group players by team
    team_players = {}
    for player_data in ipl_player_data.values():
        team_id = player_data["team_id"]
        if team_id not in team_players:
            team_players[team_id] = []
        team_players[team_id].append(player_data)

    with open(file="player_data.json", mode="w", encoding="utf-8") as f:
        json.dump(team_players, f, indent=4)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
