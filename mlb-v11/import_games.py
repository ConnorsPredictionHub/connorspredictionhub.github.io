#!/usr/bin/env python3
"""Import official final MLB scores into Supabase; standard library only.
Required env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY.
Never expose the service role key to browser code or commit it to Git.
Usage: python mlb-v11/import_games.py 2025
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://statsapi.mlb.com/api/v1/schedule"
def get_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "PredictionHub-MLB-V1.1/1.0"})
    with urllib.request.urlopen(req, timeout=40) as resp:
        return json.load(resp)

def fetch_games(season):
    start, end = f"{season}-03-01", f"{season}-11-30"
    params = urllib.parse.urlencode({"sportId": 1, "startDate": start, "endDate": end, "hydrate": "probablePitcher", "gameTypes": "R"})
    data = get_json(BASE + "?" + params)
    for date in data.get("dates", []):
        for g in date.get("games", []):
            if g.get("status", {}).get("abstractGameState") != "Final":
                continue
            home, away = g["teams"]["home"], g["teams"]["away"]
            if "score" not in home or "score" not in away:
                continue
            yield {
                "game_id": g["gamePk"], "season": season,
                "game_date": g["officialDate"], "game_type": g.get("gameType", "R"),
                "home_team_id": home["team"]["id"], "away_team_id": away["team"]["id"],
                "home_abbrev": home["team"].get("abbreviation") or str(home["team"]["id"]),
                "away_abbrev": away["team"].get("abbreviation") or str(away["team"]["id"]),
                "home_runs": home["score"], "away_runs": away["score"],
                "home_starting_pitcher_id": home.get("probablePitcher", {}).get("id"),
                "away_starting_pitcher_id": away.get("probablePitcher", {}).get("id"),
            }

def upload(rows):
    url = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1/mlb_historical_games?on_conflict=game_id"
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    for i in range(0, len(rows), 100):
        payload = json.dumps(rows[i:i+100]).encode()
        req = urllib.request.Request(url, data=payload, method="POST", headers={
            "apikey": key, "Authorization": "Bearer " + key,
            "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates,return=minimal"})
        with urllib.request.urlopen(req, timeout=40) as resp:
            if resp.status not in (200, 201, 204):
                raise RuntimeError(f"Unexpected HTTP status {resp.status}")
        print(f"Imported {min(i+100,len(rows))}/{len(rows)}")
        time.sleep(.1)

if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("Usage: python mlb-v11/import_games.py YEAR")
    season = int(sys.argv[1])
    if not 2010 <= season <= dt.date.today().year:
        sys.exit("Season outside supported range")
    rows = list(fetch_games(season))
    print(f"Fetched {len(rows)} completed regular-season games for {season}")
    if not rows:
        sys.exit("No completed games returned; refusing empty import")
    upload(rows)
