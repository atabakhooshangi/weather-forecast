# Component Hierarchy

```mermaid
graph TD
    A[App.vue] --> B[HomeView.vue]
    B --> C[DailyForecast.vue]
    B --> D[TemperatureGraph.vue]
    B --> E[WeatherDisplay.vue]
    B --> F[StationList.vue]

    subgraph "Main Components"
        A
        B
    end

    subgraph "Weather Components"
        C
        D
        E
    end

    subgraph "Station Components"
        F
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#dfd,stroke:#333,stroke-width:2px
    style D fill:#dfd,stroke:#333,stroke-width:2px
    style E fill:#dfd,stroke:#333,stroke-width:2px
    style F fill:#dfd,stroke:#333,stroke-width:2px
```

## Component Descriptions

### Main Components
- **App.vue**: Root component that provides the main layout and routing
- **HomeView.vue**: Main view component that orchestrates the weather display

### Weather Components
- **DailyForecast.vue**: Displays daily weather forecasts
- **TemperatureGraph.vue**: Shows temperature trends over time
- **WeatherDisplay.vue**: Displays current weather conditions

### Station Components
- **StationList.vue**: Manages the list of weather stations and station selection 