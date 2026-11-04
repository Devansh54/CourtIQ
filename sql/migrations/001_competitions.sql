-- ==============================================================================
-- Migration: 001_competitions.sql
-- Domain: Competitions & Categories
-- Contributor: Devansh (50% Core Ownership)
-- Standards: ANSI SQL Compatible (SQLite, PostgreSQL, MySQL)
-- ==============================================================================

-- 1. Categories Table
-- Stores tournament categories and organizing bodies (e.g. ATP, WTA, ITF Men)
CREATE TABLE IF NOT EXISTS categories (
    category_id VARCHAR(50) PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

-- 2. Competitions Table
-- Stores competitions, tournaments, and events with self-referencing parent-child hierarchies
CREATE TABLE IF NOT EXISTS competitions (
    competition_id VARCHAR(50) PRIMARY KEY,
    competition_name VARCHAR(100) NOT NULL,
    parent_id VARCHAR(50) NULL,
    type VARCHAR(20) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    category_id VARCHAR(50) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories (category_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES competitions (competition_id) ON DELETE SET NULL
);

-- 3. Performance Indexes
CREATE INDEX IF NOT EXISTS idx_competitions_category_id ON competitions (category_id);
CREATE INDEX IF NOT EXISTS idx_competitions_parent_id ON competitions (parent_id);
CREATE INDEX IF NOT EXISTS idx_competitions_type ON competitions (type);
CREATE INDEX IF NOT EXISTS idx_competitions_gender ON competitions (gender);
