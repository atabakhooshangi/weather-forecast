from pydantic import BaseModel



class ForecastInputSchema(BaseModel):
    station_id: str


class ForcastOutputBase(BaseModel):
    temperature: str
    precipitation: str = "0"
    humidity: str = "0"
    condition: str
    timestamp: str
    type: str

class ForecastOutputSchema(BaseModel):
    data: list[ForecastInputSchema]
