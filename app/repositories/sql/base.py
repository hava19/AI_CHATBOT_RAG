from ..base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession

class SQLBaseRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
