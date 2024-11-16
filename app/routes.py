from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app, jsonify, abort
from app import db
from app.models import Commit, Attachment, Branch, BranchTransition
import markdown
import io
from werkzeug.utils import secure_filename
from datetime import datetime

bp = Blueprint('main', __name__)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'md', 'sql'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/', methods=['GET'])
def index():
    # Obtener parámetros de filtrado
    search = request.args.get('search', '').strip()
    branch_id = request.args.get('branch_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    # Construir la consulta base
    query = Commit.query

    # Aplicar filtros
    if search:
        search = f"%{search}%"
        query = query.filter(
            db.or_(
                Commit.commit_number.ilike(search),
                Commit.commit_message.ilike(search)
            )
        )
    
    if branch_id:
        query = query.filter(Commit.branch_id == branch_id)
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Commit.created_at >= date_from)
        except ValueError:
            flash('Invalid date format for Date From', 'warning')
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            # Ajustar al final del día
            date_to = date_to.replace(hour=23, minute=59, second=59)
            query = query.filter(Commit.created_at <= date_to)
        except ValueError:
            flash('Invalid date format for Date To', 'warning')

    # Ordenar por fecha de creación descendente
    commits = query.order_by(Commit.created_at.desc()).all()
    
    # Obtener todos los branches para el filtro
    branches = Branch.query.order_by(Branch.name).all()
    
    return render_template('index.html', 
                         commits=commits, 
                         branches=branches,
                         search=request.args.get('search', ''),
                         branch_id=branch_id,
                         date_from=date_from,
                         date_to=date_to)


@bp.route('/commit/new', methods=['GET', 'POST'])
def new_commit():
    if request.method == 'POST':
        try:
            jira_ticket = request.form.get('jira_ticket', '').strip()
            jira_ticket = jira_ticket.upper() if jira_ticket else ''
            
            commit = Commit(
                commit_number=int(request.form['commit_number']),
                jira_ticket=jira_ticket or None,
                branch_id=int(request.form['branch_id']),
                commit_message=request.form['commit_message'],
                long_comment=request.form['long_comment']
            )
            db.session.add(commit)
            db.session.flush()

            files = request.files.getlist('attachments')
            for file in files:
                if file and file.filename:
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_data = file.read()
                        attachment = Attachment(
                            filename=filename,
                            data=file_data,
                            commit_id=commit.id
                        )
                        db.session.add(attachment)
                    else:
                        flash(f'File {file.filename} has an unsupported format.', 'warning')

            db.session.commit()
            flash('Commit added successfully!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding commit: {str(e)}', 'danger')
            current_app.logger.error(f'Error adding commit: {str(e)}')

    branches = Branch.query.filter_by(active=True).order_by(Branch.name).all()
    return render_template('new_commit.html', branches=branches)


@bp.route('/branches', methods=['GET'])
def list_branches():
    branches = Branch.query.order_by(Branch.name).all()
    return render_template('branches.html', branches=branches)


@bp.route('/branches/new', methods=['GET', 'POST'])
def new_branch():
    if request.method == 'POST':
        try:
            branch = Branch(
                name=request.form['name'],
                description=request.form['description'],
                color=request.form['color'],
                active=bool(request.form.get('active', True)),
                order=int(request.form.get('order', 0)),
                is_independent=bool(request.form.get('is_independent', False))
            )

            # First add the branch to the session
            db.session.add(branch)
            db.session.flush()  # This will assign an ID to the branch

            # Now handle dependencies if not independent
            if not branch.is_independent and request.form.get('depends_on'):
                depends_on_id = int(request.form['depends_on'])
                depends_on_branch = Branch.query.get(depends_on_id)
                if depends_on_branch:
                    branch.add_dependency(depends_on_branch)

            # Handle allowed transitions
            try:
                allowed_transitions = request.form.getlist('allowed_transitions[]')
                for transition_id in allowed_transitions:
                    target_branch = Branch.query.get(int(transition_id))
                    if target_branch:
                        branch.add_allowed_transition(target_branch)
            except Exception as e:
                current_app.logger.error(f"Error setting allowed transitions: {str(e)}")

            db.session.commit()
            flash('Branch added successfully!', 'success')
            return redirect(url_for('main.list_branches'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding branch: {str(e)}', 'danger')
            return render_template('branch_form.html', branch=None, branches=Branch.query.all())
    return render_template('branch_form.html', branch=None, branches=Branch.query.all())


@bp.route('/branches/<int:id>/edit', methods=['GET', 'POST'])
def edit_branch(id):
    branch = Branch.query.get_or_404(id)
    if request.method == 'POST':
        try:
            branch.name = request.form['name']
            branch.description = request.form['description']
            branch.color = request.form['color']
            branch.active = bool(request.form.get('active', True))
            branch.order = int(request.form.get('order', 0))
            branch.is_independent = bool(request.form.get('is_independent', False))

            # Limpiar dependencias existentes
            for dep in branch.depends_on.all():
                branch.remove_dependency(dep)

            # Añadir nueva dependencia si no es independiente
            if not branch.is_independent and request.form.get('depends_on'):
                depends_on_id = int(request.form['depends_on'])
                depends_on_branch = Branch.query.get(depends_on_id)
                if depends_on_branch:
                    branch.add_dependency(depends_on_branch)

            try:
                # Actualizar transiciones permitidas
                current_transitions = set(t.id for t in branch.get_allowed_transitions())
                new_transitions = set(int(id) for id in request.form.getlist('allowed_transitions[]'))

                # Eliminar transiciones que ya no están seleccionadas
                for transition_id in current_transitions - new_transitions:
                    target_branch = Branch.query.get(transition_id)
                    if target_branch:
                        branch.remove_allowed_transition(target_branch)

                # Añadir nuevas transiciones seleccionadas
                for transition_id in new_transitions - current_transitions:
                    target_branch = Branch.query.get(transition_id)
                    if target_branch:
                        branch.add_allowed_transition(target_branch)
            except Exception as e:
                current_app.logger.error(f"Error updating allowed transitions: {str(e)}")

            db.session.commit()
            flash('Branch updated successfully!', 'success')
            return redirect(url_for('main.list_branches'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating branch: {str(e)}', 'danger')
    return render_template('branch_form.html', branch=branch, branches=Branch.query.all())


@bp.route('/branches/<int:id>/delete', methods=['POST'])
def delete_branch(id):
    branch = Branch.query.get_or_404(id)
    if branch.commits:
        flash('Cannot delete branch with existing commits.', 'danger')
        return redirect(url_for('main.list_branches'))
    try:
        db.session.delete(branch)
        db.session.commit()
        flash('Branch deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting branch: {str(e)}', 'danger')
    return redirect(url_for('main.list_branches'))


@bp.route('/api/branches', methods=['GET'])
def get_branches():
    branches = Branch.query.filter_by(active=True).order_by(Branch.name).all()
    return jsonify([{'id': b.id, 'name': b.name} for b in branches])


@bp.route('/commit/<int:id>', methods=['GET'])
def view_commit(id):
    commit = Commit.query.get_or_404(id)
    html_content = markdown.markdown(commit.long_comment) if commit.long_comment else ''
    branches = Branch.query.filter(Branch.id != commit.branch_id).all()
    
    # Obtener el historial de transiciones ordenado por fecha
    transitions = BranchTransition.query\
        .filter_by(commit_id=id)\
        .order_by(BranchTransition.transitioned_at.desc())\
        .all()
    
    return render_template('view_commit.html',
                         commit=commit,
                         html_content=html_content,
                         branches=branches,
                         transitions=transitions)


@bp.route('/commit/<int:id>/edit', methods=['GET', 'POST'])
def edit_commit(id):
    commit = Commit.query.get_or_404(id)
    if request.method == 'POST':
        try:
            jira_ticket = request.form.get('jira_ticket', '').strip()
            jira_ticket = jira_ticket.upper() if jira_ticket else ''
            
            commit.commit_number = int(request.form['commit_number'])
            commit.jira_ticket = jira_ticket or None
            commit.branch_id = int(request.form['branch_id'])
            commit.commit_message = request.form['commit_message']
            commit.long_comment = request.form['long_comment']

            files = request.files.getlist('attachments')
            for file in files:
                if file and file.filename:
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_data = file.read()
                        attachment = Attachment(
                            filename=filename,
                            data=file_data,
                            commit_id=commit.id
                        )
                        db.session.add(attachment)
                    else:
                        flash(f'File {file.filename} has an unsupported format.', 'warning')

            db.session.commit()
            flash('Commit updated successfully!', 'success')
            return redirect(url_for('main.view_commit', id=commit.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating commit: {str(e)}', 'danger')
            current_app.logger.error(f'Error updating commit: {str(e)}')
            return render_template('edit_commit.html', commit=commit)

    branches = Branch.query.filter_by(active=True).order_by(Branch.name).all()
    return render_template('edit_commit.html', commit=commit, branches=branches)


@bp.route('/commit/<int:id>/delete', methods=['POST'])
def delete_commit(id):
    commit = Commit.query.get_or_404(id)
    try:
        # Eliminar las transiciones primero
        BranchTransition.query.filter_by(commit_id=id).delete()
        # Eliminar el commit
        db.session.delete(commit)
        db.session.commit()
        flash('Commit deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting commit: {str(e)}')
        flash(f'Error deleting commit: {str(e)}', 'danger')
    return redirect(url_for('main.index'))


@bp.route('/commit/<int:commit_id>/attachment/<int:attachment_id>/download')
def download_attachment(commit_id, attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    
    # Verificar que el attachment pertenece al commit correcto
    if attachment.commit_id != commit_id:
        abort(404)
    
    return send_file(
        io.BytesIO(attachment.data),
        download_name=attachment.filename,
        as_attachment=True
    )


@bp.route('/attachment/<int:commit_id>/<int:attachment_id>/delete', methods=['POST'])
def delete_attachment(commit_id, attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    if attachment.commit_id != commit_id:
        flash('Invalid attachment', 'danger')
        return redirect(url_for('main.view_commit', id=commit_id))
    
    try:
        db.session.delete(attachment)
        db.session.commit()
        flash('Attachment deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting attachment: {str(e)}', 'danger')
    
    return redirect(url_for('main.view_commit', id=commit_id))


@bp.route('/commit/<int:commit_id>/transition', methods=['POST'])
def transition_commit(commit_id):
    commit = Commit.query.get_or_404(commit_id)
    try:
        to_branch_id = int(request.form['to_branch_id'])
        from_branch_id = commit.branch_id
        
        # Crear la transición
        transition = BranchTransition(
            from_branch_id=from_branch_id,
            to_branch_id=to_branch_id,
            commit_id=commit_id,
            transitioned_at=datetime.utcnow()
        )
        
        # Actualizar el branch del commit
        commit.branch_id = to_branch_id
        
        # Guardar los cambios
        db.session.add(transition)
        db.session.commit()
        
        flash('Commit moved successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error moving commit: {str(e)}', 'danger')
        current_app.logger.error(f'Error in transition_commit: {str(e)}')
    
    return redirect(url_for('main.view_commit', id=commit_id))


@bp.route('/branches/flow')
def branch_flow():
    # Obtener todos los branches ordenados por orden
    branches = Branch.query.order_by(Branch.order).all()
    
    # Separar branches independientes y del flujo principal
    independent_branches = [b for b in branches if b.is_independent]
    flow_branches = [b for b in branches if not b.is_independent]
    
    # Obtener todas las transiciones
    transitions = BranchTransition.query.order_by(BranchTransition.transitioned_at.desc()).all()
    
    return render_template('branch_flow.html',
                         flow_branches=flow_branches,
                         independent_branches=independent_branches,
                         transitions=transitions)


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500