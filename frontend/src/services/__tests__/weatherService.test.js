import { describe, it, expect, beforeEach, vi } from 'vitest'
import { getWeatherForecast, getStations } from '../weatherService'
import axios from 'axios'

vi.mock('axios')

describe('Weather Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getWeatherForecast', () => {
    const mockStationId = 'test-station-1'
    const mockResponse = {
      temperature: 25,
      humidity: 60,
      condition: 'Sunny'
    }

    it('fetches weather forecast successfully', async () => {
      axios.get.mockResolvedValueOnce({ data: mockResponse })

      const result = await getWeatherForecast(mockStationId)
      
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining(`/forecast/?station_id=${mockStationId}`)
      )
      expect(result).toEqual(mockResponse)
    })

    it('handles API errors', async () => {
      const errorMessage = 'Network Error'
      axios.get.mockRejectedValueOnce(new Error(errorMessage))

      await expect(getWeatherForecast(mockStationId)).rejects.toThrow(errorMessage)
    })
  })

  describe('getStations', () => {
    const mockStations = [
      { id: 'station-1', name: 'Station 1' },
      { id: 'station-2', name: 'Station 2' }
    ]

    it('fetches stations successfully', async () => {
      axios.get.mockResolvedValueOnce({ data: mockStations })

      const result = await getStations()
      
      expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/stations'))
      expect(result).toEqual(mockStations)
    })

    it('handles API errors', async () => {
      const errorMessage = 'Failed to fetch stations'
      axios.get.mockRejectedValueOnce(new Error(errorMessage))

      await expect(getStations()).rejects.toThrow(errorMessage)
    })
  })
}) 