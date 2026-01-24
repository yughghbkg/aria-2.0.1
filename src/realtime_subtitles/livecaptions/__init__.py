"""
Windows LiveCaptions integration module.

Provides integration with Windows 11's built-in Live Captions feature
using UI Automation to capture subtitle text for translation and display.
"""

from .monitor import LiveCaptionsMonitor, CaptionEvent
from .controller import LiveCaptionsController
from .pipeline import LiveCaptionsPipeline

__all__ = [
    'LiveCaptionsMonitor',
    'CaptionEvent',
    'LiveCaptionsController',
    'LiveCaptionsPipeline',
]
