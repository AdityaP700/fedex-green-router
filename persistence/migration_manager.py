from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import importlib
import os

class MigrationManager:
    """Manages database migrations."""
    
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations."""
        collection = self.db.migrations
        migrations = await collection.find().sort("applied_at", 1).to_list(None)
        return [m["name"] for m in migrations]
    
    async def apply_migrations(self) -> None:
        """Apply all pending migrations."""
        # Get list of applied migrations
        applied = await self.get_applied_migrations()
        
        # Get all migration files
        migration_files = sorted([
            f[:-3] for f in os.listdir(self.migrations_dir)
            if f.endswith(".py") and f != "__init__.py"
        ])
        
        # Apply pending migrations
        for migration in migration_files:
            if migration not in applied:
                # Import migration module
                module = importlib.import_module(f".{migration}", "persistence.migrations")
                
                # Apply migration
                await module.up(self.db)
                
                # Record migration
                await self.db.migrations.insert_one({
                    "name": migration,
                    "applied_at": datetime.utcnow()
                })
    
    async def rollback_migration(self, migration_name: str) -> None:
        """Rollback a specific migration."""
        # Check if migration was applied
        if migration_name not in await self.get_applied_migrations():
            raise ValueError(f"Migration {migration_name} was not applied")
        
        # Import migration module
        module = importlib.import_module(f".{migration_name}", "persistence.migrations")
        
        # Rollback migration
        await module.down(self.db)
        
        # Remove migration record
        await self.db.migrations.delete_one({"name": migration_name}) 