APP_NAME = tg_game_engine
APP_AUTHOR = vaclav-v

FILE_VSCODE_SETTINGS = .vscode/settings.json

define VSCODE_SETTINGS
echo "{" >> $(FILE_VSCODE_SETTINGS)
echo "\"python.pythonPath\": \".venv/bin/python\"," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.pylintEnabled\": false," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.flake8Enabled\": true," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.mypyEnabled\": true," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.enabled\": true," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.testing.pytestArgs\": [" >> $(FILE_VSCODE_SETTINGS)
echo "\"tests\"" >> $(FILE_VSCODE_SETTINGS)
echo "]," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.testing.unittestEnabled\": false," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.testing.nosetestsEnabled\": false," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.testing.pytestEnabled\": true" >> $(FILE_VSCODE_SETTINGS)
echo "}" >> $(FILE_VSCODE_SETTINGS)

endef


FILE_GITIGNORE = .gitignore

define GITIGNORE
echo ".venv" >> $(FILE_GITIGNORE)
echo ".vscode" >> $(FILE_GITIGNORE)
echo "*_cache" >> $(FILE_GITIGNORE)
echo "__pycache__" >> $(FILE_GITIGNORE)
echo ".python-version" >> $(FILE_GITIGNORE)

endef


init:
	pyenv local 3.9.4
	poetry init -n --name $(APP_NAME) --author $(APP_AUTHOR)
	poetry add --dev flake8
	poetry add --dev mypy
	poetry add --dev pytest
	poetry add --dev pytest-cov
	mkdir .vscode
	touch $(FILE_VSCODE_SETTINGS)
	$(VSCODE_SETTINGS)
	touch $(FILE_GITIGNORE)
	$(GITIGNORE)
	mkdir $(APP_NAME)
	touch $(APP_NAME)/__init__.py
	echo '"""Main module $(APP_NAME) project."""' > $(APP_NAME)/__init__.py
	mkdir tests
	touch tests/__init__.py
	echo '"""Tests for $(APP_NAME)."""' > tests/__init__.py
	touch tests/test_$(APP_NAME).py
	poetry shell

lint:
	poetry run flake8 $(APP_NAME)
	poetry run mypy $(APP_NAME)

install:
	poetry install

sqlalchemy:
	poetry add sqlalchemy
	poetry add psycopg2-binary
	poetry add alembic
	poetry run alembic init alembic

db_revision:
	poetry run alembic revision --autogenerate

db_update:
	poetry run alembic upgrade head
test:
	poetry run pytest tests/
test-full-diff:
	poetry run pytest -vv tests/
package-install:
	python3 -m pip -q install poetry
	poetry build -q
	python3 -m pip -q install --user dist/*.whl
coverage:
	poetry run pytest --cov=$(APP_NAME) --cov-report xml tests/
req:
	poetry export>requirements.txt