# Commit Tracker

A Flask web application to track personal commits with support for markdown comments and file attachments.

## Environment Setup

1. Clone the repository
```bash
git clone <your-repository-url>
cd commit-tracker
```

2. Create and activate a virtual environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
# Copy the example environment file
cp .env-example .env

# Edit .env with your settings
# Make sure to change the SECRET_KEY!
```

5. Initialize the database
```bash
flask db upgrade
```

6. Run the application
```bash
flask run
```

The application will be available at http://localhost:5000

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project is built using the following open-source packages:

* [Flask](https://flask.palletsprojects.com/) - BSD 3-Clause License
* [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) - BSD 3-Clause License
* [SQLAlchemy](https://www.sqlalchemy.org/) - MIT License
* [Python-Markdown](https://python-markdown.github.io/) - BSD 3-Clause License
* [python-dotenv](https://github.com/theskumar/python-dotenv) - BSD 3-Clause License

Thank you to all the maintainers and contributors of these packages!