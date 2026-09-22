RATE_LIMIT_MAX = int(os.environ.get("WETU_RATE_LIMIT_MAX", "120"))
_STATE_LOCK = threading.RLock()
AUTH_TOKEN = os.environ.get("WETU_AUTH_TOKEN")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
MAX_PROJECTS = int(os.environ.get("WETU_MAX_PROJECTS", "1000"))
MAX_TITLE_CHARS = int(os.environ.get("WETU_MAX_TITLE_CHARS", "200"))
MAX_ID_CHARS = int(os.environ.get("WETU_MAX_ID_CHARS", "128"))
MAX_PROMPT_CHARS = int(os.environ.get("WETU_MAX_PROMPT_CHARS", "20000"))
MAX_LIST_ITEMS = int(os.environ.get("WETU_MAX_LIST_ITEMS", "200"))
_RATE_LOCK = threading.Lock()
_RATE_BUCKETS = {}
LOCALIZATION = LocalizationEngine()
AUDIO = AudioRegistry()
_LOCALIZATION_TRACKS = {}

def _load_persistent_state():
    state = CreatorState(project_id="demo")
    if not STATE_FILE.exists():
        return state