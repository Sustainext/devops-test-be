## This is a README.md file


## Setting up database in postgresql
Imagine Database name is New_db
Imagine user name is New_User_be

```sql
CREATE DATABASE New_db;
CREATE USER New_User_be WITH PASSWORD 'sustainext@1234';
ALTER ROLE New_User_be SET client_encoding TO 'utf8';
ALTER ROLE New_User_be SET default_transaction_isolation TO 'read committed';
ALTER ROLE New_User_be SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE New_db TO New_User_be;
```