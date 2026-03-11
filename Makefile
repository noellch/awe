.PHONY: dev dev-backend dev-frontend test test-backend build install clean

# Development
dev: dev-backend dev-frontend

dev-backend:
	cd backend && uv run awe-server &

dev-frontend:
	cd frontend && npm run dev -- --port 3000

# Testing
test: test-backend

test-backend:
	cd backend && uv run python -m pytest -v

# Build
build:
	cd frontend && npm run build

# Install dependencies
install:
	cd backend && uv sync
	cd frontend && npm install

# Clean
clean:
	rm -rf frontend/dist
	rm -rf backend/.awe
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
