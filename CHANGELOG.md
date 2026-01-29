# ARIA Changelog

All notable changes to ARIA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-29

### Added
- **Live Captions Mode**: Direct integration with Windows 11 built-in Live Captions (Requires 22H2+). Low latency, no model download needed.
- **Precise Mode Update**: Added support for Russian (Russian language).
- **Resizable Window**: Subtitle window can now be freely resized from all four sides (4-corner resizing).
- **Lite Version**: Introduced ARIA-v2-lite (~300MB) for lightweight deployment.

### Changed
- Simplified UI with clearer mode selection (Precise / Real-time / Live Captions).
- Enhanced translation overlay behavior for better synchronization.

### Fixed
- Improved window finding stability and error handling.

## [1.0.0] - 2026-01-12

### Added
- Initial release
- Two recognition modes: Precise (Whisper) and Realtime (Sherpa-ONNX/Vosk)
- Universal audio capture using WASAPI loopback
- Multi-language speech recognition (Chinese, English, Japanese, Korean, etc.)
- Real-time translation with Google Cloud and NLLB (local)
- Draggable subtitle overlay
- System tray integration
- Multi-language UI (English, Traditional Chinese, Simplified Chinese)
- Model manager for downloading and managing AI models
- Voice Activity Detection (VAD) settings
