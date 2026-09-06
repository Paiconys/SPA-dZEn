-- SPA Comments — database schema for MySQL Workbench
-- Open in Workbench: File → Open SQL Script… → this file
-- Or: Server → Data Import → Import from Self-Contained File
--
-- App tables only (comments). Django/captcha system tables are created by migrate.

CREATE DATABASE IF NOT EXISTS spa_dzen
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE spa_dzen;

-- Root comments: parent_id IS NULL
-- Replies: parent_id → comments_comment.id (self-FK, cascade)
CREATE TABLE IF NOT EXISTS comments_comment (
  id BIGINT NOT NULL AUTO_INCREMENT,
  username VARCHAR(250) NOT NULL,
  email VARCHAR(254) NOT NULL,
  homepage VARCHAR(200) NOT NULL DEFAULT '',
  text LONGTEXT NOT NULL,
  created_at DATETIME(6) NOT NULL,
  parent_id BIGINT NULL,
  PRIMARY KEY (id),
  CONSTRAINT comments_comment_parent_id_fk
    FOREIGN KEY (parent_id) REFERENCES comments_comment (id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS comments_attachment (
  id BIGINT NOT NULL AUTO_INCREMENT,
  file VARCHAR(100) NOT NULL,
  uploaded_at DATETIME(6) NOT NULL,
  comment_id BIGINT NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT comments_attachment_comment_id_fk
    FOREIGN KEY (comment_id) REFERENCES comments_comment (id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX comments_comment_parent_id_idx ON comments_comment (parent_id);
CREATE INDEX comments_attachment_comment_id_idx ON comments_attachment (comment_id);
