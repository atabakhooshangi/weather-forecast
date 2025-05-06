
from fastapi_cache.decorator import cache

from fastapi import APIRouter, Depends
from backend.schemas.forecast import ForecastInputSchema, ForcastOutputBase, ForecastOutputSchema
from backend.services.predict import AsyncWeatherPredictor
from backend.api.dependencies.predict import get_predictor_v1, get_predictor_v2

router = APIRouter()

@router.get("/", response_model=list[ForcastOutputBase])
@cache(expire=1800)
async def forecast_weather(
    params: ForecastInputSchema=Depends(),
    predictor: AsyncWeatherPredictor = Depends(get_predictor_v2),
) -> list[ForcastOutputBase]:
    predictions = await predictor.predict(station_id=params.station_id, predict_hours=72)
    return predictions
