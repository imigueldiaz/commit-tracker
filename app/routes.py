from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app, jsonify
from app import db
from app.models import Commit, Attachment, Branch
import markdown
import io
from werkzeug.utils import secure_filename

bp = Blueprint('main', __name__)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'md', 'sql'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/', methods=['GET'])
def index():
    commits = Commit.query.order_by(Commit.created_at.desc()).all()
    return render_template('index.html', commits=commits)


@bp.route('/commit/new', methods=['GET', 'POST'])
def new_commit():
    if request.method == 'POST':
        try:
            commit = Commit(
                commit_number=request.form['commit_number'],
                branch_id=int(request.form['branch_id']),  # Make sure to convert to int
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
            flash(f'Error saving commit: {str(e)}', 'danger')
            return render_template('new_commit.html')

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
                active=bool(request.form.get('active', True))
            )
            db.session.add(branch)
            db.session.commit()
            flash('Branch added successfully!', 'success')
            return redirect(url_for('main.list_branches'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding branch: {str(e)}', 'danger')
            return render_template('branch_form.html')
    return render_template('branch_form.html')

@bp.route('/branches/<int:id>/edit', methods=['GET', 'POST'])
def edit_branch(id):
    branch = Branch.query.get_or_404(id)
    if request.method == 'POST':
        try:
            branch.name = request.form['name']
            branch.description = request.form['description']
            branch.active = bool(request.form.get('active', True))
            db.session.commit()
            flash('Branch updated successfully!', 'success')
            return redirect(url_for('main.list_branches'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating branch: {str(e)}', 'danger')
    return render_template('branch_form.html', branch=branch)

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
    return render_template('view_commit.html', commit=commit, html_content=html_content)


@bp.route('/commit/<int:id>/edit', methods=['GET', 'POST'])
def edit_commit(id):
    commit = Commit.query.get_or_404(id)
    if request.method == 'POST':
        try:
            commit.commit_number = request.form['commit_number']
            commit.branch_id = int(request.form['branch_id'])  # Make sure to convert to int
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
        db.session.delete(commit)
        db.session.commit()
        flash('Commit deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting commit: {str(e)}', 'danger')
        current_app.logger.error(f'Error deleting commit: {str(e)}')
    return redirect(url_for('main.index'))


@bp.route('/attachment/<int:id>', methods=['GET'])
def download_attachment(id):
    attachment = Attachment.query.get_or_404(id)
    return send_file(
        io.BytesIO(attachment.data),
        download_name=attachment.filename,
        as_attachment=True
    )


@bp.route('/attachment/<int:id>/delete', methods=['POST'])
def delete_attachment(id):
    attachment = Attachment.query.get_or_404(id)
    commit_id = attachment.commit_id
    try:
        db.session.delete(attachment)
        db.session.commit()
        flash('Attachment deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting attachment: {str(e)}', 'danger')
        current_app.logger.error(f'Error deleting attachment: {str(e)}')
    return redirect(url_for('main.view_commit', id=commit_id))


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500