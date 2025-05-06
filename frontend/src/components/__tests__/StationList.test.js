import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import StationList from '../StationList.vue'
import { createTestingPinia } from '@pinia/testing'

describe('StationList', () => {
  let wrapper

  const mockStations = [
    { id: 'station-1', name: 'Station 1', location: 'Location 1' },
    { id: 'station-2', name: 'Station 2', location: 'Location 2' }
  ]

  beforeEach(() => {
    wrapper = mount(StationList, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn
        })]
      },
      props: {
        stations: mockStations,
        selectedStation: 'station-1',
        isLoading: false,
        error: ''
      }
    })
  })

  it('renders properly', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('displays all stations', () => {
    const stationItems = wrapper.findAll('.station-item')
    expect(stationItems).toHaveLength(mockStations.length)
  })

  it('highlights selected station', () => {
    const selectedItem = wrapper.find('.station-item.selected')
    expect(selectedItem.text()).toContain('Station 1')
  })

  it('emits selection event when station is clicked', async () => {
    const secondStation = wrapper.findAll('.station-item')[1]
    await secondStation.trigger('click')
    
    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')[0]).toEqual(['station-2'])
  })

  it('displays loading state', async () => {
    await wrapper.setProps({ isLoading: true })
    expect(wrapper.find('.loading-spinner').exists()).toBe(true)
  })

  it('shows error message when stations fail to load', async () => {
    const errorMessage = 'Failed to load stations'
    await wrapper.setProps({ error: errorMessage })
    expect(wrapper.find('.error-message').text()).toBe(errorMessage)
  })

  it('filters stations based on search input', async () => {
    const searchInput = wrapper.find('.search-input')
    await searchInput.setValue('Station 2')
    
    const visibleStations = wrapper.findAll('.station-item')
    expect(visibleStations).toHaveLength(1)
    expect(visibleStations[0].text()).toContain('Station 2')
  })
}) 