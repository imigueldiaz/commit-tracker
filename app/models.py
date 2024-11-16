from app import db
from datetime import datetime

# Tabla de asociación para dependencias de branches
branch_dependencies = db.Table('branch_dependencies',
    db.Column('branch_id', db.Integer, db.ForeignKey('branch.id'), primary_key=True),
    db.Column('depends_on_id', db.Integer, db.ForeignKey('branch.id'), primary_key=True)
)

# Tabla de asociación para transiciones permitidas entre branches
allowed_transitions = db.Table('allowed_transitions',
    db.Column('from_branch_id', db.Integer, db.ForeignKey('branch.id', ondelete='CASCADE'), primary_key=True),
    db.Column('to_branch_id', db.Integer, db.ForeignKey('branch.id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    color = db.Column(db.String(7), default='#6c757d')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order = db.Column(db.Integer, default=0)
    is_independent = db.Column(db.Boolean, default=False)

    # Relaciones
    commits = db.relationship('Commit', backref='branch', lazy=True)
    
    # Tabla de asociación para dependencias
    depends_on = db.relationship(
        'Branch', secondary='branch_dependencies',
        primaryjoin='Branch.id == branch_dependencies.c.branch_id',
        secondaryjoin='Branch.id == branch_dependencies.c.depends_on_id',
        backref=db.backref('dependent_branches', lazy='dynamic'),
        lazy='dynamic'
    )

    # Relación para transiciones permitidas
    allowed_transitions_to = db.relationship(
        'Branch', secondary='allowed_transitions',
        primaryjoin='Branch.id == allowed_transitions.c.from_branch_id',
        secondaryjoin='Branch.id == allowed_transitions.c.to_branch_id',
        backref=db.backref('allowed_transitions_from', lazy='dynamic'),
        lazy='dynamic'
    )

    def has_dependency(self, branch):
        return self.depends_on.filter_by(id=branch.id).first() is not None

    def add_dependency(self, branch):
        if not self.has_dependency(branch):
            self.depends_on.append(branch)

    def remove_dependency(self, branch):
        if self.has_dependency(branch):
            self.depends_on.remove(branch)

    def get_dependencies_count(self):
        return self.depends_on.count()

    def get_commits_count(self):
        return len(self.commits)

    def add_allowed_transition(self, target_branch):
        """Añade una rama como destino permitido para transiciones"""
        if not self.can_transition_to(target_branch):
            self.allowed_transitions_to.append(target_branch)

    def remove_allowed_transition(self, target_branch):
        """Elimina una rama como destino permitido para transiciones"""
        if self.can_transition_to(target_branch):
            self.allowed_transitions_to.remove(target_branch)

    def can_transition_to(self, target_branch):
        """Verifica si se puede hacer una transición a la rama objetivo"""
        try:
            transitions = self.get_allowed_transitions()
            return any(t.id == target_branch.id for t in transitions)
        except Exception:
            # Si la tabla no existe aún, permitimos todas las transiciones temporalmente
            return True

    def get_allowed_transitions(self):
        """Obtiene todas las ramas a las que se puede transicionar desde esta rama"""
        try:
            return self.allowed_transitions_to.all()
        except Exception:
            # Si la tabla no existe aún, retornamos una lista vacía
            return []

    def __repr__(self):
        return f'<Branch {self.name}>'

class BranchTransition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    to_branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    commit_id = db.Column(db.Integer, db.ForeignKey('commit.id'), nullable=False)
    transitioned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    commit = db.relationship('Commit', foreign_keys=[commit_id], back_populates='transitions')
    source = db.relationship('Branch', 
                           foreign_keys=[from_branch_id],
                           backref=db.backref('outgoing_transitions', lazy=True))
    target = db.relationship('Branch',
                           foreign_keys=[to_branch_id],
                           backref=db.backref('incoming_transitions', lazy=True))

    def __repr__(self):
        return f'<BranchTransition {self.source.name} -> {self.target.name}>'

class Commit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commit_number = db.Column(db.Integer, nullable=False)
    jira_ticket = db.Column(db.String(20), nullable=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    commit_message = db.Column(db.String(200), nullable=False)
    long_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    attachments = db.relationship('Attachment', backref='commit', lazy=True, cascade='all, delete-orphan')
    transitions = db.relationship('BranchTransition', 
                                back_populates='commit',
                                lazy=True,
                                cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Commit {self.commit_number}>'

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    data = db.Column(db.LargeBinary)
    commit_id = db.Column(db.Integer, db.ForeignKey('commit.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Attachment {self.filename}>'