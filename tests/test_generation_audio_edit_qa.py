from wetu_studio.generation_engine import GenerationEngine
from wetu_studio.audio_engine import AudioEngine
from wetu_studio.edit_engine import EditEngine
from wetu_studio.qa_engine import QAEngine, QAReport

def test_generation_fingerprint_and_artifact():
    e=GenerationEngine(); r=e.create_request("g1","p1","s1","cinematic shot",["ref1"],"provider","model")
    assert e.fingerprint_request(r) == e.fingerprint_request(r)
    a=e.register_artifact(r,b"media"); assert len(a.content_hash)==64 and a.status=="READY"

def test_audio_multilingual_and_timing():
    e=AudioEngine(); t=e.create_track("a1"); e.add_line(t,"c1","Bonjour","fr",start_ms=0,end_ms=900); e.add_line(t,"c2","Hello","en",start_ms=900,end_ms=1800); assert len(t.lines)==2

def test_edit_overlap_same_layer_only():
    e=EditEngine(); t=e.create("t1"); a=e.add_item(t,"v1","VIDEO","x",0,1000); b=e.add_item(t,"v2","VIDEO","y",500,500); c=e.add_item(t,"a1","AUDIO","z",500,500,1); assert e.overlaps(t,a,b); assert not e.overlaps(t,a,c)

def test_qa_blocks_identity_mismatch():
    q=QAEngine(); r=QAReport(); q.validate_identity(r,(('face','a'),),(('face','b'),)); assert not r.passed
