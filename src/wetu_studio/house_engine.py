from dataclasses import dataclass, field

@dataclass
class House:
    house_id: str
    name: str
    style: str = ""
    exterior: str = ""
    interior: str = ""
    materials: list[str] = field(default_factory=list)
    rooms: list[str] = field(default_factory=list)
    realism_notes: list[str] = field(default_factory=list)

class HouseEngine:
    def create(self, house_id: str, name: str, style: str = "") -> House:
        if not house_id.strip() or not name.strip():
            raise ValueError("house_id and name are required")
        return House(house_id, name, style)

    def set_design(self, house: House, exterior: str = "", interior: str = "") -> None:
        house.exterior, house.interior = exterior, interior

    def add_material(self, house: House, material: str) -> None:
        if material.strip() and material not in house.materials:
            house.materials.append(material)

    def add_room(self, house: House, room: str) -> None:
        if room.strip() and room not in house.rooms:
            house.rooms.append(room)

    def add_realism_note(self, house: House, note: str) -> None:
        if note.strip() and note not in house.realism_notes:
            house.realism_notes.append(note)
