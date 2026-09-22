from wetu_studio.location_engine import LocationEngine
from wetu_studio.house_engine import HouseEngine

def test_location_and_realistic_house_metadata():
    le = LocationEngine()
    city = le.create("kin-city", "Kinshasa", "Kinshasa", "DRC")
    le.set_design(city, architecture="modern tropical", environment="urban")
    le.add_landmark(city, "city center")
    he = HouseEngine()
    house = he.create("h1", "Family House", "modern")
    he.set_design(house, exterior="concrete and glass", interior="warm contemporary")
    he.add_material(house, "wood")
    he.add_room(house, "living room")
    assert city.landmarks and house.rooms
