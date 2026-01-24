"""
Windows LiveCaptions Controller
Automatically launch and configure LiveCaptions
"""

import os
import time
from typing import Optional

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None

try:
    import uiautomation as auto
    UIAUTOMATION_AVAILABLE = True
except ImportError:
    UIAUTOMATION_AVAILABLE = False
    auto = None

from ..logger import info, debug, warning, error


class LiveCaptionsController:
    """
    Controls the launch and configuration of Windows LiveCaptions
    """
    
    @staticmethod
    def is_windows_11() -> bool:
        """Check if running on Windows 11"""
        try:
            import platform
            version = platform.version()
            # Windows 11 build number >= 10.0.22000
            parts = version.split('.')
            if len(parts) >= 3:
                build = int(parts[2].split('-')[0])  # Handle format like "10.0.22000-xxx"
                return build >= 22000
            return False
        except Exception as e:
            warning(f"LiveCaptionsController: Error checking Windows version: {e}")
            return False
    
    @staticmethod
    def is_livecaptions_available() -> bool:
        """Check if LiveCaptions feature is available"""
        if not LiveCaptionsController.is_windows_11():
            debug("LiveCaptionsController: Not Windows 11")
            return False
        
        # Can add more checks, such as registry or system settings
        # But basically all Windows 11 systems have this feature
        return True
    
    @staticmethod
    def launch_livecaptions() -> bool:
        """
        Launch LiveCaptions
        
        Method:
        1. Use keyboard shortcut Win + Ctrl + L
        2. Wait for window to appear
        
        Returns:
            bool: Whether launch was successful
        """
        if not PYAUTOGUI_AVAILABLE:
            error("LiveCaptionsController: pyautogui is required")
            return False
        
        try:
            info("LiveCaptionsController: Launching LiveCaptions...")
            
            # Temporarily disable fail-safe to prevent corner trigger issues
            original_failsafe = pyautogui.FAILSAFE
            pyautogui.FAILSAFE = False
            
            try:
                # Method 1: Simulate hotkey
                pyautogui.hotkey('win', 'ctrl', 'l')
                info("LiveCaptionsController: Launched via hotkey (Win+Ctrl+L)")
            finally:
                # Restore fail-safe setting
                pyautogui.FAILSAFE = original_failsafe
            
            # Wait for window to appear
            time.sleep(2)
            
            # Verify window appeared
            if UIAUTOMATION_AVAILABLE:
                try:
                    window = auto.WindowControl(
                        searchDepth=1,
                        Name="Live Captions"
                    )
                    if window.Exists(0, 0):
                        info("LiveCaptionsController: LiveCaptions window found")
                        return True
                except:
                    pass
            
            # Even if verification fails, return success (may have launched but positioning failed)
            return True
            
        except Exception as e:
            error(f"LiveCaptionsController: Failed to launch: {e}")
            return False
    
    @staticmethod
    def minimize_livecaptions_window() -> bool:
        """
        Minimize LiveCaptions window to taskbar
        
        This keeps the window accessible for UI Automation while hiding it from view.
        Better than moving off-screen which breaks UI Automation.
        
        Returns:
            bool: Whether minimizing was successful
        """
        if not UIAUTOMATION_AVAILABLE:
            warning("LiveCaptionsController: uiautomation not available")
            return False
        
        try:
            import win32gui
            import win32con
            
            # Find window by class name
            hwnd = win32gui.FindWindow("LiveCaptionsDesktopWindow", None)
            if hwnd:
                # Minimize to taskbar
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                debug("LiveCaptionsController: Window minimized")
                return True
            else:
                # Try with uiautomation
                window = auto.WindowControl(
                    searchDepth=1, 
                    ClassName="LiveCaptionsDesktopWindow"
                )
                if window.Exists(0, 0):
                    # Move to bottom-right corner and make it small
                    try:
                        import win32api
                        screen_width = win32api.GetSystemMetrics(0)
                        screen_height = win32api.GetSystemMetrics(1)
                        window.MoveWindow(screen_width - 50, screen_height - 50, 1, 1)
                        debug("LiveCaptionsController: Window moved to corner")
                        return True
                    except:
                        pass
                
                warning("LiveCaptionsController: Window not found for minimizing")
                return False
        except Exception as e:
            warning(f"LiveCaptionsController: Failed to minimize window: {e}")
            # Fallback: keep window visible
            return False
    
    @staticmethod
    def hide_livecaptions_window() -> bool:
        """
        Hide LiveCaptions window (but keep it running)
        
        WARNING: Moving window off-screen may break UI Automation access!
        Use minimize_livecaptions_window() instead for better compatibility.
        
        Hides by moving window off-screen
        
        Returns:
            bool: Whether hiding was successful
        """
        if not UIAUTOMATION_AVAILABLE:
            warning("LiveCaptionsController: uiautomation not available")
            return False
        
        try:
            window = auto.WindowControl(
                searchDepth=1, 
                ClassName="LiveCaptionsDesktopWindow"
            )
            if window.Exists(0, 0):
                # Move window off-screen
                window.MoveWindow(-10000, -10000, 1, 1)
                debug("LiveCaptionsController: Window hidden")
                return True
            else:
                warning("LiveCaptionsController: Window not found for hiding")
                return False
        except Exception as e:
            warning(f"LiveCaptionsController: Failed to hide window: {e}")
            return False
    
    @staticmethod
    def show_livecaptions_window() -> bool:
        """
        Show LiveCaptions window
        
        Moves window back to screen center
        
        Returns:
            bool: Whether showing was successful
        """
        if not UIAUTOMATION_AVAILABLE:
            warning("LiveCaptionsController: uiautomation not available")
            return False
        
        try:
            window = auto.WindowControl(
                searchDepth=1, 
                ClassName="LiveCaptionsDesktopWindow"
            )
            if window.Exists(0, 0):
                # Get screen size and move window to bottom center
                try:
                    import win32api
                    screen_width = win32api.GetSystemMetrics(0)
                    screen_height = win32api.GetSystemMetrics(1)
                    
                    # Move to bottom center
                    x = (screen_width - 600) // 2
                    y = screen_height - 200
                    window.MoveWindow(x, y, 600, 150)
                except:
                    # If unable to get screen size, move to fixed position
                    window.MoveWindow(500, 800, 600, 150)
                
                debug("LiveCaptionsController: Window shown")
                return True
            else:
                warning("LiveCaptionsController: Window not found for showing")
                return False
        except Exception as e:
            warning(f"LiveCaptionsController: Failed to show window: {e}")
            return False
    
    @staticmethod
    def is_livecaptions_running() -> bool:
        """
        Check if LiveCaptions is currently running
        
        Returns:
            bool: Whether it's running
        """
        if not UIAUTOMATION_AVAILABLE:
            return False
        
        try:
            window = auto.WindowControl(
                searchDepth=1, 
                ClassName="LiveCaptionsDesktopWindow"
            )
            return window.Exists(0, 0)
        except:
            return False


# Simple test
if __name__ == "__main__":
    print("Testing LiveCaptionsController...")
    
    # Check system
    print(f"Is Windows 11: {LiveCaptionsController.is_windows_11()}")
    print(f"LiveCaptions available: {LiveCaptionsController.is_livecaptions_available()}")
    
    # Check if already running
    if LiveCaptionsController.is_livecaptions_running():
        print("LiveCaptions is already running")
    else:
        print("LiveCaptions is not running")
        
        # Try to launch
        if LiveCaptionsController.is_livecaptions_available():
            print("Launching LiveCaptions...")
            if LiveCaptionsController.launch_livecaptions():
                print("Successfully launched!")
                
                time.sleep(2)
                
                # Test hide
                print("Hiding window...")
                LiveCaptionsController.hide_livecaptions_window()
                
                time.sleep(2)
                
                # Test show
                print("Showing window...")
                LiveCaptionsController.show_livecaptions_window()
            else:
                print("Failed to launch")
        else:
            print("LiveCaptions is not available on this system")
