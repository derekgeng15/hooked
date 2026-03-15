--- stores user data ---
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_image_url TEXT,
    onboarding_vec JSONB DEFAULT '{}'::jsonb
);

--- stores artist data ---
CREATE TABLE artists(
    artist_id SERIAL PRIMARY KEY,
    artist_name TEXT NOT NULL,
    artist_image_url TEXT
);

--- stores song data ---
CREATE TABLE songs (
    song_id SERIAL PRIMARY KEY,
    song_name TEXT NOT NULL,
    album_id INTEGER REFERENCES albums(album_id),
    duration_ms INTEGER,
    preview_mp3_url TEXT,
    song_image_url TEXT,
    release_date DATE,
    genre TEXT
);

--- stores album data ---
CREATE TABLE albums(
    album_id SERIAL PRIMARY KEY,
    album_name TEXT NOT NULL,
    release_date DATE,
    cover_image_url TEXT
);

--- joins songs to artists ---
CREATE TABLE song_artists (
    song_id INTEGER REFERENCES songs(song_id),
    artist_id INTEGER REFERENCES artists(artist_id),
    PRIMARY KEY (song_id, artist_id)
);

--- stores interaction data ---
CREATE TABLE interactions (
    interaction_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    song_id INTEGER REFERENCES songs(song_id),
    interaction_type TEXT NOT NULL,
    --- actions: ["like", "dislike", "skip", "rewind"] ---
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--
--- stores user taste profiles ---
CREATE TABLE user_profiles(
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id),
    genre_weights JSONB DEFAULT '{}'::jsonb,
    artist_weights JSONB DEFAULT '{}'::jsonb,
    weight_vector JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--- self made playlists ---
CREATE TABLE playlists (
    playlist_id SERIAL PRIMARY KEY,
    owner_user_id INTEGER REFERENCES users(user_id),
    playlist_name TEXT NOT NULL,
    is_public BOOLEAN
);

CREATE TABLE playlist_tracks (
    playlist_id INTEGER REFERENCES playlists(playlist_id),
    song_id INTEGER REFERENCES songs(song_id),
    PRIMARY KEY (playlist_id, song_id)
);