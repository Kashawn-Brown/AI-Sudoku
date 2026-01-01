# Docker Setup Guide

This guide explains the Docker containerization setup for the Sudoku game.

## Files Created

### Dockerfiles
- `backend/Dockerfile` - Production Dockerfile for FastAPI backend
- `frontend/Dockerfile` - Production Dockerfile for React frontend (multi-stage build with nginx)
- `frontend/Dockerfile.dev` - Development Dockerfile for React frontend (with hot reload)

### Docker Compose Files
- `docker-compose.yml` - Development setup with hot reload
- `docker-compose.prod.yml` - Production setup with optimized builds

### Configuration Files
- `frontend/nginx.conf` - Nginx configuration for production frontend
- `.env.example` - Environment variables template
- `.dockerignore` files - Exclude unnecessary files from Docker builds

### Other Files
- `backend/requirements.txt` - Python dependencies (created/updated)

## Quick Start

### Development
```bash
# Start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production
```bash
# Build and start production containers
docker-compose -f docker-compose.prod.yml up --build -d

# Stop production containers
docker-compose -f docker-compose.prod.yml down
```

## Services

### Database (PostgreSQL)
- **Port**: 5432
- **Container**: `sudoku-db` (dev) / `sudoku-db-prod` (prod)
- **Volume**: `postgres_data` (persistent storage)

### Backend (FastAPI)
- **Port**: 8000
- **Container**: `sudoku-backend` (dev) / `sudoku-backend-prod` (prod)
- **Hot Reload**: Enabled in development
- **Health Check**: HTTP check on `/` endpoint

### Frontend (React)
- **Port**: 5173 (dev) / 80 (prod)
- **Container**: `sudoku-frontend` (dev) / `sudoku-frontend-prod` (prod)
- **Hot Reload**: Enabled in development
- **Production**: Served via nginx

## Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=db
DB_USER=sudoku_user
DB_PASSWORD=sudoku_pass
DB_NAME=sudoku_db
```

**Note**: For Docker, `DB_HOST` should be `db` (the service name), not `localhost`.

## Database Setup

After starting the containers, populate the database:

```bash
# Development
docker-compose exec backend python app/populate_boards.py

# Production
docker-compose -f docker-compose.prod.yml exec backend python app/populate_boards.py
```

## Access Points

### Development
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Production
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Useful Commands

```bash
# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Restart specific service
docker-compose restart backend

# View service logs
docker-compose logs backend
docker-compose logs frontend

# Execute commands in containers
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec db psql -U sudoku_user -d sudoku_db

# Remove all containers and volumes
docker-compose down -v

# Clean up Docker system
docker system prune -a
```

## Troubleshooting

### Port Conflicts
If ports are already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change host port
```

### Database Connection Issues
- Ensure `.env` file exists with correct credentials
- Wait for database health check to pass before backend starts
- Check logs: `docker-compose logs db`

### Build Failures
- Clear Docker cache: `docker-compose build --no-cache`
- Check that `requirements.txt` exists in `backend/`
- Verify all Dockerfiles are in correct locations

### Frontend Not Connecting to Backend
- Check `VITE_API_URL` environment variable
- For production, update `frontend/src/api.js` with correct backend URL
- Verify backend is running: `docker-compose ps`

## Production Deployment

For production deployment:

1. Update environment variables in `.env`
2. Use `docker-compose.prod.yml`
3. Configure reverse proxy (nginx/traefik) if needed
4. Set up SSL certificates
5. Configure domain names
6. Set up monitoring and logging

## Notes

- Development setup uses volume mounts for hot reload
- Production setup uses optimized multi-stage builds
- Database data persists in Docker volumes
- All services are on the same Docker network for communication

