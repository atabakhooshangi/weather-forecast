import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import TemperatureGraph from '../TemperatureGraph.vue'
import { createTestingPinia } from '@pinia/testing'

// Mock vue-chartjs
vi.mock('vue-chartjs', () => ({
  Line: {
    name: 'Line',
    render: () => null
  }
}))

// Mock chart.js
vi.mock('chart.js', () => ({
  Chart: {
    register: vi.fn()
  },
  CategoryScale: {},
  LinearScale: {},
  PointElement: {},
  LineElement: {},
  Title: {},
  Tooltip: {},
  Legend: {},
  TimeScale: {},
  _adapters: {
    _date: {
      formats: () => ({
        datetime: 'MMM d, yyyy, h:mm:ss a',
        millisecond: 'h:mm:ss.SSS a',
        second: 'h:mm:ss a',
        minute: 'h:mm a',
        hour: 'h a',
        day: 'MMM d',
        week: 'PP',
        month: 'MMM yyyy',
        quarter: 'qqq - yyyy',
        year: 'yyyy'
      }),
      override: vi.fn()
    }
  }
}))

describe('TemperatureGraph', () => {
  let wrapper

  const mockForecasts = [
    { timestamp: '2024-01-01T00:00:00', temperature: '20' },
    { timestamp: '2024-01-01T01:00:00', temperature: '22' }
  ]

  beforeEach(() => {
    wrapper = mount(TemperatureGraph, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn
        })]
      },
      props: {
        forecasts: mockForecasts,
        timeRange: '24h'
      }
    })
  })

  it('renders properly', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('updates when forecasts change', async () => {
    const newForecasts = [
      { timestamp: '2024-01-01T02:00:00', temperature: '24' },
      { timestamp: '2024-01-01T03:00:00', temperature: '25' }
    ]
    await wrapper.setProps({ forecasts: newForecasts })
    expect(wrapper.props('forecasts')).toEqual(newForecasts)
  })

  it('handles time range changes', async () => {
    const newTimeRange = '7d'
    await wrapper.setProps({ timeRange: newTimeRange })
    expect(wrapper.props('timeRange')).toBe(newTimeRange)
  })

  it('displays no data message when forecasts are empty', async () => {
    await wrapper.setProps({ forecasts: [] })
    expect(wrapper.find('.no-data-message').exists()).toBe(true)
  })
}) 