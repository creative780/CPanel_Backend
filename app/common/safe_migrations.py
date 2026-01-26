"""
Safe Migration Operations

This module provides safe versions of Django migration operations that check
for existence before performing database operations, preventing errors like:
- "Duplicate column name"
- "Can't DROP COLUMN; check that it exists"
- "Key column doesn't exist in table"
- Similar errors for tables, indexes, and constraints

All classes support MySQL, SQLite, and PostgreSQL.
"""

from django.core.exceptions import FieldDoesNotExist
from django.db import migrations


class SafeAddField(migrations.AddField):
    """AddField that safely handles the case where the field already exists in the database."""
    
    def state_forwards(self, app_label, state):
        """Override to safely handle missing model in state."""
        try:
            # Check if model exists in state
            model_key = (app_label, self.model_name.lower())
            if model_key not in state.models:
                # Model doesn't exist in state, skip state update
                return
            super().state_forwards(app_label, state)
        except KeyError:
            # Model or field doesn't exist in state, skip
            pass
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Override to check if field exists before adding."""
        # First check if model exists in to_state
        model_key = (app_label, self.model_name.lower())
        if model_key not in to_state.models:
            # Model doesn't exist, skip database operation
            return
        
        vendor = schema_editor.connection.vendor
        cursor = schema_editor.connection.cursor()
        
        # Get table name from model - try lowercase first, then original case
        try:
            model = to_state.apps.get_model(app_label, self.model_name.lower())
        except LookupError:
            try:
                model = to_state.apps.get_model(app_label, self.model_name)
            except LookupError:
                # Model not in state, skip
                return
        table_name = model._meta.db_table
        
        # Get the actual database column name
        # For ForeignKey fields, Django uses field_name + '_id'
        column_name = self.name
        if hasattr(self.field, 'related_model') and self.field.related_model:
            # This is a ForeignKey, check for the _id column
            column_name = f"{self.name}_id"
        
        # Check if column already exists
        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
                """,
                [table_name, column_name],
            )
            exists = cursor.fetchone()[0] > 0
        elif vendor == "sqlite":
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = [row[1] for row in cursor.fetchall()]
            exists = column_name in columns
        else:  # PostgreSQL
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
                """,
                [table_name, column_name],
            )
            exists = cursor.fetchone()[0] > 0
        
        # If column exists, skip the database operation
        if exists:
            return
        
        # Column doesn't exist, proceed with adding it
        try:
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        except Exception as e:
            # Catch duplicate column errors
            error_str = str(e)
            if "Duplicate column" in error_str or "duplicate" in error_str.lower() or "1060" in error_str:
                # Column already exists, skip
                return
            # Re-raise other exceptions
            raise


class SafeRemoveField(migrations.RemoveField):
    """RemoveField that safely handles the case where the field doesn't exist."""
    
    def state_forwards(self, app_label, state):
        try:
            super().state_forwards(app_label, state)
        except KeyError:
            pass
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Override to check if field exists before removing."""
        model_key = (app_label, self.model_name.lower())
        if model_key not in to_state.models:
            return
        
        vendor = schema_editor.connection.vendor
        cursor = schema_editor.connection.cursor()
        
        model = to_state.apps.get_model(app_label, self.model_name)
        table_name = model._meta.db_table
        
        # Get the actual database column name
        # For ForeignKey fields, Django uses field_name + '_id'
        try:
            from_state_model = from_state.apps.get_model(app_label, self.model_name)
            field = from_state_model._meta.get_field(self.name)
            if hasattr(field, 'get_attname'):
                column_name = field.get_attname()
            else:
                column_name = self.name
        except (LookupError, KeyError, AttributeError, FieldDoesNotExist):
            # Field doesn't exist in state, skip
            return
        
        # Check if column exists
        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
                """,
                [table_name, column_name],
            )
            exists = cursor.fetchone()[0] > 0
        elif vendor == "sqlite":
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = [row[1] for row in cursor.fetchall()]
            exists = column_name in columns
        else:  # PostgreSQL
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
                """,
                [table_name, column_name],
            )
            exists = cursor.fetchone()[0] > 0
        
        # If column doesn't exist, skip the operation
        if not exists:
            return
        
        try:
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        except Exception as e:
            error_str = str(e)
            if "doesn't exist" in error_str.lower() or "no such column" in error_str.lower() or "1091" in error_str or "Can't DROP" in error_str:
                return
            raise


class SafeAlterField(migrations.AlterField):
    """AlterField that safely handles the case where the model or field doesn't exist in state."""
    
    def state_forwards(self, app_label, state):
        """Override to safely handle missing model or field in state."""
        # Check if model exists first
        model_key = (app_label, self.model_name.lower())
        if model_key not in state.models:
            # Model doesn't exist, skip
            return
        
        # Check if field exists in the model
        try:
            model_state = state.models[model_key]
            if self.name not in model_state.fields:
                # Field doesn't exist, skip
                return
        except (KeyError, AttributeError):
            # Can't access model state, skip
            return
        
        # Catch all exceptions - if model doesn't exist or anything goes wrong, skip silently
        try:
            super().state_forwards(app_label, state)
        except Exception:
            # Model, field, or state doesn't exist - skip this operation
            pass
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Override to safely handle missing model in database operations."""
        # Check if model exists in to_state
        model_key = (app_label, self.model_name.lower())
        if model_key not in to_state.models:
            # Model doesn't exist, skip
            return
        
        # Check if field exists in to_state
        try:
            to_model = to_state.apps.get_model(app_label, self.model_name)
            to_model._meta.get_field(self.name)
        except (LookupError, KeyError, AttributeError, FieldDoesNotExist, Exception):
            # Model or field doesn't exist, skip
            return
        
        # Check if field exists in from_state
        try:
            if model_key in from_state.models:
                from_model = from_state.apps.get_model(app_label, self.model_name)
                from_field = from_model._meta.get_field(self.name)
        except (LookupError, KeyError, AttributeError, FieldDoesNotExist, Exception):
            # Field doesn't exist in from_state, skip
            return
        
        # Handle data truncation when changing from TextField to CharField with max_length
        # or reducing max_length of CharField
        try:
            from_field_type = type(from_field).__name__
            to_field_type = type(self.field).__name__
            
            # Check if we're changing from TextField to CharField or reducing max_length
            if (from_field_type == 'TextField' and to_field_type == 'CharField' and 
                hasattr(self.field, 'max_length') and self.field.max_length):
                # Need to truncate data before altering field
                model = to_state.apps.get_model(app_label, self.model_name)
                table_name = model._meta.db_table
                column_name = self.name
                
                vendor = schema_editor.connection.vendor
                cursor = schema_editor.connection.cursor()
                
                # Truncate data to fit new max_length
                max_length = self.field.max_length
                if vendor == "mysql":
                    cursor.execute(
                        f"UPDATE `{table_name}` SET `{column_name}` = LEFT(`{column_name}`, %s) WHERE CHAR_LENGTH(`{column_name}`) > %s",
                        [max_length, max_length]
                    )
                elif vendor == "sqlite":
                    cursor.execute(
                        f'UPDATE "{table_name}" SET "{column_name}" = substr("{column_name}", 1, ?) WHERE length("{column_name}") > ?',
                        [max_length, max_length]
                    )
                else:  # PostgreSQL
                    cursor.execute(
                        f'UPDATE "{table_name}" SET "{column_name}" = LEFT("{column_name}", %s) WHERE LENGTH("{column_name}") > %s',
                        [max_length, max_length]
                    )
            elif (from_field_type == 'CharField' and to_field_type == 'CharField' and
                  hasattr(from_field, 'max_length') and hasattr(self.field, 'max_length') and
                  from_field.max_length and self.field.max_length and
                  self.field.max_length < from_field.max_length):
                # Reducing max_length, truncate data
                model = to_state.apps.get_model(app_label, self.model_name)
                table_name = model._meta.db_table
                column_name = self.name
                
                vendor = schema_editor.connection.vendor
                cursor = schema_editor.connection.cursor()
                
                max_length = self.field.max_length
                if vendor == "mysql":
                    cursor.execute(
                        f"UPDATE `{table_name}` SET `{column_name}` = LEFT(`{column_name}`, %s) WHERE CHAR_LENGTH(`{column_name}`) > %s",
                        [max_length, max_length]
                    )
                elif vendor == "sqlite":
                    cursor.execute(
                        f'UPDATE "{table_name}" SET "{column_name}" = substr("{column_name}", 1, ?) WHERE length("{column_name}") > ?',
                        [max_length, max_length]
                    )
                else:  # PostgreSQL
                    cursor.execute(
                        f'UPDATE "{table_name}" SET "{column_name}" = LEFT("{column_name}", %s) WHERE LENGTH("{column_name}") > %s',
                        [max_length, max_length]
                    )
        except Exception:
            # If truncation fails, continue anyway - the alter might still work
            pass
        
        try:
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        except Exception as e:
            # Catch any errors related to missing models or fields, or data truncation
            error_str = str(e)
            if ("doesn't have" in error_str.lower() or "LookupError" in error_str or "KeyError" in error_str or
                "data truncated" in error_str.lower() or "1265" in error_str):
                # Model or field doesn't exist, or data truncation error, skip
                return
            # Re-raise other exceptions
            raise


class SafeCreateModel(migrations.CreateModel):
    """CreateModel that safely handles the case where the table already exists."""
    
    def state_forwards(self, app_label, state):
        """Always update state, even if table exists in database."""
        # Always call parent to update migration state
        # This ensures the model is registered in the state even if table exists
        super().state_forwards(app_label, state)
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Override to check if table exists before creating."""
        # Use lowercase model name for consistency
        model_name_lower = self.name.lower()
        try:
            model = to_state.apps.get_model(app_label, model_name_lower)
        except LookupError:
            # Try with original case
            model = to_state.apps.get_model(app_label, self.name)
        table_name = model._meta.db_table
        
        vendor = schema_editor.connection.vendor
        cursor = schema_editor.connection.cursor()
        
        # Check if table already exists
        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
                """,
                [table_name],
            )
            exists = cursor.fetchone()[0] > 0
        elif vendor == "sqlite":
            # SQLite doesn't support parameterized queries for table names
            cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
            )
            exists = cursor.fetchone() is not None
        else:  # PostgreSQL
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = %s
                """,
                [table_name],
            )
            exists = cursor.fetchone()[0] > 0
        
        # If table exists, skip the database operation
        if exists:
            return
        
        # Table doesn't exist, proceed with creating it
        try:
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        except Exception as e:
            # Catch duplicate table errors
            error_str = str(e)
            if "already exists" in error_str.lower() or "1050" in error_str:
                # Table already exists, skip
                return
            # Re-raise other exceptions
            raise


class SafeDeleteModel(migrations.DeleteModel):
    """DeleteModel that safely handles the case where the table doesn't exist."""
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Override to check if table exists before deleting."""
        model = from_state.apps.get_model(app_label, self.name)
        table_name = model._meta.db_table
        
        vendor = schema_editor.connection.vendor
        cursor = schema_editor.connection.cursor()
        
        # Check if table exists
        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
                """,
                [table_name],
            )
            exists = cursor.fetchone()[0] > 0
        elif vendor == "sqlite":
            cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
            )
            exists = cursor.fetchone() is not None
        else:  # PostgreSQL
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = %s
                """,
                [table_name],
            )
            exists = cursor.fetchone()[0] > 0
        
        # If table doesn't exist, skip the operation
        if not exists:
            return
        
        try:
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        except Exception as e:
            error_str = str(e)
            if "doesn't exist" in error_str.lower() or "no such table" in error_str.lower():
                return
            raise


class SafeAddIndex(migrations.AddIndex):
    """AddIndex that safely handles the case where the index already exists."""
    
    def state_forwards(self, app_label, state):
        """Override to safely handle missing model in state."""
        model_key = (app_label, self.model_name.lower())
        if model_key not in state.models:
            return
        try:
            super().state_forwards(app_label, state)
        except (ValueError, KeyError):
            pass
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Override to check if index exists and all columns exist before adding."""
        model_key = (app_label, self.model_name.lower())
        if model_key not in to_state.models:
            return
        
        vendor = schema_editor.connection.vendor
        cursor = schema_editor.connection.cursor()
        
        model = to_state.apps.get_model(app_label, self.model_name)
        table_name = model._meta.db_table
        index_name = self.index.name
        
        # Check if all columns in the index exist
        for field_name in self.index.fields:
            try:
                field = model._meta.get_field(field_name)
                # For ForeignKey, check the _id column
                if hasattr(field, 'get_attname'):
                    column_name = field.get_attname()
                else:
                    column_name = field_name
                
                if vendor == "mysql":
                    cursor.execute(
                        """
                        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
                        """,
                        [table_name, column_name],
                    )
                    column_exists = cursor.fetchone()[0] > 0
                elif vendor == "sqlite":
                    cursor.execute(f'PRAGMA table_info("{table_name}")')
                    columns = [row[1] for row in cursor.fetchall()]
                    column_exists = column_name in columns
                else:  # PostgreSQL
                    cursor.execute(
                        """
                        SELECT COUNT(*) FROM information_schema.columns
                        WHERE table_name = %s AND column_name = %s
                        """,
                        [table_name, column_name],
                    )
                    column_exists = cursor.fetchone()[0] > 0
                
                if not column_exists:
                    # Column doesn't exist, skip index creation
                    return
            except (LookupError, AttributeError, FieldDoesNotExist):
                # Field doesn't exist, skip index creation
                return
        
        # Check if index already exists
        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND INDEX_NAME = %s
                """,
                [table_name, index_name],
            )
            exists = cursor.fetchone()[0] > 0
        elif vendor == "sqlite":
            cursor.execute(f'PRAGMA index_list("{table_name}")')
            indexes = [row[1] for row in cursor.fetchall()]
            exists = index_name in indexes
        else:  # PostgreSQL
            cursor.execute(
                """
                SELECT COUNT(*) FROM pg_indexes
                WHERE tablename = %s AND indexname = %s
                """,
                [table_name, index_name],
            )
            exists = cursor.fetchone()[0] > 0
        
        if exists:
            return
        
        try:
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        except Exception as e:
            error_str = str(e)
            if "Duplicate key" in error_str or "duplicate" in error_str.lower() or "1061" in error_str or "1072" in error_str:
                return
            raise


class SafeRemoveIndex(migrations.RemoveIndex):
    """RemoveIndex that safely handles the case where the index doesn't exist."""
    
    def state_forwards(self, app_label, state):
        model_key = (app_label, self.model_name.lower())
        if model_key not in state.models:
            return
        try:
            super().state_forwards(app_label, state)
        except (ValueError, KeyError):
            pass
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model_key = (app_label, self.model_name.lower())
        if model_key not in to_state.models:
            return
        
        # Check if index exists in migration state
        try:
            model_state = from_state.models[model_key]
            # Try to get the index from the model state
            try:
                model_state.get_index_by_name(self.name)
            except ValueError:
                # Index doesn't exist in migration state, skip
                return
        except (KeyError, AttributeError):
            # Model doesn't exist in from_state, skip
            return
        
        vendor = schema_editor.connection.vendor
        cursor = schema_editor.connection.cursor()
        model = to_state.apps.get_model(app_label, self.model_name)
        table_name = model._meta.db_table
        index_name = self.name
        
        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND INDEX_NAME = %s
                """,
                [table_name, index_name],
            )
            exists = cursor.fetchone()[0] > 0
        elif vendor == "sqlite":
            cursor.execute(f'PRAGMA index_list("{table_name}")')
            indexes = [row[1] for row in cursor.fetchall()]
            exists = index_name in indexes
        else:  # PostgreSQL
            cursor.execute(
                """
                SELECT COUNT(*) FROM pg_indexes
                WHERE tablename = %s AND indexname = %s
                """,
                [table_name, index_name],
            )
            exists = cursor.fetchone()[0] > 0
        
        if not exists:
            return
        
        try:
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        except Exception as e:
            error_str = str(e)
            if "doesn't exist" in error_str.lower() or "no such index" in error_str.lower() or "no index named" in error_str.lower():
                return
            raise


class SafeRenameIndex(migrations.RenameIndex):
    """RenameIndex that safely handles the case where the old index doesn't exist."""
    
    def state_forwards(self, app_label, state):
        model_key = (app_label, self.model_name_lower)
        if model_key not in state.models:
            return
        try:
            super().state_forwards(app_label, state)
        except (ValueError, KeyError):
            pass
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model_key = (app_label, self.model_name.lower())
        if model_key not in to_state.models:
            return
        
        # Check if old index exists in migration state
        try:
            model_state = from_state.models[model_key]
            # Try to get the old index from the model state
            try:
                model_state.get_index_by_name(self.old_name)
            except ValueError:
                # Old index doesn't exist in migration state, skip
                return
        except (KeyError, AttributeError):
            # Model doesn't exist in from_state, skip
            return
        
        vendor = schema_editor.connection.vendor
        cursor = schema_editor.connection.cursor()
        model = to_state.apps.get_model(app_label, self.model_name)
        table_name = model._meta.db_table
        
        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND INDEX_NAME = %s
                """,
                [table_name, self.old_name],
            )
            exists = cursor.fetchone()[0] > 0
        elif vendor == "sqlite":
            cursor.execute(f'PRAGMA index_list("{table_name}")')
            indexes = [row[1] for row in cursor.fetchall()]
            exists = self.old_name in indexes
        else:  # PostgreSQL
            cursor.execute(
                """
                SELECT COUNT(*) FROM pg_indexes
                WHERE tablename = %s AND indexname = %s
                """,
                [table_name, self.old_name],
            )
            exists = cursor.fetchone()[0] > 0
        
        if not exists:
            return
        
        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND INDEX_NAME = %s
                """,
                [table_name, self.new_name],
            )
            new_exists = cursor.fetchone()[0] > 0
        elif vendor == "sqlite":
            new_exists = self.new_name in indexes
        else:  # PostgreSQL
            cursor.execute(
                """
                SELECT COUNT(*) FROM pg_indexes
                WHERE tablename = %s AND indexname = %s
                """,
                [table_name, self.new_name],
            )
            new_exists = cursor.fetchone()[0] > 0
        
        if new_exists:
            return
        
        try:
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        except Exception as e:
            error_str = str(e)
            if "doesn't exist" in error_str.lower() or "1176" in error_str or "Key" in error_str or "no index named" in error_str.lower():
                return
            raise


class SafeRenameField(migrations.RenameField):
    """RenameField that safely handles the case where the model or field doesn't exist in state."""
    
    def state_forwards(self, app_label, state):
        """Override to safely handle missing model in state."""
        # Check if model exists in state
        model_key = (app_label, self.model_name_lower)
        if model_key not in state.models:
            # Model doesn't exist in state, skip
            return
        try:
            super().state_forwards(app_label, state)
        except (KeyError, AttributeError):
            # Field doesn't exist in state, skip
            pass
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Override to safely handle already-renamed field."""
        model_key = (app_label, self.model_name.lower())
        if model_key not in from_state.models:
            return
        
        # Get table name and check actual database columns
        try:
            model = to_state.apps.get_model(app_label, self.model_name)
            table_name = model._meta.db_table
        except (LookupError, KeyError):
            return
        
        vendor = schema_editor.connection.vendor
        cursor = schema_editor.connection.cursor()
        
        # Get the actual database column names
        # For ForeignKey fields, Django uses field_name + '_id'
        old_column_name = self.old_name
        new_column_name = self.new_name
        
        # Check if we need to add _id suffix for ForeignKey fields
        try:
            from_model = from_state.apps.get_model(app_label, self.model_name)
            old_field = from_model._meta.get_field(self.old_name)
            if hasattr(old_field, 'get_attname'):
                old_column_name = old_field.get_attname()
        except (LookupError, KeyError, AttributeError, FieldDoesNotExist):
            pass
        
        try:
            to_model = to_state.apps.get_model(app_label, self.model_name)
            new_field = to_model._meta.get_field(self.new_name)
            if hasattr(new_field, 'get_attname'):
                new_column_name = new_field.get_attname()
        except (LookupError, KeyError, AttributeError, FieldDoesNotExist):
            pass
        
        # Check if columns exist in database
        old_exists = False
        new_exists = False
        
        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
                """,
                [table_name, old_column_name],
            )
            old_exists = cursor.fetchone()[0] > 0
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
                """,
                [table_name, new_column_name],
            )
            new_exists = cursor.fetchone()[0] > 0
        elif vendor == "sqlite":
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = {row[1]: row for row in cursor.fetchall()}
            old_exists = old_column_name in columns
            new_exists = new_column_name in columns
        else:  # PostgreSQL
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
                """,
                [table_name, old_column_name],
            )
            old_exists = cursor.fetchone()[0] > 0
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
                """,
                [table_name, new_column_name],
            )
            new_exists = cursor.fetchone()[0] > 0
        
        # If old column doesn't exist but new one does, already renamed, skip
        if not old_exists and new_exists:
            return
        
        # If old column doesn't exist and new one doesn't exist, skip
        if not old_exists and not new_exists:
            return
        
        # If old column exists and new column exists, might be a conflict, skip to be safe
        if old_exists and new_exists:
            return
        
        # Only proceed if old column exists and new column doesn't exist
        try:
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        except Exception as e:
            error_str = str(e)
            if ("doesn't exist" in error_str.lower() or "no such column" in error_str.lower() or 
                "unknown column" in error_str.lower() or "1054" in error_str):
                return
            raise


class SafeAlterUniqueTogether(migrations.AlterUniqueTogether):
    """AlterUniqueTogether that safely handles missing models or fields."""
    
    def state_forwards(self, app_label, state):
        model_key = (app_label, self.model_name.lower())
        if model_key not in state.models:
            return
        try:
            super().state_forwards(app_label, state)
        except (KeyError, AttributeError):
            pass
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model_key = (app_label, self.model_name.lower())
        if model_key not in to_state.models:
            return
        try:
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        except Exception as e:
            error_str = str(e)
            if "doesn't exist" in error_str.lower() or "doesn't have" in error_str.lower():
                return
            raise


class SafeAlterIndexTogether(migrations.AlterIndexTogether):
    """AlterIndexTogether that safely handles missing models or fields."""
    
    def state_forwards(self, app_label, state):
        model_key = (app_label, self.model_name.lower())
        if model_key not in state.models:
            return
        try:
            super().state_forwards(app_label, state)
        except (KeyError, AttributeError):
            pass
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model_key = (app_label, self.model_name.lower())
        if model_key not in to_state.models:
            return
        try:
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        except Exception as e:
            error_str = str(e)
            if "doesn't exist" in error_str.lower() or "doesn't have" in error_str.lower():
                return
            raise

