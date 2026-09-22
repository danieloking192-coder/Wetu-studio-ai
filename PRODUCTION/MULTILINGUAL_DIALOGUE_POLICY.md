# WETU STUDIO AI — Multilingual Dialogue Policy

Status: CORE PRODUCT DESIGN

WETU supports multilingual conversations at the dialogue layer. Each line records its speaker and source language and may store translations for other supported languages.

Initial language set: French, English, Spanish, Portuguese, Arabic, Swahili and Lingala.

## Requirements
- Preserve the original dialogue and language code.
- Translations are separate from the source line.
- A scene may contain speakers using different languages.
- Future voice adapters may map each language to appropriate speech synthesis.
- Subtitles/dubbing should retain timing and speaker identity.
- No translation should silently replace the original source dialogue.

WETU should be designed so a future production can contain natural multilingual conversations without rebuilding the script.
