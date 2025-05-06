from dataclasses import dataclass
from typing import ClassVar, Dict

@dataclass
class Station:
    id: str
    name: str
    latitude: float
    longitude: float

class StationLookup:
    # build a class‐level dict mapping IDs → Station instances
    _stations: ClassVar[Dict[str, Station]] = {
        "12756": Station("12756", "Szecseny",48.1167, 19.5167),
        "12840": Station("12840", "Budapest Met Center", 47.5167, 19.0333),
        "12882": Station("12882", "Debrecen",              47.4833, 21.6),
        "12846": Station("12846", "Agard",                 47.1833, 18.6167),
        "12942": Station("12942", "Pecs / Pogany",         46.1,    18.2333),
        "12822": Station("12822", "Gyor",                  47.7167, 17.6833),
        "12982": Station("12982", "Szeged",                46.25,   20.1),
        "12892": Station("12892", "Nyiregyhaza / Napkor",  47.9667, 21.9833),
        "12970": Station("12970", "Kecskemet",             46.9167, 19.75),
        "12812": Station("12812", "Szombathely",           47.2667, 16.6333),
        "12772": Station("12772", "Miskolc",               48.0833, 20.7667),
        "LHSA0": Station("LHSA0", "Azentkilyszabadja / Szentkirályszabadja", 47.0667, 17.9833),
        "12930": Station("12930", "Kaposvar",              46.3833, 17.8333),
        "12839": Station("12839", "Budapest / Ferihegy",   47.4333, 19.2667),
        "12805": Station("12805", "Sopron",                47.6833, 16.6),
        "12836": Station("12836", "Tata",                  47.65,   18.3167),
        "12915": Station("12915", "Zalaegerszeg / Andrashida", 46.8667, 16.8),
        "12992": Station("12992", "Bekescsaba",            46.6833, 21.1667),
        "12870": Station("12870", "Eger",                  47.9,    20.3833),
        "12925": Station("12925", "Nagykanizsa",           46.45,   16.9667),
        "12847": Station("12847", "Tat / Mogyorósbánya",   47.75,   18.6),
        "12935": Station("12935", "Siofok",                46.9167, 18.05),
    }

    @classmethod
    def get_station(cls, id: str) -> Station:
        """Return the Station object for the given ID, or raise KeyError."""
        try:
            return cls._stations[id]
        except KeyError:
            raise KeyError(f"No station found with id={id!r}") from None

    @classmethod
    def get_station_dict(cls, id: str) -> dict:
        """Return the station data as a dict."""
        station = cls.get_station(id)
        return station.__dict__.copy()
