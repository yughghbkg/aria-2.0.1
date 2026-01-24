"""
Windows LiveCaptions Monitor
Captures real-time subtitle text using UI Automation
"""

import time
import threading
from typing import Optional, Callable
from dataclasses import dataclass

try:
    import uiautomation as auto
    UIAUTOMATION_AVAILABLE = True
except ImportError:
    UIAUTOMATION_AVAILABLE = False
    auto = None

from ..logger import info, debug, warning, error


@dataclass
class CaptionEvent:
    """Caption event data"""
    text: str
    timestamp: float
    is_final: bool = True


class LiveCaptionsMonitor:
    """
    Monitors Windows LiveCaptions window for text changes
    
    Uses UI Automation technology to capture text content from 
    Windows 11's built-in Live Captions feature.
    
    Example:
        >>> def on_caption(event):
        ...     print(f"[{event.timestamp}] {event.text}")
        >>> 
        >>> monitor = LiveCaptionsMonitor(on_caption=on_caption)
        >>> monitor.start()
        >>> # ... do something ...
        >>> monitor.stop()
    """
    
    # LiveCaptions window properties (multi-language support)
    WINDOW_CLASS = "LiveCaptionsDesktopWindow"  # Consistent across all language versions
    # Supported window names (multi-language, fallback method)
    WINDOW_NAMES = [
        "Live Captions",        # English (en-US)
        "即時輔助字幕",            # Traditional Chinese (zh-TW)
        "实时字幕",               # Simplified Chinese (zh-CN)
        "ライブキャプション",       # Japanese (ja-JP)
        "라이브 캡션",            # Korean (ko-KR)
        "Legendas ao Vivo",     # Portuguese (pt-BR)
        "Subtítulos en Vivo",   # Spanish (es-ES)
        "Sous-titres en Direct", # French (fr-FR)
        "Live-Untertitel",      # German (de-DE)
        "Sottotitoli Live",     # Italian (it-IT)
        "Живые субтитры",       # Russian (ru-RU)
    ]
    
    def __init__(
        self,
        on_caption: Optional[Callable[[CaptionEvent], None]] = None,
        poll_interval: float = 0.1,  # 100ms polling interval
    ):
        """
        Initialize the monitor
        
        Args:
            on_caption: Caption callback function
            poll_interval: Polling interval in seconds
        """
        if not UIAUTOMATION_AVAILABLE:
            raise ImportError(
                "uiautomation is required for LiveCaptions mode. "
                "Install it with: pip install uiautomation"
            )
        
        self.on_caption = on_caption or self._default_callback
        self.poll_interval = poll_interval
        
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._last_text = ""
        self._caption_element: Optional[auto.Control] = None
        
        info("LiveCaptionsMonitor: Initialized")
    
    def _find_livecaptions_window(self) -> Optional[auto.WindowControl]:
        """Find the LiveCaptions window"""
        try:
            window = auto.WindowControl(
                searchDepth=1,
                ClassName=self.WINDOW_CLASS
            )
            if window.Exists(maxSearchSeconds=2):
                return window
            
            # Fallback: iterate through windows
            for window in auto.GetRootControl().GetChildren():
                if window.ClassName == self.WINDOW_CLASS:
                    return window
                if any(name in window.Name for name in self.WINDOW_NAMES):
                    return window
            return None
            
        except Exception as e:
            return None
    
    def _find_caption_element(self, window: auto.WindowControl) -> Optional[auto.Control]:
        """
        Find the caption text element in LiveCaptions window
        """
        try:
            # Try CaptionsTextBlock first (actual captions)
            try:
                caption_element = window.TextControl(AutomationId="CaptionsTextBlock", searchDepth=10)
                if caption_element and caption_element.Exists(maxSearchSeconds=0.5):
                    return caption_element
            except:
                pass
            
            # Fall back to ReadyToCaptionTextBlock (initial state)
            try:
                ready_element = window.TextControl(AutomationId="ReadyToCaptionTextBlock", searchDepth=10)
                if ready_element and ready_element.Exists(maxSearchSeconds=0.5):
                    return ready_element
            except:
                pass
            
            # Search by index as last resort
            try:
                for i in range(1, 4):
                    text_ctrl = window.TextControl(searchDepth=15, foundIndex=i)
                    if text_ctrl and text_ctrl.Exists(maxSearchSeconds=0.3):
                        automation_id = getattr(text_ctrl, 'AutomationId', '') or ""
                        if automation_id in ["CaptionsTextBlock", "ReadyToCaptionTextBlock"]:
                            return text_ctrl
            except:
                pass
            
            return None
            
        except Exception as e:
            error(f"LiveCaptionsMonitor: Error finding caption element: {e}")
            return None
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        info("LiveCaptionsMonitor: Monitor loop started")
        retry_count = 0
        max_retries = 10
        
        # Initial placeholder texts to ignore (don't set as _last_text)
        initial_texts = [
            "即時輔助字幕",
            "实时辅助字幕",
            "準備好",
            "准备好",
            "Ready for live subtitles",
            "Live captions"
        ]
        
        while self._running:
            try:
                # Find window and element
                if not self._caption_element:
                    window = self._find_livecaptions_window()
                    if window:
                        self._caption_element = self._find_caption_element(window)
                        retry_count = 0
                    else:
                        retry_count += 1
                        if retry_count >= max_retries:
                            error("LiveCaptionsMonitor: Max retries reached, stopping")
                            self._running = False
                            break
                        time.sleep(1)
                        continue
                
                # Periodically refresh element to check for CaptionsTextBlock
                # (CaptionsTextBlock only appears when audio is playing)
                refresh_needed = False
                if hasattr(self, '_last_element_refresh'):
                    if time.time() - self._last_element_refresh > 5:  # Refresh every 5 seconds
                        refresh_needed = True
                else:
                    self._last_element_refresh = time.time()
                
                if refresh_needed:
                    window = self._find_livecaptions_window()
                    if window:
                        new_element = self._find_caption_element(window)
                        if new_element:
                            current_id = getattr(self._caption_element, 'AutomationId', '') or ""
                            new_id = getattr(new_element, 'AutomationId', '') or ""
                            
                            # Switch to CaptionsTextBlock if available
                            if current_id == "ReadyToCaptionTextBlock" and new_id == "CaptionsTextBlock":
                                self._caption_element = new_element
                                self._last_text = ""  # Reset to detect new content
                            elif new_id == "CaptionsTextBlock":
                                self._caption_element = new_element
                    
                    self._last_element_refresh = time.time()
                
                # Read text
                try:
                    # Try multiple methods to get text
                    current_text = None
                    
                    # Refresh element reference periodically to avoid stale references
                    # Re-get the element every time to ensure fresh reference
                    if self._caption_element:
                        try:
                            # Test if element is still valid by accessing a property
                            _ = self._caption_element.ClassName
                        except:
                            # Element reference is stale, re-find it
                            debug("LiveCaptionsMonitor: Element reference stale, re-finding...")
                            self._caption_element = None
                    
                    # Method 1: Name property
                    if self._caption_element:
                        try:
                            text_from_name = self._caption_element.Name
                            if text_from_name is not None:  # Accept empty string
                                current_text = text_from_name
                        except:
                            pass
                    
                    # If current_text is None (not empty string), it means read failed
                    if current_text is None:
                        current_text = ""  # Treat as empty, not None
                    
                    # Skip if it's initial placeholder text
                    if current_text:
                        is_initial_text = any(initial_text in current_text for initial_text in initial_texts)
                    else:
                        is_initial_text = False
                    
                    # Check for new content (including empty -> non-empty or non-empty -> different)
                    if current_text != self._last_text:
                        # Only send event if it's not initial placeholder and not empty
                        if current_text and not is_initial_text:
                            # Send event
                            event = CaptionEvent(
                                text=current_text,
                                timestamp=time.time(),
                                is_final=True
                            )
                            self.on_caption(event)
                            self._last_text = current_text
                        elif is_initial_text:
                            debug(f"LiveCaptionsMonitor: Skipping initial placeholder")
                            self._last_text = current_text
                        else:
                            # Empty text - just update last_text without sending event
                            self._last_text = current_text
                        
                except Exception as e:
                    warning(f"LiveCaptionsMonitor: Error reading text: {e}")
                    self._caption_element = None  # Re-find element
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                error(f"LiveCaptionsMonitor: Monitor loop error: {e}")
                time.sleep(1)
        
        info("LiveCaptionsMonitor: Monitor loop stopped")
    
    def start(self):
        """Start monitoring"""
        if self._running:
            warning("LiveCaptionsMonitor: Already running")
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        info("LiveCaptionsMonitor: Started")
    
    def stop(self):
        """Stop monitoring"""
        if not self._running:
            return
        
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
        info("LiveCaptionsMonitor: Stopped")
    
    def _default_callback(self, event: CaptionEvent):
        """Default callback"""
        print(f"[LiveCaptions] {event.text}")


# Simple test
if __name__ == "__main__":
    print("Testing LiveCaptionsMonitor...")
    print("Please make sure Windows LiveCaptions is running (Win+Ctrl+L)")
    print("Press Ctrl+C to stop")
    
    monitor = LiveCaptionsMonitor()
    monitor.start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
        monitor.stop()
        print("Done!")
