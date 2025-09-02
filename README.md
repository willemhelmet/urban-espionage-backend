# Example disco Django Postgres Site

[See the documentation here](https://docs.letsdisco.dev/deployment-guides/django-postgres)

---

## how to run locally

### first time

- make a copy of the `.env.example` file and call the copy `.env`
- fill out the `DJANGO_SECRET_KEY` value in `.env` with a random secret-ish string
- setup a local postgres database and point to it in `.env`
  - on macs, we suggest using [Postgres.app](https://postgresapp.com/)
  - you can also use [Postico](https://eggerapps.at/postico2/) to manage your local databases
  - the `DATABASE_URL` value in `.env` should look like `postgresql://USER@localhost:5432/SOMEDB` where USER is your username on your local computer and SOMEDB is the name of the database you created.
- then, run:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

### every time

```bash
source venv/bin/activate
python manage.py runserver
```
