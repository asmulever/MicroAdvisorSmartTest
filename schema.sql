CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE tests (
  id BIGSERIAL PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  description TEXT,
  lang VARCHAR(10) NOT NULL DEFAULT 'es',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  published_version INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE test_versions (
  id BIGSERIAL PRIMARY KEY,
  test_id BIGINT NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
  version INTEGER NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'draft',
  config_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (test_id, version)
);

CREATE TABLE questions (
  id BIGSERIAL PRIMARY KEY,
  test_version_id BIGINT NOT NULL REFERENCES test_versions(id) ON DELETE CASCADE,
  "order" INTEGER NOT NULL,
  type VARCHAR(20) NOT NULL,
  text TEXT NOT NULL,
  is_required BOOLEAN NOT NULL DEFAULT TRUE,
  rules_json JSONB,
  UNIQUE (test_version_id, "order")
);

CREATE TABLE options (
  id BIGSERIAL PRIMARY KEY,
  question_id BIGINT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  value TEXT,
  score_json JSONB,
  next_question_id BIGINT REFERENCES questions(id) ON DELETE SET NULL
);

CREATE TABLE profiles (
  id BIGSERIAL PRIMARY KEY,
  test_version_id BIGINT NOT NULL REFERENCES test_versions(id) ON DELETE CASCADE,
  code VARCHAR(20) NOT NULL,
  title TEXT NOT NULL,
  summary TEXT,
  recommendations_json JSONB,
  min_score INTEGER NOT NULL,
  max_score INTEGER NOT NULL,
  UNIQUE (test_version_id, code)
);

CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  test_version_id BIGINT NOT NULL REFERENCES test_versions(id) ON DELETE RESTRICT,
  status VARCHAR(20) NOT NULL DEFAULT 'started',
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMPTZ,
  source TEXT,
  campaign TEXT,
  user_agent_hash TEXT,
  ip_hash TEXT
);

CREATE TABLE session_answers (
  id BIGSERIAL PRIMARY KEY,
  session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  question_id BIGINT NOT NULL REFERENCES questions(id) ON DELETE RESTRICT,
  selected_option_ids BIGINT[] NOT NULL,
  value TEXT,
  answered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE share_results (
  id BIGSERIAL PRIMARY KEY,
  session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  share_token TEXT NOT NULL UNIQUE,
  profile_code VARCHAR(20) NOT NULL,
  title TEXT NOT NULL,
  summary TEXT,
  recommendations_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE analytics_daily (
  id BIGSERIAL PRIMARY KEY,
  day DATE NOT NULL,
  test_version_id BIGINT NOT NULL REFERENCES test_versions(id) ON DELETE CASCADE,
  starts INTEGER NOT NULL DEFAULT 0,
  finishes INTEGER NOT NULL DEFAULT 0,
  avg_time_sec INTEGER NOT NULL DEFAULT 0,
  source TEXT,
  campaign TEXT,
  UNIQUE (day, test_version_id, source, campaign)
);

CREATE TABLE analytics_daily_question (
  id BIGSERIAL PRIMARY KEY,
  analytics_daily_id BIGINT NOT NULL REFERENCES analytics_daily(id) ON DELETE CASCADE,
  question_id BIGINT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  drop_count INTEGER NOT NULL DEFAULT 0,
  UNIQUE (analytics_daily_id, question_id)
);

CREATE TABLE analytics_daily_profile (
  id BIGSERIAL PRIMARY KEY,
  analytics_daily_id BIGINT NOT NULL REFERENCES analytics_daily(id) ON DELETE CASCADE,
  profile_code VARCHAR(20) NOT NULL,
  count INTEGER NOT NULL DEFAULT 0,
  UNIQUE (analytics_daily_id, profile_code)
);

CREATE INDEX idx_tests_active ON tests (is_active);
CREATE INDEX idx_test_versions_test ON test_versions (test_id);
CREATE INDEX idx_questions_version ON questions (test_version_id, "order");
CREATE INDEX idx_options_question ON options (question_id);
CREATE INDEX idx_profiles_version ON profiles (test_version_id);
CREATE INDEX idx_sessions_version_status ON sessions (test_version_id, status);
CREATE INDEX idx_sessions_started_at ON sessions (started_at);
CREATE INDEX idx_analytics_daily_day ON analytics_daily (day);
CREATE INDEX idx_share_results_token ON share_results (share_token);
