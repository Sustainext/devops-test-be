# Setup

## Setting up database in postgresql

Imagine Database name is New_db
Imagine user name is New_User_be

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE New_db;
CREATE USER New_User_be WITH PASSWORD 'sustainext@1234';
ALTER ROLE New_User_be SET client_encoding TO 'utf8';
ALTER ROLE New_User_be SET default_transaction_isolation TO 'read committed';
ALTER ROLE New_User_be SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE New_db TO New_User_be;
\c New_db;
GRANT USAGE ON SCHEMA public TO New_User_be;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO New_User_be;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO New_User_be;
GRANT CREATE ON SCHEMA public TO New_User_be;
```

```Celery development Mode Start command
celery -A project_name worker --loglevel=info --pool=threads --concurrency=4

if need 1 worker use
celery -A project_name worker --loglevel=info --pool=solo

Need debugging?
use
celery -A project_name worker --loglevel=debug --pool=solo

Always run below command after full setup of celery/django
celery -A azureproject inspect active      (If you get duplicate node error then please check celery db used on env, it should be unique)

```

## Libraries required

```bash

```
