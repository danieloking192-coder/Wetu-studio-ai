from dataclasses import dataclass, field

@dataclass
class Location:
    location_id: str
    name: str
    city: str = ""
    country: str = ""
    description: str = ""
    architecture: str = ""
    environment: str = ""
    landmarks: list[str] = field(default_factory=list)

class LocationEngine:
    def create(self, location_id: str, name: str, city: str = "", country: str = "", description: str = "") -> Location:
        if not location_id.strip() or not name.strip():
            raise ValueError("location_id and name are required")
        return Location(location_id, name, city, country, description)

    def set_design(self, location: Location, architecture: str = "", environment: str = "") -> None:
        location.architecture = architecture
        location.environment = environment

    def add_landmark(self, location: Location, landmark: str) -> None:
        if not landmark.strip():
            raise ValueError("landmark is required")
        if landmark not in location.landmarks:
            location.landmarks.append(landmark)
