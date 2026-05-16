-- =============================================================================
-- My Cifras — Migração v2: colunas adicionais para compatibilidade
-- Executar no: Supabase Dashboard → SQL Editor → New query → Run
-- =============================================================================

-- repertories: coluna songs (armazena lista de músicas como JSONB)
ALTER TABLE repertories
  ADD COLUMN IF NOT EXISTS songs jsonb DEFAULT '[]'::jsonb;

-- shares: FKs opcionais + todos os campos do modelo atual
ALTER TABLE shares
  ALTER COLUMN owner_id     DROP NOT NULL,
  ALTER COLUMN repertory_id DROP NOT NULL;

ALTER TABLE shares
  ADD COLUMN IF NOT EXISTS rep_name      text,
  ADD COLUMN IF NOT EXISTS songs         jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS from_email    text,
  ADD COLUMN IF NOT EXISTS from_name     text,
  ADD COLUMN IF NOT EXISTS from_picture  text,
  ADD COLUMN IF NOT EXISTS to_email      text,
  ADD COLUMN IF NOT EXISTS shared_at     timestamptz DEFAULT now(),
  ADD COLUMN IF NOT EXISTS seen_by       jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS dismissed_by  jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS group_ref     text;

-- groups: membros como lista de emails (JSONB)
ALTER TABLE groups
  ADD COLUMN IF NOT EXISTS members jsonb DEFAULT '[]'::jsonb;
