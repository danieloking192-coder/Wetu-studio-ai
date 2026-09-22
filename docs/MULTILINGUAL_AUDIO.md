# WETU Multilingual + Audio

WETU treats language as production data, not as a final translation step.

Supported system languages:
- French (fr)
- English (en)
- Spanish (es)
- Portuguese (pt)
- Arabic (ar)
- Swahili (sw)
- Lingala (ln)

Each dialogue line retains speaker, language, voice ID and subtitle text. The audio layer uses provider adapters so voice generation can later be connected to real providers without changing production state.

The local audio provider is a deterministic development manifest. It does **not** generate real audio.