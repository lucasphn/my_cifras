-- =============================================================================
-- My Cifras — Migração inicial Supabase
-- Executar no: Supabase Dashboard → SQL Editor → New query → Run
-- =============================================================================

-- Extensão para gerar bytes aleatórios (tokens de compartilhamento)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- -----------------------------------------------------------------------------
-- 1. Usuários (populado no login via Google OAuth)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  google_id    text UNIQUE NOT NULL,
  email        text NOT NULL,
  name         text,
  avatar_url   text,
  is_owner     boolean DEFAULT false,
  created_at   timestamptz DEFAULT now(),
  last_seen_at timestamptz DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- 2. Visualizações por usuário / música
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS song_views (
  user_id      uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  file_id      text NOT NULL,
  view_count   integer NOT NULL DEFAULT 1,
  last_viewed  timestamptz DEFAULT now(),
  PRIMARY KEY (user_id, file_id)
);

-- -----------------------------------------------------------------------------
-- 3. Tom pessoal por usuário / música
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_tones (
  user_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  file_id       text NOT NULL,
  my_key        text,
  original_key  text,
  alt_key       text,
  my_capo       integer,
  updated_at    timestamptz DEFAULT now(),
  PRIMARY KEY (user_id, file_id)
);

-- -----------------------------------------------------------------------------
-- 4. Repertórios (setlists)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS repertories (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name        text NOT NULL,
  notes       text,
  date        date,
  color       text,
  created_at  timestamptz DEFAULT now(),
  updated_at  timestamptz DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- 5. Músicas do repertório (com ordem e tom opcional por entrada)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS repertory_songs (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  repertory_id   uuid NOT NULL REFERENCES repertories(id) ON DELETE CASCADE,
  file_id        text NOT NULL,
  position       integer NOT NULL DEFAULT 0,
  tone_override  text,
  capo_override  integer,
  added_at       timestamptz DEFAULT now(),
  UNIQUE (repertory_id, file_id)
);

-- -----------------------------------------------------------------------------
-- 6. Grupos de ministério
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS groups (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name         text NOT NULL,
  invite_code  text UNIQUE DEFAULT encode(gen_random_bytes(8), 'hex'),
  created_at   timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS group_members (
  group_id   uuid NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
  user_id    uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role       text NOT NULL DEFAULT 'member' CHECK (role IN ('admin', 'member')),
  joined_at  timestamptz DEFAULT now(),
  PRIMARY KEY (group_id, user_id)
);

-- -----------------------------------------------------------------------------
-- 7. Compartilhamentos de repertório
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS shares (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id         uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  repertory_id     uuid NOT NULL REFERENCES repertories(id) ON DELETE CASCADE,
  recipient_email  text,
  token            text UNIQUE DEFAULT encode(gen_random_bytes(16), 'hex'),
  permissions      text NOT NULL DEFAULT 'view' CHECK (permissions IN ('view', 'edit')),
  expires_at       timestamptz,
  accepted_at      timestamptz,
  created_at       timestamptz DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- Índices para buscas frequentes
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_song_views_file    ON song_views(file_id);
CREATE INDEX IF NOT EXISTS idx_user_tones_file    ON user_tones(file_id);
CREATE INDEX IF NOT EXISTS idx_repertories_user   ON repertories(user_id);
CREATE INDEX IF NOT EXISTS idx_rep_songs_rep      ON repertory_songs(repertory_id);
CREATE INDEX IF NOT EXISTS idx_group_members_user ON group_members(user_id);
CREATE INDEX IF NOT EXISTS idx_shares_token       ON shares(token);
CREATE INDEX IF NOT EXISTS idx_shares_owner       ON shares(owner_id);

-- -----------------------------------------------------------------------------
-- Row Level Security (RLS) — habilitado mas sem políticas por enquanto.
-- O Flask acessa via service_role key (bypassa RLS).
-- Políticas serão adicionadas se houver acesso client-side no futuro.
-- -----------------------------------------------------------------------------
ALTER TABLE users          ENABLE ROW LEVEL SECURITY;
ALTER TABLE song_views     ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_tones     ENABLE ROW LEVEL SECURITY;
ALTER TABLE repertories    ENABLE ROW LEVEL SECURITY;
ALTER TABLE repertory_songs ENABLE ROW LEVEL SECURITY;
ALTER TABLE groups         ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_members  ENABLE ROW LEVEL SECURITY;
ALTER TABLE shares         ENABLE ROW LEVEL SECURITY;
