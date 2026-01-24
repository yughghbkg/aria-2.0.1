# ARIA Changelog

All notable changes to ARIA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-25

### Added
- **Live Captions Mode**: Integration with Windows 11 built-in Live Captions
  - Supports AMD, NVIDIA, and Intel GPUs (uses Windows AI engine)
  - Multiple language support via Windows built-in models
  - No additional model downloads required
  - Lower latency and resource usage
  - Requires Windows 11 22H2 or later
- LiveCaptions monitor with UI Automation for caption capture
- LiveCaptions controller for window management
- Translation overlay support for LiveCaptions mode
- Three-mode selector in settings window (Precise/Real-time/Live Captions)

### Changed
- Updated UI to support three recognition modes instead of two
- Improved mode selection logic in settings window
- Enhanced overlay behavior for Live Captions mode (shows Windows native caption + ARIA translation)

### Fixed
- All Chinese comments converted to English for better code maintainability
- Improved window finding logic with better error handling
- Fixed UI Automation element search with proper timeout handling

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
