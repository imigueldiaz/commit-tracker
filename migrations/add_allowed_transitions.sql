-- Crear tabla de transiciones permitidas
CREATE TABLE IF NOT EXISTS allowed_transitions (
    from_branch_id INTEGER NOT NULL,
    to_branch_id INTEGER NOT NULL,
    PRIMARY KEY (from_branch_id, to_branch_id),
    FOREIGN KEY (from_branch_id) REFERENCES branch (id) ON DELETE CASCADE,
    FOREIGN KEY (to_branch_id) REFERENCES branch (id) ON DELETE CASCADE
);
