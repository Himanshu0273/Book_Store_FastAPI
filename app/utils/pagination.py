from typing import Optional, Type
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.ext.asyncio import AsyncSession

async def paginate_query(
    db: AsyncSession,
    model: Type[DeclarativeMeta],
    limit: int=10,
    after: Optional[int]=None,
    order_column="id"
):
    query = select(model).order_by(getattr(model, order_column))
    if after:
        query=query.where(getattr (model, order_column)>None)
    query=query.limit(limit+1)
    
    result = await db.execute(query)
    items = result.scalar().all()
    
    has_next = len(items)>limit
    items = items[:limit]
    next_cursor = getattr(items[-1], order_column) if has_next else None
    
    return {"data": items, "next_cursor": next_cursor}