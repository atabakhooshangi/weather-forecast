import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import WeatherDisplay from '../WeatherDisplay.vue'
import { createTestingPinia } from '@pinia/testing'
import { getWeatherForecast } from '../../services/weatherService'

vi.mock('../../services/weatherService', () => ({
  getWeatherForecast: vi.fn()
}))

describe('WeatherDisplay', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    wrapper = mount(WeatherDisplay, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn
        })]
      },
      props: {
        stationId: 'test-station-1'
      }
    })
  })

  it('renders properly', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('displays weather data when loaded', async () => {
    const mockWeatherData = {
      temperature: 25,
      humidity: 60,
      condition: 'Sunny'
    }
    getWeatherForecast.mockResolvedValueOnce(mockWeatherData)

    await wrapper.vm.fetchWeatherData()

    expect(wrapper.find('.temperature').text()).toContain('25°C')
    expect(wrapper.find('.humidity').text()).toContain('60%')
    expect(wrapper.find('.condition').text()).toBe('Sunny')
  })

  it('shows error message when API call fails', async () => {
    const errorMessage = 'Failed to fetch weather data'
    getWeatherForecast.mockRejectedValueOnce(new Error(errorMessage))

    await wrapper.vm.fetchWeatherData()

    expect(wrapper.find('.error-message').text()).toBe(errorMessage)
  })

  it('calls API with correct station ID', async () => {
    const mockWeatherData = {
      temperature: 25,
      humidity: 60,
      condition: 'Sunny'
    }
    getWeatherForecast.mockResolvedValueOnce(mockWeatherData)

    await wrapper.vm.fetchWeatherData()

    expect(getWeatherForecast).toHaveBeenCalledWith('test-station-1')
  })
}) 