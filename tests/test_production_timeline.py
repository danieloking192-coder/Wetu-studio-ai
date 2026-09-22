from wetu_studio.production_timeline import ProductionTimeline, EditItem

def test_timeline_add_validate_and_duration():
    t=ProductionTimeline("t1")
    t.add(EditItem("v1","a1","VIDEO",0,5000,0))
    t.add(EditItem("a1","a2","AUDIO",1000,2000,1))
    assert t.validate()["passed"]
    assert t.duration_ms()==5000

def test_timeline_detects_overlap():
    t=ProductionTimeline("t1")
    t.add(EditItem("v1","a1","VIDEO",0,5000,0))
    t.add(EditItem("v2","a2","VIDEO",4000,2000,0))
    assert not t.validate()["passed"]