import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from backend.main import app
from backend.schemas.forecast import ForcastOutputBase

client = TestClient(app)

@pytest.fixture
def mock_predictor():
    with patch('backend.api.endpoints.forecast.get_predictor_v2') as mock:
        predictor = AsyncMock()
        mock.return_value = predictor
        yield predictor

def test_forecast_endpoint_success(mock_predictor):
    # Mock the predictor's response
    mock_predictions = [
        ForcastOutputBase(
            timestamp="2024-01-01T00:00:00",
            temperature=25.5,
            humidity=60,
            condition="Sunny"
        ),
        ForcastOutputBase(
            timestamp="2024-01-01T01:00:00",
            temperature=26.0,
            humidity=58,
            condition="Sunny"
        )
    ]
    mock_predictor.predict.return_value = mock_predictions

    # Make the request
    response = client.get("/forecast/?station_id=test-station-1")

    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["temperature"] == 25.5
    assert data[0]["humidity"] == 60
    assert data[0]["condition"] == "Sunny"

    # Verify predictor was called correctly
    mock_predictor.predict.assert_called_once_with(
        station_id="test-station-1",
        predict_hours=72
    )

def test_forecast_endpoint_missing_station_id():
    # Make request without station_id
    response = client.get("/forecast/")
    
    # Assert response
    assert response.status_code == 422  # Validation error

def test_forecast_endpoint_predictor_error(mock_predictor):
    # Mock predictor to raise an exception
    mock_predictor.predict.side_effect = Exception("Prediction failed")

    # Make the request
    response = client.get("/forecast/?station_id=test-station-1")

    # Assert response
    assert response.status_code == 500  # Internal server error 