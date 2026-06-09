-- Tabela de sugestões de músicas
-- Executar no SQL Editor do Supabase

CREATE TABLE IF NOT EXISTS song_suggestions (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  from_email      TEXT        NOT NULL,
  from_name       TEXT        NOT NULL DEFAULT '',
  from_picture    TEXT        NOT NULL DEFAULT '',
  song_name       TEXT        NOT NULL,
  artist          TEXT        NOT NULL DEFAULT '',
  status          TEXT        NOT NULL DEFAULT 'pending'
                              CHECK (status IN ('pending', 'fulfilled', 'rejected')),
  rejection_reason TEXT       NOT NULL DEFAULT '',
  fulfilled_file_id TEXT      NOT NULL DEFAULT '',
  fulfilled_song_name TEXT    NOT NULL DEFAULT '',
  owner_read      BOOLEAN     NOT NULL DEFAULT FALSE,
  user_read       BOOLEAN     NOT NULL DEFAULT FALSE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Índices úteis
CREATE INDEX IF NOT EXISTS idx_song_suggestions_user_id ON song_suggestions(user_id);
CREATE INDEX IF NOT EXISTS idx_song_suggestions_status  ON song_suggestions(status);

-- RLS: desabilitado (usa service key no backend, como as demais tabelas)
ALTER TABLE song_suggestions DISABLE ROW LEVEL SECURITY;
