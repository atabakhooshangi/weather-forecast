const stations = [
  { id: 12756, name: 'Szecseny', latitude: 48.1167, longitude: 19.5167 },
  { id: 12840, name: 'Budapest Met Center', latitude: 47.5167, longitude: 19.0333 },
  { id: 12882, name: 'Debrecen', latitude: 47.4833, longitude: 21.6 },
  { id: 12846, name: 'Agard', latitude: 47.1833, longitude: 18.6167 },
  { id: 12942, name: 'Pecs / Pogany', latitude: 46.1, longitude: 18.2333 },
  { id: 12822, name: 'Gyor', latitude: 47.7167, longitude: 17.6833 },
  { id: 12825, name: 'Papa', latitude: 47.2, longitude: 17.5 },
  { id: 12982, name: 'Szeged', latitude: 46.25, longitude: 20.1 },
  { id: 12892, name: 'Nyiregyhaza / Napkor', latitude: 47.9667, longitude: 21.9833 },
  { id: 12970, name: 'Kecskemet', latitude: 46.9167, longitude: 19.75 },
  { id: 12812, name: 'Szombathely', latitude: 47.2667, longitude: 16.6333 },
  { id: 12772, name: 'Miskolc', latitude: 48.0833, longitude: 20.7667 },
  { id: 12930, name: 'Kaposvar', latitude: 46.3833, longitude: 17.8333 },
  { id: 12839, name: 'Budapest / Ferihegy', latitude: 47.4333, longitude: 19.2667 },
  { id: 12805, name: 'Sopron', latitude: 47.6833, longitude: 16.6 },
  { id: 12836, name: 'Tata', latitude: 47.65, longitude: 18.3167 },
  { id: 12866, name: 'Poroszlo', latitude: 47.65, longitude: 20.6333 },
  { id: 12915, name: 'Zalaegerszeg / Andrashida', latitude: 46.8667, longitude: 16.8 },
  { id: 12992, name: 'Bekescsaba', latitude: 46.6833, longitude: 21.1667 },
  { id: 12870, name: 'Eger', latitude: 47.9, longitude: 20.3833 },
  { id: 12925, name: 'Nagykanizsa', latitude: 46.45, longitude: 16.9667 },
  { id: 12935, name: 'Siofok', latitude: 46.9167, longitude: 18.05 },
  { id: 12950, name: 'Paks', latitude: 46.5833, longitude: 18.85 }
]

export const getStations = () => {
  // Remove duplicates based on station ID
  return [...new Map(stations.map(station => [station.id, station])).values()]
} 