# ARIA

<p align="center">
  <strong>AI Realtime Intelligent Audio</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey.svg" alt="Windows">
  <img src="https://img.shields.io/badge/license-GPLv3-blue.svg" alt="GPLv3 License">
</p>

**Universal Real-time AI Subtitles for Windows** - Capture and transcribe any audio playing on your system with AI-powered speech recognition.

## Features

- **Universal Audio Capture** - Works with any application (games, videos, calls, etc.)
- **Three Recognition Modes**:
  - **Precise Mode**: Uses Whisper for high-accuracy transcription (NVIDIA GPU recommended)
  - **Realtime Mode**: Uses Sherpa-ONNX/Vosk for word-by-word streaming (CPU/GPU)
  - **LiveCaptions Mode**: Uses Windows 11 built-in Live Captions (✅ **AMD GPU supported**)
- **Multi-language Support**: Chinese, English, Japanese, Korean, and more
- **Real-time Translation**: Translate transcriptions with Google Cloud or NLLB (local)
- **Customizable Overlay**: Draggable subtitle window with adjustable position
- **Multilingual UI**: English, Traditional Chinese, Simplified Chinese
- **Embedded Python**: No separate Python installation required

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10 64-bit or later |
| **CPU** | Intel i5 / AMD Ryzen 5 or better |
| **RAM** | 8 GB (12 GB recommended) |
| **Storage** | 6 GB (Lite) / 12 GB (Full) |

### GPU Requirements

ARIA includes CUDA 12.1 runtime, so **you don't need to install CUDA separately**.

**For Precise Mode:**
- ✅ **NVIDIA GTX 10 series or newer** (recommended)
- ⚠️ **AMD / Intel / No GPU**: Falls back to CPU mode (slower but works)

**For LiveCaptions Mode:**
- ✅ **All GPUs supported** (AMD, NVIDIA, Intel) - uses Windows 11 built-in AI
- ⚠️ **Requires Windows 11 22H2 or later**

### NVIDIA Driver Requirements

| Feature | Minimum Driver Version |
|---------|----------------------|
| CUDA 12.1 | **525.60.13** or later |
| Recommended | **550+** for best compatibility |

> 💡 **Tip**: Update your NVIDIA driver to the latest version for best performance.
> Download from: https://www.nvidia.com/drivers

## Download

### Choose Your Version

| Version | Size | Description | Google Drive | Baidu |
|---------|------|-------------|--------------|-----------------------------|
| **Lite** | ~3 GB | No models included. Download models in-app. | [Google Drive](https://drive.google.com/drive/folders/1rRQrj0IPX7rnQxA30WvmxhH-5c6fWZa8?usp=drive_link) | [Baidu](https://pan.baidu.com/s/1KkSlAv7X5yi90hTYuWZoPQ?pwd=j5ip) |
| **Full** | ~7.6 GB | All models pre-installed. Ready to use. | [Google Drive](https://drive.google.com/drive/folders/1rdxunARIa3-68VV4xAKlbzh_dv_wI130?usp=drive_link) | [Baidu](https://pan.baidu.com/s/1yGc-pU6DdPFw8po60ubI3w?pwd=r2m6) |

### Included Models (Full Version)

| Model | Type | Size | Languages |
|-------|------|------|-----------|
| Whisper Large-v3 | Precise | 3 GB | All |
| Sherpa-ONNX Bilingual | Realtime | 500 MB | Chinese, English |
| Vosk Japanese | Realtime | 1 GB | Japanese |
| NLLB Translation | Translation | 1.2 GB | Many |

## Quick Start

1. Download and extract the ZIP file
2. Double-click **`ARIA.vbs`** (silent) or **`ARIA.bat`** (with console)
3. If using **Lite** version, click **Manage Models** to download required models
4. Select recognition mode and language
5. Click **Start Subtitles**

## Configuration

### Recognition Modes

| Mode | Engine | Best For | GPU Requirement |
|------|--------|----------|----------------|
| **Precise** | Whisper | Speeches, videos, pre-recorded content | NVIDIA recommended |
| **Realtime** | Sherpa-ONNX / Vosk | Live conversations, streaming | CPU/GPU |
| **LiveCaptions** | Windows 11 AI | AMD GPU users, low latency | ✅ AMD/NVIDIA/Intel |

### Supported Languages

| Language | Precise Mode | Realtime Mode | LiveCaptions Mode |
|----------|--------------|---------------|------------------|
| Chinese (中文) | ✅ | ✅ (Sherpa-ONNX) | ✅ |
| English | ✅ | ✅ (Sherpa-ONNX) | ✅ |
| Japanese (日本語) | ✅ | ✅ (Vosk) | ✅ |
| Korean (한국어) | ✅ | ❌ | ✅ |
| Spanish, French, etc. | ✅ | ❌ | ✅ |
| + 50 more | ✅ | ❌ | ❌ |

> 💡 **LiveCaptions Mode**: Supports 11 languages via Windows 11 built-in AI. No model download required!

### Translation

**Local Models (Offline):**
- **NLLB-200**: Meta's multilingual translation model, supports 200+ languages, runs locally

**Online Services (Free APIs):**
- **Google Translate**: Fast and accurate, via web scraping
- **Bing Translator**: Microsoft's translation service
- **Youdao**: 有道翻譯 (specialized for Chinese-English translation)

> 💡 **Note**: Online services use web scraping and may be subject to rate limiting. Local NLLB model recommended for reliability.

## Package Structure

```
ARIA/
├── python/          # Embedded Python (no installation needed)
├── src/             # Source code
├── models/          # AI models (Lite: empty, Full: pre-installed)
├── ARIA.bat         # Launcher with console window
└── ARIA.vbs         # Silent launcher (recommended)
```

## Screenshots

![image-20260117231941984](README.assets/image-20260117231941984.png)
![image-20260117233035105](README.assets/image-20260117233035105.png)

## For Developers

```bash
# Clone the repository
git clone https://github.com/sayksii/aria.git
cd aria

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -e .
pip install PyQt6  # UI framework

# Run
python -m realtime_subtitles.ui.app
```

## License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper)
- [Sherpa-ONNX](https://github.com/k2-fsa/sherpa-onnx)
- [Vosk](https://alphacephei.com/vosk/)
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- [PyAudioWPatch](https://github.com/s0d3s/PyAudioWPatch)

## Contact

- GitHub: [@sayksii](https://github.com/sayksii)
- Email: mark42967151@gmail.com
