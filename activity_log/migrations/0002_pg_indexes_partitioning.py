from __future__ import annotations

from django.db import migrations, connections


def pg_indexes_and_partition(apps, schema_editor):
    conn = connections[schema_editor.connection.alias]
    if conn.vendor != "postgresql":
        return
    with conn.cursor() as cur:
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_event_context_gin ON activity_event USING GIN ((context));"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_event_hash_hash ON activity_event USING HASH (hash);"
        )
        # Partition parent scaffold (optional)
        cur.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.tables WHERE table_name='activity_event_parent'
                ) THEN
                    -- Create partitioned table structure without constraints and indexes
                    -- We exclude both because PostgreSQL requires primary keys on partitioned tables
                    -- to include all partitioning columns, and INCLUDING INDEXES copies the PK index
                    CREATE TABLE activity_event_parent (
                        LIKE activity_event INCLUDING DEFAULTS EXCLUDING CONSTRAINTS EXCLUDING INDEXES
                    ) PARTITION BY RANGE (timestamp);
                    
                    -- Add composite primary key that includes the partition key (required for partitioned tables)
                    ALTER TABLE activity_event_parent ADD PRIMARY KEY (id, timestamp);
                    
                    -- Note: Unique constraint on (tenant_id, request_id) is not added here because
                    -- PostgreSQL requires unique constraints on partitioned tables to include all
                    -- partitioning columns. The original constraint is maintained on the non-partitioned
                    -- activity_event table. If partitioning is used in the future, the constraint
                    -- would need to be modified to include timestamp: UNIQUE (tenant_id, request_id, timestamp)
                    
                    -- Recreate indexes that were excluded (only indexes that exist at this migration point)
                    CREATE INDEX IF NOT EXISTS activity_event_parent_timestamp_idx ON activity_event_parent (timestamp);
                    CREATE INDEX IF NOT EXISTS activity_event_parent_request_id_idx ON activity_event_parent (request_id);
                    CREATE INDEX IF NOT EXISTS activity_event_parent_tenant_id_idx ON activity_event_parent (tenant_id);
                    CREATE INDEX IF NOT EXISTS activity_event_parent_hash_idx ON activity_event_parent (hash);
                    CREATE INDEX IF NOT EXISTS idx_event_tenant_ts ON activity_event_parent (tenant_id, timestamp);
                END IF;
            END$$;
            """
        )


class Migration(migrations.Migration):
    dependencies = [
        ("activity_log", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(pg_indexes_and_partition, migrations.RunPython.noop),
    ]
