PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL,
 role TEXT NOT NULL CHECK(role IN ('gestor','editor','leitor'))
);
CREATE TABLE IF NOT EXISTS features (
 id INTEGER PRIMARY KEY,
 name TEXT NOT NULL CHECK(length(name) BETWEEN 3 AND 120),
 kind TEXT NOT NULL CHECK(kind IN ('trilha','nascente')),
 description TEXT NOT NULL DEFAULT '',
 photo_url TEXT NOT NULL DEFAULT '',
 category TEXT NOT NULL DEFAULT '',
 geometry_file TEXT NOT NULL DEFAULT '',
 status TEXT NOT NULL CHECK(status IN ('a_verificar','conservado','atencao')),
 geometry TEXT NOT NULL,
 source TEXT NOT NULL,
 observed_on TEXT NOT NULL,
 created_by INTEGER NOT NULL REFERENCES users(id),
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
 updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
 version INTEGER NOT NULL DEFAULT 1,
 archived INTEGER NOT NULL DEFAULT 0 CHECK(archived IN (0,1))
);
CREATE INDEX IF NOT EXISTS features_kind_status ON features(kind,status,archived);
CREATE TABLE IF NOT EXISTS history (
 id INTEGER PRIMARY KEY,
 feature_id INTEGER NOT NULL REFERENCES features(id),
 actor_id INTEGER NOT NULL REFERENCES users(id),
 action TEXT NOT NULL,
 snapshot TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
