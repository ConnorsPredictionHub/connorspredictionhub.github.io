-- MLB V1.1: isolated historical results storage.
-- Run only after reviewing on the target Supabase project.
create table if not exists public.mlb_historical_games (
 game_id bigint primary key,
 season integer not null check (season between 1900 and 2200),
 game_date date not null,
 game_type text not null default 'R',
 home_team_id integer not null,
 away_team_id integer not null,
 home_abbrev text not null,
 away_abbrev text not null,
 home_runs integer not null check (home_runs >= 0),
 away_runs integer not null check (away_runs >= 0),
 home_starting_pitcher_id bigint,
 away_starting_pitcher_id bigint,
 source text not null default 'MLB Stats API',
 imported_at timestamptz not null default now()
);
create index if not exists mlb_historical_games_season_date_idx on public.mlb_historical_games (season, game_date);
alter table public.mlb_historical_games enable row level security;
revoke all on public.mlb_historical_games from anon, authenticated;
-- No public read/write policy. Historical imports use server-side privileged credentials only.
