# Commit Tracker

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status: Development](https://img.shields.io/badge/Status-Development-blue)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)

A Flask web application for documenting and organizing Git commits with branch management, file attachments, and Markdown support.

## 🚀 Features

- 📝 Rich commit documentation with Markdown support
- 🌳 Branch organization and management
- 📎 File attachment support (documents, images, SQL scripts)
- 🌙 Dark mode interface
- 🔄 SQLite with migrations support
- 📱 Responsive Bootstrap design

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite, SQLAlchemy, Flask-Migrate
- **Frontend:** Bootstrap, Custom Dark Theme
- **Features:** Markdown Support, File Management
- **Development:** Git, Flask-SQLAlchemy

## 📋 Requirements

- Python 3.11+
- Git
- Web browser with JavaScript enabled

## 🚀 Installation

1. Clone the repository
```powershell
git clone https://github.com/imigueldiaz/commit-tracker.git
cd commit-tracker
```

2. Create and activate a virtual environment
```powershell
# Windows/PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies
```powershell
pip install -r requirements.txt
```

4. Set up environment variables
```powershell
# Copy the example environment file
cp .env-example .env

# Edit .env with your settings
# Make sure to change the SECRET_KEY!
```

5. Initialize the database
```powershell
flask db upgrade
```

6. Run the application
```powershell
flask run
```

The application will be available at http://localhost:5000

## 🗂️ Project Structure

```
commit-tracker/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── models.py            # Database models
│   ├── routes.py            # Application routes
│   ├── static/
│   │   └── css/            # CSS files including dark theme
│   └── templates/          # Jinja2 templates
├── migrations/             # Database migrations
├── config.py              # Configuration settings
├── requirements.txt       # Project dependencies
└── run.py                # Application entry point
```

## 🔧 Usage

1. Start by creating branches for your different development streams
2. Add commits with detailed information:
   - Commit number/hash
   - Branch selection
   - Commit message
   - Extended description (with Markdown support)
   - File attachments
3. Use the dark/light theme toggle for your preferred visualization
4. Manage branches and track your development progress

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project is built using the following open-source packages:

- Flask-SQLAlchemy - BSD 3-Clause License
- SQLAlchemy - MIT License
- Python-Markdown - BSD 3-Clause License
- python-dotenv - BSD 3-Clause License
- Flask - BSD 3-Clause License

Thank you to all the maintainers and contributors of these packages!

## 📫 Contact

Ignacio de Miguel Díaz - [@imigueldiaz](https://github.com/imigueldiaz)

Project Link: [https://github.com/imigueldiaz/commit-tracker](https://github.com/imigueldiaz/commit-tracker)
