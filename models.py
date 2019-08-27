from database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.types import DateTime

class Items(Base):
    """
    Items table
    """
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    quantity = Column(Integer)
    description = Column(String(256))
    date_added = Column(DateTime())

    def __str__(self):
        """Return basic HTML string that can be rendered for this object."""
        ret_fmt = "Item for sale: {}</br>"
        ret_fmt = ret_fmt + "&emsp; Description: {}</br>"
        ret_fmt = ret_fmt + "&emsp; Quantity available: {}</br>"
        ret_fmt = ret_fmt + "&emsp; Date listed: {}</br></br>"
        return ret_fmt.format(self.name, self.description, self.quantity,
                              self.date_added)
