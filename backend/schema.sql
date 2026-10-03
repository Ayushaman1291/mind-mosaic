-- Run this in Supabase Dashboard -> SQL Editor -> New query -> Run.
-- Matches the shapes expected by db/supabase_db.py.

create table users (
  id bigint generated always as identity primary key,
  username text unique,
  name text not null,
  email text not null unique,
  password_hash text not null,
  phone text,
  address text,
  caregiver_name text,
  caregiver_phone text,
  birthday date,
  language text default 'en',
  created_at timestamptz default now()
);

create table medicines (
  id bigint generated always as identity primary key,
  user_id bigint references users(id) on delete cascade,
  name text not null,
  time text,              -- now optional: new frontend form doesn't always collect this
  dosage text              -- new: e.g. "500mg"
);

create table reminders (
  id bigint generated always as identity primary key,
  user_id bigint references users(id) on delete cascade,
  text text not null,
  time text not null,
  note text,
  done boolean default false
);

create table family_members (
  id bigint generated always as identity primary key,
  user_id bigint references users(id) on delete cascade,
  name text not null,
  relation text not null,
  photo_url text
);

create table memories (
  id bigint generated always as identity primary key,
  user_id bigint references users(id) on delete cascade,
  photo_url text not null,
  caption text
);

create table game_scores (
  id bigint generated always as identity primary key,
  user_id bigint references users(id) on delete cascade,
  game text not null,           -- 'family_quiz' | 'memory_shuffle'
  score numeric not null,
  accuracy numeric not null,
  time_taken numeric not null,
  attempts int not null,
  level_reached int,             -- how far the player got (e.g. 1-10), optional
  performance_label text,        -- 'Excellent' | 'Good' | 'Average' | 'Poor', optional
  created_at timestamptz default now()
);
