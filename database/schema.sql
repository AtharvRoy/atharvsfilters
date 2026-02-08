CREATE TABLE teams (
  team_id TEXT PRIMARY KEY,
  team_name TEXT NOT NULL,
  home_region TEXT,
  gender TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE players (
  player_id TEXT PRIMARY KEY,
  player_name TEXT NOT NULL,
  dob DATE,
  batting_hand TEXT,
  bowling_style TEXT,
  primary_role TEXT
);

CREATE TABLE venues (
  venue_id TEXT PRIMARY KEY,
  venue_name TEXT NOT NULL,
  country TEXT,
  city TEXT,
  boundary_size_avg NUMERIC
);

CREATE TABLE matches (
  match_id TEXT PRIMARY KEY,
  start_time TIMESTAMP,
  venue_id TEXT REFERENCES venues(venue_id),
  team_a_id TEXT REFERENCES teams(team_id),
  team_b_id TEXT REFERENCES teams(team_id),
  tournament TEXT,
  stage TEXT,
  toss_winner_id TEXT REFERENCES teams(team_id),
  toss_decision TEXT,
  result TEXT,
  margin TEXT,
  day_night TEXT,
  pitch_type TEXT
);

CREATE TABLE innings (
  innings_id TEXT PRIMARY KEY,
  match_id TEXT REFERENCES matches(match_id),
  batting_team_id TEXT REFERENCES teams(team_id),
  bowling_team_id TEXT REFERENCES teams(team_id),
  innings_number INTEGER,
  runs INTEGER,
  wickets INTEGER,
  overs NUMERIC
);

CREATE TABLE deliveries (
  delivery_id TEXT PRIMARY KEY,
  match_id TEXT REFERENCES matches(match_id),
  innings_id TEXT REFERENCES innings(innings_id),
  over NUMERIC,
  ball INTEGER,
  batter_id TEXT REFERENCES players(player_id),
  bowler_id TEXT REFERENCES players(player_id),
  non_striker_id TEXT REFERENCES players(player_id),
  runs_bat INTEGER,
  runs_total INTEGER,
  wicket_type TEXT,
  extra_type TEXT,
  line TEXT,
  length TEXT,
  speed NUMERIC,
  movement NUMERIC,
  pitch_condition_id TEXT,
  phase TEXT
);

CREATE TABLE weather_snapshots (
  weather_id TEXT PRIMARY KEY,
  match_id TEXT REFERENCES matches(match_id),
  timestamp TIMESTAMP,
  humidity NUMERIC,
  wind_speed NUMERIC,
  temperature NUMERIC
);

CREATE TABLE pitch_reports (
  pitch_condition_id TEXT PRIMARY KEY,
  match_id TEXT REFERENCES matches(match_id),
  surface_friction NUMERIC,
  grass_pct NUMERIC,
  crack_score NUMERIC
);

CREATE TABLE elo_ratings (
  elo_id TEXT PRIMARY KEY,
  team_id TEXT REFERENCES teams(team_id),
  date DATE,
  elo_rating NUMERIC,
  format TEXT,
  venue_adjusted BOOLEAN
);

CREATE TABLE player_form (
  form_id TEXT PRIMARY KEY,
  player_id TEXT REFERENCES players(player_id),
  window_start DATE,
  window_end DATE,
  xR_delta NUMERIC,
  xW_delta NUMERIC,
  batting_impact NUMERIC,
  bowling_impact NUMERIC
);

CREATE TABLE upset_flags (
  upset_id TEXT PRIMARY KEY,
  match_id TEXT REFERENCES matches(match_id),
  type TEXT,
  severity TEXT,
  phase TEXT,
  contributors TEXT
);
