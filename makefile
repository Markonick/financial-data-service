.PHONY: install test lint run e2e

install:
	poetry install

shell:
	pyenv install 3.13
	pyenv virtualenv 3.13 neptune_3.13
	pyenv local neptune_3.13

test:
	poetry run pytest

test-v:
	poetry run pytest -v

test-vv:
	poetry run pytest -vv

test-cov:
	poetry run pytest --cov=src tests/ --cov-report=term-missing

# Usage: make test-file file=test_running_stats.py
test-file:
	poetry run pytest tests/$(file) -v

# Usage: make test-method file=test_running_stats.py method=test_running_stats_initialization
test-method:
	poetry run pytest tests/$(file) -v -k $(method)

lint:
	poetry run ruff .

lint-fix:
	poetry run ruff check . --fix 

kill-server:
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true

run: kill-server
	poetry run uvicorn src.main:app --reload

batches:
	poetry run python scripts/test_hft_stream.py

stats:
	poetry run python scripts/test_stats_stream.py

monitor:
	@PID=$$(ps aux | grep "[u]vicorn src.main:app" | awk '{print $$2}') && \
	if [ -n "$$PID" ]; then \
		htop -p "$$PID"; \
	else \
		echo "Uvicorn process not found"; \
	fi
	
start-all:
	tmux new-session -d -s financial_service \; \
		send-keys 'make run' C-m \; \
		split-window -h \; \
		send-keys 'make batches' C-m \; \
		select-layout even-horizontal \; \
		split-window -v \; \
		send-keys 'sleep 3 && make monitor' C-m \; \
		select-pane -t 0 \; \
		split-window -v \; \
		send-keys 'make stats' C-m \; \
		select-layout tiled \; \
		attach-session -d
	
kill-session:
	-tmux kill-session -t financial_service

kill-all:
	-tmux kill-server

monitor-ui:
	poetry run streamlit run scripts/monitor_ui.py

.PHONY: profile
profile:
	poetry run python -m cProfile -o profile.stats src/main.py

profile-view:
	poetry run python -m snakeviz profile.stats