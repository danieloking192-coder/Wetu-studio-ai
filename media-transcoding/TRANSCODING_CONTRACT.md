# WETU Creator Core — Multi-rendition Transcoding Contract

## Objective
Produce lightweight delivery renditions without modifying or replacing the original master.

## Renditions
| Profile | Video | Audio | Target use |
|---|---:|---:|---|
| MASTER | original | original | archival/source |
| MOBILE_SAVER_480P | 854x480 max | AAC 64 kbps | low-data mobile |
| MOBILE_720P | 1280x720 max | AAC 96 kbps | mobile |
| STANDARD_1080P | 1920x1080 max | AAC 128 kbps | standard |

Video bitrate targets: 480p 700 kbps; 720p 1800 kbps; 1080p 4000 kbps.

## Encoding rules
- H.264/AVC, yuv420p, AAC audio, MP4 fast-start.
- Preserve source frame rate and aspect ratio; never stretch.
- Never upscale beyond native source dimensions.
- Keep the master untouched.
- Preserve audio and subtitle streams where applicable.

## Adaptive streaming preparation
Each rendition records width/height, video and audio bitrate, duration, frame rate, codecs, file size and SHA-256. Profiles are aligned for later HLS/DASH packaging.

## Integrity gates
1. ffprobe reads the output.
2. Duration differs from master by no more than 250 ms.
3. Dimensions obey the selected profile and never upscale the source.
4. Required video/audio streams exist.
5. Audio/video duration differs by no more than 250 ms.
6. Subtitle stream count is preserved when subtitles exist.
7. Full decode passes without FFmpeg errors.
8. SHA-256 is recorded.

## Size estimation
Estimated bytes = duration_seconds × (video_bitrate + audio_bitrate) / 8. Actual output size is always recorded after encoding.

## Data-saving principle
480p is the low-data default. The master remains archival/source only.

## Non-goal
This contract prepares renditions for adaptive streaming; it does not claim HLS/DASH deployment is already active.
