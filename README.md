# Sword World 2.5 AI GM

An AI-powered Game Master for the Sword World 2.5 tabletop RPG, implemented as a single-player isometric RPG.

## Project Overview

This project implements a complete AI Game Master for Sword World 2.5, a Japanese tabletop RPG. The system uses OpenRouter API to generate dynamic worlds, quests, and narratives while strictly adhering to the Sword World 2.5 ruleset.

## Project Structure
- `src/` - Source code for the backend API and core game logic
- `web/` - Web-based chat interface frontend
- `resources/` - Documentation, rulebooks, and project requirements
- `saves/` - Game save files (JSON format)

## Prerequisites

- Docker and Docker Compose
- OpenRouter API key (free account available at https://openrouter.ai/)

## Quick Start (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd SwordWorld2.5
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key
   ```

3. **Start the application:**
   ```bash
   docker-compose up -d
   ```

4. **Access the application:**
   - Web Interface: http://localhost
   - API Documentation: http://localhost:8000/docs

5. **Stop the application:**
   ```bash
   docker-compose down
   ```

## Manual Installation (Development)

### Backend Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key
   ```

4. **Start the API server:**
   ```bash
   python -m src.api.main
   ```

### Database Setup

The application uses PostgreSQL. You can either:

1. **Use Docker for PostgreSQL:**
   ```bash
   docker-compose up postgres -d
   ```

2. **Or set up your own PostgreSQL instance:**
   - Create database: `swordworld`
   - Create user: `swordworld` with password `swordworld`
   - Update `DATABASE_URL` in your `.env` file if needed

### Frontend Setup

The frontend is served by Nginx and can be accessed at http://localhost when using Docker Compose.

For development, you can serve the web files using any static file server:
```bash
cd web
python -m http.server 8080
```

## API Endpoints

- `POST /api/game/new` - Create a new game session
- `GET /api/game/{session_id}/state` - Get current game state
- `POST /api/game/{session_id}/action` - Process player action
- `GET /api/game/{session_id}/save` - Save current game state

## Environment Variables

- `OPENROUTER_API_KEY` - Your OpenRouter API key (required)
- `DATABASE_URL` - PostgreSQL connection string (default: postgresql://swordworld:swordworld@localhost:5432/swordworld)

## Development

### Running Tests

```bash
# Test API key
python test_api_key.py

# Test character generation
python test_character_generation.py

# Test world generation
python test_world_generation.py
```

### Project Phases

1. **Phase 1**: Web-based chat interface (Complete)
2. **Phase 2**: Isometric Godot client (Planned)

## Troubleshooting

- **Database connection issues**: Ensure PostgreSQL is running and credentials are correct
- **API key errors**: Verify your OpenRouter API key is valid and properly configured
- **Docker issues**: Check Docker logs: `docker-compose logs`
