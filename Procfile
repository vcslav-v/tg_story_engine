release: alembic upgrade head
web: gunicorn tg_game_engine.main:app --bind 0.0.0.0:$PORT -w 1