from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer, ForeignKey
from blushy.db.models.base import Base


# Define the association table
item_color_association = Table('item_color_association', Base.metadata,
    Column('item_id', Integer, ForeignKey('items.id')),
    Column('color_id', Integer, ForeignKey('master_colors.id'))
)