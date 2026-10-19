# MLB V1.1 historical data — development only

This branch does not change the live MLB page or Bet Tracker.

## Steps
1. Review and apply schema.sql to the correct Supabase project.
2. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY as **server-side secrets**, never browser variables.
3. Run `python mlb-v11/import_games.py 2025` in a trusted server environment.
4. Validate row count, unique game IDs and team-season aggregates.
5. Add opponent-adjusted models and seeded simulations only after data quality checks.

Data source: MLB Stats API schedule endpoint. Current import is final **regular-season scores only**.
Probable pitcher IDs are optional and **must not be treated as verified actual starters**.
Run imports are idempotent on game_id. Future seasons must be imported separately.
Do not use this importer from GitHub Pages or commit any API secrets.
