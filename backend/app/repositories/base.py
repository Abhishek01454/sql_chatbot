"""
Base repository class providing common CRUD operations.
This implements the Repository pattern for data access abstraction.
"""

from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations.

    Provides a clean abstraction layer over database operations,
    making it easy to swap databases or add caching without changing business logic.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize repository with a model class.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    async def get_by_id(
        self,
        db: AsyncSession,
        id: str,
        raise_not_found: bool = False
    ) -> Optional[ModelType]:
        """
        Get a single record by ID.

        Args:
            db: Database session
            id: Record ID
            raise_not_found: Whether to raise exception if not found

        Returns:
            Model instance or None

        Raises:
            ValueError: If raise_not_found is True and record not found
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        instance = result.scalar_one_or_none()

        if raise_not_found and instance is None:
            raise ValueError(f"{self.model.__name__} with id {id} not found")

        return instance

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get all records with optional pagination and filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field name to order by (prefix with - for descending)
            filters: Dictionary of field:value filters

        Returns:
            List of model instances
        """
        stmt = select(self.model)

        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    stmt = stmt.where(getattr(self.model, field) == value)

        # Apply ordering
        if order_by:
            if order_by.startswith("-"):
                field_name = order_by[1:]
                if hasattr(self.model, field_name):
                    stmt = stmt.order_by(getattr(self.model, field_name).desc())
            else:
                if hasattr(self.model, order_by):
                    stmt = stmt.order_by(getattr(self.model, order_by))

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        obj_in: Dict[str, Any],
        commit: bool = True
    ) -> ModelType:
        """
        Create a new record.

        Args:
            db: Database session
            obj_in: Dictionary of field values
            commit: Whether to commit immediately

        Returns:
            Created model instance
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)

        if commit:
            await db.commit()
            await db.refresh(db_obj)

        return db_obj

    async def update(
        self,
        db: AsyncSession,
        id: str,
        obj_in: Dict[str, Any],
        commit: bool = True
    ) -> Optional[ModelType]:
        """
        Update an existing record.

        Args:
            db: Database session
            id: Record ID
            obj_in: Dictionary of field values to update
            commit: Whether to commit immediately

        Returns:
            Updated model instance or None if not found
        """
        db_obj = await self.get_by_id(db, id)

        if not db_obj:
            return None

        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)

        if commit:
            await db.commit()
            await db.refresh(db_obj)

        return db_obj

    async def update_by_query(
        self,
        db: AsyncSession,
        filters: Dict[str, Any],
        values: Dict[str, Any],
        commit: bool = True
    ) -> int:
        """
        Update multiple records matching filters.

        Args:
            db: Database session
            filters: Dictionary of field:value filters
            values: Dictionary of field values to update
            commit: Whether to commit immediately

        Returns:
            Number of updated records
        """
        stmt = update(self.model)

        for field, value in filters.items():
            if hasattr(self.model, field):
                stmt = stmt.where(getattr(self.model, field) == value)

        stmt = stmt.values(**values)

        result = await db.execute(stmt)

        if commit:
            await db.commit()

        return result.rowcount

    async def delete(
        self,
        db: AsyncSession,
        id: str,
        commit: bool = True
    ) -> bool:
        """
        Delete a record by ID.

        Args:
            db: Database session
            id: Record ID
            commit: Whether to commit immediately

        Returns:
            True if deleted, False if not found
        """
        db_obj = await self.get_by_id(db, id)

        if not db_obj:
            return False

        await db.delete(db_obj)

        if commit:
            await db.commit()

        return True

    async def delete_by_query(
        self,
        db: AsyncSession,
        filters: Dict[str, Any],
        commit: bool = True
    ) -> int:
        """
        Delete multiple records matching filters.

        Args:
            db: Database session
            filters: Dictionary of field:value filters
            commit: Whether to commit immediately

        Returns:
            Number of deleted records
        """
        stmt = delete(self.model)

        for field, value in filters.items():
            if hasattr(self.model, field):
                stmt = stmt.where(getattr(self.model, field) == value)

        result = await db.execute(stmt)

        if commit:
            await db.commit()

        return result.rowcount

    async def count(
        self,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count records with optional filtering.

        Args:
            db: Database session
            filters: Dictionary of field:value filters

        Returns:
            Number of records
        """
        stmt = select(func.count()).select_from(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    stmt = stmt.where(getattr(self.model, field) == value)

        result = await db.execute(stmt)
        return result.scalar()

    async def exists(
        self,
        db: AsyncSession,
        id: str
    ) -> bool:
        """
        Check if a record exists by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            True if exists, False otherwise
        """
        stmt = select(func.count()).select_from(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        count = result.scalar()
        return count > 0

    async def get_by_field(
        self,
        db: AsyncSession,
        field: str,
        value: Any
    ) -> Optional[ModelType]:
        """
        Get a single record by a specific field.

        Args:
            db: Database session
            field: Field name
            value: Field value

        Returns:
            Model instance or None
        """
        if not hasattr(self.model, field):
            raise ValueError(f"{self.model.__name__} has no field '{field}'")

        stmt = select(self.model).where(getattr(self.model, field) == value)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_many_by_field(
        self,
        db: AsyncSession,
        field: str,
        value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records by a specific field.

        Args:
            db: Database session
            field: Field name
            value: Field value
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        if not hasattr(self.model, field):
            raise ValueError(f"{self.model.__name__} has no field '{field}'")

        stmt = select(self.model).where(
            getattr(self.model, field) == value
        ).offset(skip).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def bulk_create(
        self,
        db: AsyncSession,
        objects: List[Dict[str, Any]],
        commit: bool = True
    ) -> List[ModelType]:
        """
        Create multiple records in bulk.

        Args:
            db: Database session
            objects: List of dictionaries with field values
            commit: Whether to commit immediately

        Returns:
            List of created model instances
        """
        db_objs = [self.model(**obj) for obj in objects]
        db.add_all(db_objs)

        if commit:
            await db.commit()
            for obj in db_objs:
                await db.refresh(obj)

        return db_objs

    async def soft_delete(
        self,
        db: AsyncSession,
        id: str,
        commit: bool = True
    ) -> Optional[ModelType]:
        """
        Soft delete a record by setting is_deleted flag.
        Only works if model has is_deleted field.

        Args:
            db: Database session
            id: Record ID
            commit: Whether to commit immediately

        Returns:
            Updated model instance or None if not found
        """
        if not hasattr(self.model, 'is_deleted'):
            raise ValueError(f"{self.model.__name__} does not support soft delete")

        return await self.update(db, id, {'is_deleted': 1}, commit)

    async def restore(
        self,
        db: AsyncSession,
        id: str,
        commit: bool = True
    ) -> Optional[ModelType]:
        """
        Restore a soft-deleted record.
        Only works if model has is_deleted field.

        Args:
            db: Database session
            id: Record ID
            commit: Whether to commit immediately

        Returns:
            Updated model instance or None if not found
        """
        if not hasattr(self.model, 'is_deleted'):
            raise ValueError(f"{self.model.__name__} does not support soft delete")

        return await self.update(db, id, {'is_deleted': 0}, commit)
