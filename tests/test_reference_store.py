from wetu_studio.reference_store import ReferenceStore, ReferenceRecord

def test_reference_store_tracks_assets():
    s = ReferenceStore()
    x = s.add(ReferenceRecord("ref-1","p","image","memory://ref"))
    assert s.get("ref-1") is x