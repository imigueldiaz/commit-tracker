from app import create_app, db
from app.models import Branch, Commit, Attachment, BranchTransition
import json
from datetime import datetime

app = create_app()

def parse_datetime(date_str):
    return datetime.fromisoformat(date_str)

def import_data():
    with app.app_context():
        with open('backup_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Importar branches
        branch_map = {}  # Para mantener el mapeo de IDs viejos a nuevos
        for branch_data in data['branches']:
            branch = Branch(
                name=branch_data['name'],
                description=branch_data['description'],
                active=branch_data['active'],
                color=branch_data['color'],
                created_at=parse_datetime(branch_data['created_at']),
                order=branch_data['order'],
                is_independent=branch_data['is_independent']
            )
            db.session.add(branch)
            db.session.flush()  # Para obtener el nuevo ID
            branch_map[branch_data['id']] = branch.id

        # Importar commits
        commit_map = {}
        for commit_data in data['commits']:
            commit = Commit(
                commit_number=commit_data['commit_number'],
                jira_ticket=commit_data['jira_ticket'],
                branch_id=branch_map[commit_data['branch_id']],
                commit_message=commit_data['commit_message'],
                long_comment=commit_data['long_comment'],
                created_at=parse_datetime(commit_data['created_at'])
            )
            db.session.add(commit)
            db.session.flush()
            commit_map[commit_data['id']] = commit.id

        # Importar attachments
        for attachment_data in data['attachments']:
            if attachment_data['data']:
                binary_data = attachment_data['data'].encode('latin1')
                attachment = Attachment(
                    filename=attachment_data['filename'],
                    data=binary_data,
                    commit_id=commit_map[attachment_data['commit_id']],
                    uploaded_at=parse_datetime(attachment_data['uploaded_at'])
                )
                db.session.add(attachment)

        # Importar dependencias de branches
        for dep in data['dependencies']:
            branch = Branch.query.get(branch_map[dep['branch_id']])
            depends_on = Branch.query.get(branch_map[dep['depends_on_id']])
            branch.add_dependency(depends_on)

        # Importar transiciones
        for transition_data in data['transitions']:
            transition = BranchTransition(
                from_branch_id=branch_map[transition_data['from_branch_id']],
                to_branch_id=branch_map[transition_data['to_branch_id']],
                commit_id=commit_map[transition_data['commit_id']],
                transitioned_at=parse_datetime(transition_data['transitioned_at'])
            )
            db.session.add(transition)

        db.session.commit()

if __name__ == '__main__':
    import_data()
    print("Data imported successfully!")