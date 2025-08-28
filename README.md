# Course Management System

A Django-based REST API for managing courses, lectures, homework, and user authentication.

## Prerequisites

- Python 3.13+
- UV package manager
- Docker & Docker Compose (optional, for containerized setup)

## Quick Start For Local Development

1. **Clone the repository**

2. **Install dependencies using UV**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your database settings
   ```

4. **Run migrations**
   ```bash
   uv run manage.py makemigrations
   uv run manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   uv run manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   uv run manage.py runserver
   ```

## API Documentation

Once the server is running, you can access:

- **API Documentation**: `http://localhost:8000/api/docs`
- **Admin Interface**: `http://localhost:8000/admin/`

## Features

- **User Authentication**: JWT-based authentication system
- **Course Management**: Create and manage courses
- **Lecture Management**: Upload and manage course lectures
- **Homework System**: Assign and grade homework assignments
- **RESTful API**: Full REST API with proper versioning
- **Admin Interface**: Django admin for easy management

## Development

- **Check code style**: `uv run ruff check .`
- **Format code**: `uv run ruff format .`
