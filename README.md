# Spotify Personalized Daily Drive

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Spotipy](https://img.shields.io/badge/Spotipy-1DB954?style=flat-square&logo=spotify&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat&logo=pytest&logoColor=white)
![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![uv](https://img.shields.io/badge/uv-281032?style=flat-square&logo=uv&logoColor=DE5FEa)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/github/license/eriquinhos/spotify-personalized-daily-drive?style=flat-square)](LICENSE)

> A system to create personalized daily playlists combining curated news podcasts and user-favorite songs. Runs on any machine and automatically refreshes a Spotify playlist with your podcasts intelligently interleaved with your top tracks.

## 📋 Project Description

Spotify Personalized Daily Drive is a Python-based automation system that generates and updates a Spotify playlist every day with a structured mix of podcast episodes and personalized music recommendations. The system handles Spotify API authentication, retrieves user preferences, manages podcast content, and maintains a consistently organized playlist following a specific structure.

### Key Features

🎵 **Personalized Music Selection** — Automatically fetches your top tracks from different time periods (short/medium/long term)

🎙️ **Podcast Integration** — Includes the latest episodes from 7 curated news podcasts, intelligently interleaved with music

📅 **Daily Automation** — Runs on schedule via GitHub Actions, updating your playlist every morning at 9 AM GMT

🔐 **Secure Authentication** — OAuth2-based Spotify authentication with automatic token refresh and cache management

🏗️ **Structured Playlists** — Maintains a consistent, predictable format with podcasts and tracks perfectly balanced

🎨 **Custom Branding** — Supports custom playlist cover images

## 🚀 Setup & Execution

### Step 1: Create a Spotify Developer App

This tells Spotify your script is allowed to manage your playlists. It's free and takes 2 minutes.

1. Go to **[developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)** and log in with your Spotify account
2. Click **"Create App"**
3. Fill in the form:
    - **App name:** `Spotify Daily Drive` (or anything)
    - **App description:** `Personal playlist tool` (or anything)
    - **Redirect URI:** type in exactly: `http://localhost:8080/callback` then click **Add**
    - Check both **Web API** and **Web Playback SDK**
4. Click **"Save"**

#### Finding Your Credentials

5. On your app's page, click **"Settings"** (top right)
6. Copy your **Client ID**
7. Click **"View client secret"** to reveal your **Client Secret** — copy that too

#### Adding Yourself as an Authorized User

8. Still in Settings, scroll down to **"User Management"**
9. Type in the **email address** tied to your Spotify account and click **Add**

> **Why?** Spotify requires even the app owner to be explicitly authorized. Without this, you'll get a 403 error when the script tries to update your playlist.

### Step 2: Clone and Install

```bash
git clone https://github.com/eriquinhos/spotify-personalized-daily-drive.git
cd spotify-personalized-daily-drive

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync
```

### Step 3: Configure Credentials

Create a .env file in the project root:

```bash
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

Create a `config.yaml` file in the project root for non-secret settings:

```yaml
daily_drive:
    tracks_after_welcome: 2
    tracks_between_episodes: 4
    final_tracks: 10

podcasts:
    - key: 123_segundos
        id: 4Z5CoK9UJq3ykgLbcBTQwP
        name: 123 Segundos

    - key: cafe_da_manha
        id: 6WRTzGhq3uFxMrxHrHh1lo
        name: Café da Manhã

    - key: boletim_folha
        id: 45PqwRAJBEOdNc28ijJnIz
        name: Boletim Folha

    - key: o_assunto
        id: 4gkKyFdZzkv1eDnlTVrguk
        name: O Assunto

    - key: noticia_no_seu_tempo
        id: 3M3xXhNXudIXGNSrjvoETG
        name: Notícia no Seu Tempo

    - key: panorama_cbn
        id: 3mKy8vUlAHoLxZVaILsUWw
        name: Panorama CBN

    - key: resumao_diario
        id: 7fzhxpt0RgWaLFYydsv2b4
        name: Resumão Diário
```

The app reads secrets from `.env` and playlist-structure settings from `config.yaml`.
If `config.yaml` is missing, it falls back to the defaults above.

### Step 4: Authenticate (First Time Only)

```bash
uv run main
```

Follow the browser prompt to authorize the application. Your token will be cached automatically for future runs.

### Step 5: Deploy to GitHub Actions (Optional)

For automatic daily updates, push your credentials as GitHub Secrets:

```bash
SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET
SPOTIFY_REDIRECT_URI
SPOTIFY_CACHE (base64-encoded .cache file)
```

The workflow will automatically run daily at 9 AM GMT and update your playlist.

## 📝 Usage

### Commands Reference

| Command         | What it does                   |
| --------------- | ------------------------------ |
| `uv run main`   | Build/refresh the playlist now |
| `uv run pytest` | Run tests                      |

### Manual Playlist Update

```bash
uv run main
```

**What happens:**

- Authenticates with Spotify
- Retrieves your top 23 tracks (randomly chosen from short/medium/long term)
- Fetches the latest episodes from 7 curated news podcasts
- Updates or creates your "Personal Daily Drive" playlist with this structure:

```markdown
1 track → 123 Segundos (episode)
2 tracks → Café da Manhã (episode)
2 tracks → Boletim Folha (episode)
2 tracks → O Assunto (episode)
2 tracks → Notícia no Seu Tempo (episode)
2 tracks → Panorama CBN (episode)
2 tracks → Resumão Diário (episode)
10 remaining tracks
```

## 🎙️ Included Podcasts

The system includes these Brazilian news podcasts by default (editable in `config.yaml`):

| Podcast                  | Description                        |
| ------------------------ | ---------------------------------- |
| **123 Segundos**         | Quick 2-minute news updates        |
| **Café da Manhã**        | Morning briefing show              |
| **Boletim Folha**        | Folha de S.Paulo news bulletin     |
| **O Assunto**            | In-depth topic discussions         |
| **Notícia no Seu Tempo** | On-demand news updates             |
| **Panorama CBN**         | CBN news overview                  |
| **Resumão Diário**       | Daily summary of important stories |

## ⚙️ How It Works

1. **Authentication:** OAuth 2.0 flow — you authorize once via browser, tokens are cached and auto-refresh on subsequent runs
2. **Music Selection:** Fetches your top tracks from Spotify, randomly choosing from short-term (~4 weeks), medium-term (~6 months), or long-term (all-time) listening habits
3. **Podcast Episodes:** Retrieves the latest episode from each of the 7 subscribed podcasts
4. **Playlist Building:** Constructs a structured list of URIs following the configurable pattern from `config.yaml`
5. **Playlist Update:** Replaces the entire playlist contents via the Spotify API, or creates a new playlist if it doesn't exist
6. **Playlist Image:** Uploads a custom cover image to personalize the playlist
7. **Schedule:** Optionally runs automatically via GitHub Actions cron scheduler

## 🔧 Troubleshooting

| Problem                                                  | Solution                                                                                                                                                             |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Spotify credentials not found`                          | Create a .env file with `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, and `SPOTIFY_REDIRECT_URI`                                                                     |
| Playlist structure looks wrong                           | Check `config.yaml` for `tracks_after_welcome`, `tracks_between_episodes`, and `final_tracks`                                                                        |
| `Not authenticated!`                                     | Run `uv run main` again to re-authenticate                                                                                                                           |
| `403 Forbidden`                                          | Add your Spotify email to User Management in your app's Settings on [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard), then re-authenticate |
| `404 Not Found (podcast)`                                | Verify the podcast IDs in playlist_service.py are correct                                                                                                            |
| Playlist is empty after running                          | Check the logs — podcasts may not have recent episodes available                                                                                                     |
| `OSError: [Errno 2] No such file or directory: '.cache'` | This is normal on first run — the cache file is created after initial authentication                                                                                 |

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🎯 Roadmap & Next Steps

### Phase 1: Customization

- [ ] **Customizable Playlist Structure** — Configure number of tracks between podcasts, total playlist length, and podcast placement
- [ ] **Configurable Podcasts** — Allow users to pick their own podcasts instead of the hardcoded list
- [ ] **Configurable Time Ranges** — Let users choose which time periods to sample from (short/medium/long term)

### Phase 2: Intelligence

- [ ] **AI-Powered Music Recommendations** — Integrate ML models (scikit-learn, TensorFlow) to suggest songs based on audio features and user history
- [ ] **Genre-Based Discovery** — Recommend tracks from genres matching your listening profile
- [ ] **Artist Avoidance** — Prevent the same artists from appearing too frequently

### Phase 3: Advanced Features

- [ ] **Daylist Feature** — Create context-aware playlists that change based on time of day, day of week, and mood (inspired by [Spotify's Daylist](https://newsroom.spotify.com/2023-09-12/ever-changing-playlist-daylist-music-for-all-day/))
- [ ] **Web Dashboard** — Build a UI to view playlist history, customize settings, and preview recommendations
- [ ] **Listening Analytics** — Track and visualize listening patterns, top genres, and favorite artists over time
- [ ] **Playlist Scheduling** — Allow different playlists for different times/days (morning playlist, workout playlist, evening wind-down, etc.)
- [ ] **Real-Time Notifications** — Alert users when new episodes drop or playlist is successfully updated
- [ ] **Backup & Version History** — Keep track of playlist changes and allow rollback to previous versions

## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

⭐ If this project was helpful, please consider giving it a star!
