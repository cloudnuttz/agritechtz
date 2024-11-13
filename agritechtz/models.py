"""Relational database/Object mapping module"""

from decimal import Decimal
from datetime import date
from typing import Dict, List

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

Base = declarative_base()


class CropPrice(Base):
    """Mapper class for the crop prices stored in the database."""

    __tablename__ = "cn_crop_prices"

    source_url: Mapped[str] = mapped_column(primary_key=True)
    ts: Mapped[date] = mapped_column(primary_key=True)
    region: Mapped[str] = mapped_column(primary_key=True)
    district: Mapped[str] = mapped_column(primary_key=True)

    crop_prices: Mapped[List[Dict[str, str | Decimal | None]]] = mapped_column(
        JSON, nullable=False
    )

    def __repr__(self):
        return (
            f"<CropPrice(id={self.source_url}, "
            f"ts={self.ts}, region={self.region}, "
            f"district={self.district}), crop_prices={self.crop_prices}>"
        )
