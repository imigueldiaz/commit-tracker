import json
from datetime import datetime
from app import create_app, db
from app.models import Branch, Commit, BranchTransition

# Datos de ejemplo
sample_data = {
    "branches": [
        {
            "name": "Development",
            "description": "Main development branch",
            "color": "#4CAF50",
            "order": 0,
            "active": True,
            "is_independent": False
        },
        {
            "name": "Integration",
            "description": "Integration testing branch",
            "color": "#2196F3",
            "order": 1,
            "active": True,
            "is_independent": False,
            "depends_on": ["Development"]
        },
        {
            "name": "QA",
            "description": "Quality assurance branch",
            "color": "#FFC107",
            "order": 2,
            "active": True,
            "is_independent": False,
            "depends_on": ["Integration"]
        },
        {
            "name": "Production",
            "description": "Production branch",
            "color": "#9C27B0",
            "order": 3,
            "active": True,
            "is_independent": False,
            "depends_on": ["QA"]
        },
        {
            "name": "Hotfix",
            "description": "Emergency fixes branch",
            "color": "#F44336",
            "order": 99,
            "active": True,
            "is_independent": True
        }
    ],
    "commits": [
        {
            "commit_number": 12345,
            "jira_ticket": "PROJ-123",
            "branch": "Development",
            "commit_message": "Add user authentication system",
            "long_comment": "## Changes\n- Implemented JWT authentication\n- Added login/register endpoints\n- Created user model\n\n## Testing\nAll tests passing \n\n```python\nclass User(db.Model):\n    id = db.Column(db.Integer, primary_key=True)\n    username = db.Column(db.String(80), unique=True)\n```",
            "transitions": [
                {
                    "from_branch": "Development",
                    "to_branch": "Integration",
                    "date": "2024-01-15T10:30:00"
                }
            ]
        },
        {
            "commit_number": 12346,
            "jira_ticket": "PROJ-124",
            "branch": "Integration",
            "commit_message": "Implement dashboard analytics",
            "long_comment": "Added new dashboard with:\n- User statistics\n- Activity graphs\n- Performance metrics",
            "transitions": []
        },
        {
            "commit_number": 12347,
            "jira_ticket": "HOTFIX-001",
            "branch": "Hotfix",
            "commit_message": "Fix critical security vulnerability",
            "long_comment": "**Emergency Fix**\n- Updated dependencies\n- Patched XSS vulnerability\n- Added security headers",
            "transitions": [
                {
                    "from_branch": "Hotfix",
                    "to_branch": "Production",
                    "date": "2024-01-16T15:45:00"
                }
            ]
        }
    ]
}

def import_data():
    app = create_app()
    with app.app_context():
        # Limpiar base de datos
        print("Limpiando base de datos...")
        db.drop_all()
        db.create_all()

        # Crear branches
        print("\nCreando branches...")
        branches = {}
        for branch_data in sample_data["branches"]:
            branch = Branch(
                name=branch_data["name"],
                description=branch_data["description"],
                color=branch_data["color"],
                order=branch_data["order"],
                active=branch_data["active"],
                is_independent=branch_data["is_independent"]
            )
            db.session.add(branch)
            branches[branch.name] = branch
        
        # Establecer dependencias
        print("Estableciendo dependencias entre branches...")
        for branch_data in sample_data["branches"]:
            if not branch_data["is_independent"] and "depends_on" in branch_data:
                for dep_name in branch_data["depends_on"]:
                    branches[branch_data["name"]].add_dependency(branches[dep_name])

        # Crear commits
        print("\nCreando commits...")
        for commit_data in sample_data["commits"]:
            commit = Commit(
                commit_number=commit_data["commit_number"],
                jira_ticket=commit_data["jira_ticket"],
                branch=branches[commit_data["branch"]],
                commit_message=commit_data["commit_message"],
                long_comment=commit_data["long_comment"]
            )
            db.session.add(commit)
            
            # Crear transiciones
            for transition in commit_data["transitions"]:
                branch_transition = BranchTransition(
                    commit=commit,
                    source=branches[transition["from_branch"]],
                    target=branches[transition["to_branch"]],
                    transitioned_at=datetime.fromisoformat(transition["date"])
                )
                db.session.add(branch_transition)

        # Guardar cambios
        print("\nGuardando cambios...")
        db.session.commit()
        print("\n¡Importación completada con éxito!")

if __name__ == "__main__":
    import_data()