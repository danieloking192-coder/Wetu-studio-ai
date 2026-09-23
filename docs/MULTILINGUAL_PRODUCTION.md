# WETU Multilingual Production

WETU separates script language from video language.

Example: screenplay in French, output language Tshiluba (tsh).

Pipeline:
French script -> meaning-preserving Tshiluba adaptation -> dialogue -> target-language voice -> lip-sync -> subtitles -> final QA.

Supported output-language identifiers include French, English, Lingala, Swahili, Tshiluba and Kikongo.

The architecture is provider-neutral. A production deployment must configure a server-side translation and voice provider capable of the selected language. WETU does not claim that a language is fully supported by an external provider until that provider is configured and tested.
