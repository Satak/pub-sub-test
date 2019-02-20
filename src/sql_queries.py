CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS vms (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        vm_name TEXT NOT NULL,
        namespace TEXT NOT NULL,
        message TEXT,
        UNIQUE (vm_name, namespace)
    );
"""
INSERT_RECORD = """
    INSERT INTO vms (namespace, vm_name, message)
    VALUES (:namespace, :vm_name, :message)
"""
DELETE_RECORD = """
    DELETE FROM vms WHERE
    vm_name = :vm_name AND
    namespace = :namespace
"""
SELECT_VMS = "SELECT id, vm_name, namespace, message FROM vms"
