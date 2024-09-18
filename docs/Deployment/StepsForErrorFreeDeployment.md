# Steps for an Error-Free Back-End Deployment

## 1. **.env File Setup**
- Begin by checking out the correct branch from the repository that needs to be deployed.
- After pulling the code, ensure that all necessary details are properly filled in the `.env` file.
- **Database Credentials**: Retrieve them when your database is created.
- **Email & Climatiq Credentials**: These can be referenced from other `.env` files.
- **Zoho Credentials**: Get these details directly from the Data Analytics team. Do **not** copy Zoho credentials from other `.env` files, as this can cause conflicts on other client platforms post-deployment.
- Ensure the correct Front-End and Back-End DNS names, as well as IP addresses, are added to the `ALLOWED_HOSTS` in the `.env` file.


## 2. **Fixing CORS Errors**
Once the `.env` file setup is complete, handle any potential CORS issues by:

- Adding the Front-End and Back-End DNS and server IP addresses to `ALLOWED_HOSTS` in the `.env` file.
- Also, update `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` with these DNS or IP addresses to ensure proper cross-origin functionality in the `settings.py` file.



## 3. **Loading Data** 

### For Old Backend Code:
- **Scopes Datatable**: Add 3 objects with IDs 1, 2, and 3 to the Scopes datatable using the Django Admin Panel.
- **Client Datatable**: Create a client named "Client_for_random_users" in the Client datatable within Sustainapp.
- **Preference Section Images**: To load images for the Preference section, run the script using the command:
  ```python
  python manage.py load_data
  ```
### For New Backend Code:
- **Paths, Field Groups and DataMetrics** : Load the data into the database using the command:
  ```python
  python manage.py loaddata datemetric/fixtures/paths.json

  python manage.py loaddata datametrics/fixtures/field_groups.json

  python manage.py loaddata datametrics/fixtures/data_metrics.json
  ```
  Please load the Paths fixtures first since other 2 fixtures are dependent on it.
- **Preference Section Images**: To load images for the Preference section, run the script using the command:
  ```python
  python manage.py load_data
  ```

## 4. **Installing Packages**
- Before installing the packages, **activate the virtual environment**
- Install all required dependencies by running the command:
  ```bash
  pip install -r requirements.txt
  ```
- If you encounter "module not found" errors, even after installing the packages, double-check that the package is installed within the Virtual Environment that Gunicorn is configured to use.

---
