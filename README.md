# Commit Tracker

A powerful web application for tracking and managing software development commits across different branches with advanced dependency and transition features.

## 🚀 Features

### Branch Management
- **Branch Flow Visualization**: Interactive diagram showing branch relationships and dependencies
- **Commit Counter**: Visual indicators showing number of commits per branch
- **Tooltips**: Hover over branches to see detailed commit information
- **Branch Dependencies**: Define and validate branch relationships
- **Independent Branches**: Support for branches outside the main flow
- **Branch Ordering**: Customizable branch order for deployment flows

### Commit Management
- **VSTFS Integration**: Track Visual Studio Team Foundation Server commits
- **JIRA Integration**: Link commits to JIRA tickets
- **Markdown Support**: Rich text formatting for commit descriptions
- **File Attachments**: Support for multiple file attachments per commit
- **Smart File Handling**: 
  - Automatic file attachment for images
  - Intelligent paste handling based on context
  - Support for drag & drop

### Commit Transitions
- **Branch Transitions**: Move commits between branches
- **Transition History**: Track all commit movements
- **Dependency Validation**: Prevent invalid transitions
- **Recent Activity**: View recent commit transitions

### UI/UX
- **Dark Theme**: Modern dark theme design
- **Responsive Layout**: Works on desktop and mobile
- **Interactive Diagrams**: Using Mermaid.js for flow visualization
- **Bootstrap 5**: Modern and responsive design
- **FontAwesome Icons**: Clear visual indicators

## 🛠 Technical Stack
- **Backend**: Python/Flask
- **Database**: SQLAlchemy ORM
- **Frontend**: 
  - Bootstrap 5
  - JavaScript
  - Mermaid.js
- **Features**:
  - Markdown rendering
  - File upload/download
  - Dynamic tooltips
  - Interactive diagrams

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/commit-tracker.git
cd commit-tracker
```
2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```
5. Run the application:
```bash
flask run
```
## 💡 Usage

### Branch Setup
1. Create branches with appropriate order and dependencies
2. Define independent branches for hotfixes or parallel development
3. Customize branch colors for visual distinction

### Commit Management
1. Create commits with VSTFS numbers and optional JIRA tickets
2. Add detailed descriptions using Markdown
3. Attach relevant files (images, documents, etc.)
4. Move commits between branches following defined flows

### Viewing and Reporting
1. View branch flow diagram
2. Track commit transitions
3. Monitor branch dependencies
4. View commit details and attachments

## 🔒 Security Features
- Attachment ownership validation
- Branch transition validation
- Input sanitization
- Error handling and logging

## 🤝 Contributing
Contributions are welcome! Please feel free to submit pull requests.

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments
- Flask team for the excellent web framework
- Mermaid.js for flow visualization
- Bootstrap team for the UI framework

