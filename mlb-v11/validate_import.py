#!/usr/bin/env python3
"""Validate stored MLB season counts and unique game identifiers."""
import json, os, sys, urllib.parse, urllib.request
season=int(sys.argv[1])
base=os.environ["SUPABASE_URL"].rstrip("/")
key=os.environ["SUPABASE_SERVICE_ROLE_KEY"]
url=base+"/rest/v1/mlb_historical_games?"+urllib.parse.urlencode({"season":"eq."+str(season),"select":"game_id,home_runs,away_runs"})
req=urllib.request.Request(url,headers={"apikey":key,"Authorization":"Bearer "+key,"Accept":"application/json","Range-Unit":"items","Range":"0-2999"})
with urllib.request.urlopen(req,timeout=40) as resp: rows=json.load(resp)
ids=[r["game_id"] for r in rows]
if len(ids)<1000: raise SystemExit(f"FAIL: only {len(ids)} games for {season}")
if len(ids)!=len(set(ids)): raise SystemExit("FAIL: duplicate game IDs")
if any(r["home_runs"]<0 or r["away_runs"]<0 for r in rows): raise SystemExit("FAIL: invalid scores")
print(f"PASS: {len(rows)} unique completed games for {season}")
