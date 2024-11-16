import json
from datetime import datetime
from app import create_app, db
from app.models import Branch, Commit, Attachment, BranchTransition
from sqlalchemy import select

app = create_app()

def parse_datetime(dt_str):
    if dt_str:
        return datetime.fromisoformat(dt_str)
    return None

def import_data():
    with app.app_context():
        try:
            # Cargar datos del archivo JSON
            with open('backup_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Limpiar base de datos existente
            BranchTransition.query.delete()
            Attachment.query.delete()
            Commit.query.delete()
            Branch.query.delete()
            db.session.commit()

            # Diccionario para mapear IDs viejos a nuevos
            branch_id_map = {}
            commit_id_map = {}

            # Importar branches
            for branch_data in data['branches']:
                branch = Branch(
                    name=branch_data['name'],
                    description=branch_data['description'],
                    active=branch_data['active'],
                    color=branch_data['color'],
                    order=branch_data['order'],
                    is_independent=branch_data['is_independent'],
                    created_at=parse_datetime(branch_data['created_at'])
                )
                db.session.add(branch)
                db.session.flush()  # Para obtener el nuevo ID
                branch_id_map[branch_data['id']] = branch.id

            # Establecer dependencias y transiciones permitidas
            for branch_data in data['branches']:
                # Usar db.session.get en lugar de query.get
                branch = db.session.get(Branch, branch_id_map[branch_data['id']])
                
                # Establecer dependencias
                for old_dep_id in branch_data['dependencies']:
                    if old_dep_id in branch_id_map:
                        dep_branch = db.session.get(Branch, branch_id_map[old_dep_id])
                        if dep_branch:
                            branch.add_dependency(dep_branch)

                # Establecer transiciones permitidas
                for old_trans_id in branch_data['allowed_transitions']:
                    if old_trans_id in branch_id_map:
                        target_branch = db.session.get(Branch, branch_id_map[old_trans_id])
                        if target_branch:
                            branch.add_allowed_transition(target_branch)

            # Importar commits
            for commit_data in data['commits']:
                commit = Commit(
                    commit_number=commit_data['commit_number'],
                    jira_ticket=commit_data['jira_ticket'],
                    branch_id=branch_id_map[commit_data['branch_id']],
                    commit_message=commit_data['commit_message'],
                    long_comment=commit_data['long_comment'],
                    created_at=parse_datetime(commit_data['created_at'])
                )
                db.session.add(commit)
                db.session.flush()
                commit_id_map[commit_data['id']] = commit.id

            # Importar attachments
            for attachment_data in data['attachments']:
                attachment = Attachment(
                    filename=attachment_data['filename'],
                    data=attachment_data['data'].encode('latin1') if attachment_data['data'] else None,
                    commit_id=commit_id_map[attachment_data['commit_id']],
                    uploaded_at=parse_datetime(attachment_data['uploaded_at'])
                )
                db.session.add(attachment)

            # Importar transiciones
            for transition_data in data['transitions']:
                transition = BranchTransition(
                    from_branch_id=branch_id_map[transition_data['from_branch_id']],
                    to_branch_id=branch_id_map[transition_data['to_branch_id']],
                    commit_id=commit_id_map[transition_data['commit_id']],
                    transitioned_at=parse_datetime(transition_data['transitioned_at'])
                )
                db.session.add(transition)

            db.session.commit()
            print("Data imported successfully!")

        except Exception as e:
            db.session.rollback()
            print(f"Error importing data: {str(e)}")
            raise

if __name__ == "__main__":
    import_data()