from app import create_app, db
from app.models import Branch, Commit, Attachment, BranchTransition
import json
from datetime import datetime

app = create_app()

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def export_data():
    with app.app_context():
        # Exportar branches
        branches = Branch.query.all()
        branches_data = [{
            'id': b.id,
            'name': b.name,
            'description': b.description,
            'active': b.active,
            'color': b.color,
            'order': b.order,
            'is_independent': b.is_independent,
            'created_at': b.created_at,
            'dependencies': [d.id for d in b.depends_on.all()],
            'allowed_transitions': [t.id for t in b.get_allowed_transitions()]  # Añadido
        } for b in branches]

        # Exportar commits
        commits = Commit.query.all()
        commits_data = [{
            'id': c.id,
            'commit_number': c.commit_number,
            'jira_ticket': c.jira_ticket,
            'branch_id': c.branch_id,
            'commit_message': c.commit_message,
            'long_comment': c.long_comment,
            'created_at': c.created_at
        } for c in commits]

        # Exportar attachments
        attachments = Attachment.query.all()
        attachments_data = [{
            'id': a.id,
            'filename': a.filename,
            'commit_id': a.commit_id,
            'uploaded_at': a.uploaded_at,
            'data': a.data.decode('latin1') if a.data else None  # Codificar datos binarios
        } for a in attachments]

        # Exportar transiciones de branches
        transitions = BranchTransition.query.all()
        transitions_data = [{
            'id': t.id,
            'from_branch_id': t.from_branch_id,
            'to_branch_id': t.to_branch_id,
            'commit_id': t.commit_id,
            'transitioned_at': t.transitioned_at
        } for t in transitions]

        # Crear el diccionario completo de datos
        data = {
            'branches': branches_data,
            'commits': commits_data,
            'attachments': attachments_data,
            'transitions': transitions_data
        }

        # Guardar en archivo JSON
        with open('backup_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, default=serialize_datetime, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    export_data()
    print("Data exported successfully to backup_data.json")