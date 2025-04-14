from ninja import Field, Schema


class CurrentDay(Schema):
    current_date: int = Field(0, ge=0)
