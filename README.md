# Task Manager

A Django web application for managing projects, tasks, teams, workers, positions, and task types. The project uses
class-based views, reusable list/detail mixins, Bootstrap-based templates, Select2 widgets, and a custom `Worker` user
model.

## Demo
https://task-manager-9cw3.onrender.com
- Login: `admin`
- Password: `dcgBm7gA`
> ⚠️ **If the page does not load**
>
> Please wait ~50 seconds — the server may be waking up.
> On free Render.com plans, the service sleeps after 5 minutes of inactivity and needs time to restart.

## Features

- Authentication-protected dashboard with project, team, worker, and task counters.
- CRUD pages for:
    - projects
    - tasks
    - teams
    - workers
    - positions
    - task types
- Project and task completion toggles.
- Deadline validation that prevents new past deadlines.
- Overdue status detection for project and task detail pages.
- Search, filtering, sorting, and pagination on list views.
- Paginated project task lists on project detail pages.
- Django admin configuration for core models.
- Fixture data for local development and testing.

## Tech Stack

- Python 3.12+
- Django 6.0
- SQLite
- django-environ
- django-crispy-forms with crispy-bootstrap5
- django-select2
- django-debug-toolbar
- Bootstrap / Pixel UI static assets
- flake8

## Project Structure

```text
task_manager/
├── fixtures/                  # Sample fixture data
├── static/                    # Project CSS and vendored frontend assets
├── task_manager/              # Django project settings and root URLs
├── tasks/                     # Main app: models, forms, views, tests
├── templates/                 # Shared and app templates
├── manage.py
├── requirements.txt
└── README.md
```

## Data Model

- `Position`: worker job position.
- `Worker`: custom user model extending `AbstractUser`, linked to a position.
- `Team`: group of workers.
- `Project`: project with description, deadline, completion state, and assigned teams.
- `TaskType`: task category.
- `Task`: task with type, priority, deadline, completion state, assignees, and optional project.

## Setup

1. Clone the repository and enter the project directory.

```bash
git clone <repository-url>
cd task_manager
```

2. Create and activate a virtual environment.

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the template.

Windows:

```powershell
cp .env.template .env
```

macOS/Linux:

```bash
cp .env.template .env
```

Then update `.env`:

```env
DATABASE_URL=your-db-url
SECRET_KEY=your-secret-key
DJANGO_SETTINGS_MODULE=settings-module
RENDER_EXTERNAL_HOSTNAME=host-name
```

5. Apply migrations.

```bash
python manage.py migrate
```

6. Optional: load sample data.

```bash
python manage.py loaddata fixtures/task_manager_test_db_data.json
```

7. Optional: create an admin user.

```bash
python manage.py createsuperuser
```

8. Run the development server.

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Common Commands

Run tests:

```bash
python manage.py test
```

Run linting:

```bash
flake8
```

Open the Django admin:

```text
http://127.0.0.1:8000/admin/
```

## Main Routes

| Route               | Description    |
|---------------------|----------------|
| `/`                 | Dashboard      |
| `/projects/`        | Project list   |
| `/tasks/`           | Task list      |
| `/teams/`           | Team list      |
| `/workers/`         | Worker list    |
| `/positions/`       | Position list  |
| `/task-types/`      | Task type list |
| `/accounts/login/`  | Login          |
| `/accounts/logout/` | Logout         |
| `/admin/`           | Django admin   |

## Notes

- The app uses `tasks.Worker` as `AUTH_USER_MODEL`.
- The default database is SQLite at `db.sqlite3`.
- Static frontend assets are committed under `static/assets`.
- Debug Toolbar is enabled for local development and `127.0.0.1`.
