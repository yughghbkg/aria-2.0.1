"""
Floating Subtitle Overlay Window using PyQt6.

A transparent, always-on-top, draggable window that displays subtitles.
"""

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QApplication, QSizeGrip, QFrame, QTextEdit
)
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette, QScreen, QPainter
from typing import Optional, Callable
import sys

import ctypes
from ctypes.wintypes import POINT

from realtime_subtitles.settings_manager import get_settings_manager

class SubtitleOverlay(QWidget):
    """
    Transparent floating subtitle overlay using PyQt6.
    
    Features:
    - Transparent background
    - Always on top
    - Draggable (Native)
    - Resizable (Native 4-corner)
    - Positioned at bottom of screen
    """
    
    # Resize constants
    RESIZE_MARGIN = 10
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        position_key: str = "overlay",
        on_close: Optional[Callable] = None,
    ):
        """Initialize the overlay window."""
        super().__init__(parent)
        
        self._position_key = position_key
        self._on_close_callback = on_close
        
        # Drag/Resize state
        self._drag_pos: Optional[QPoint] = None
        self._resize_edge: Optional[int] = None
        self._initial_geometry = None
        
        # Window dimensions
        self._window_width = 1200
        self._window_height = 120
        
        # Enable mouse tracking is NOT needed for native event, 
        # but good for other hover effects if any.
        self.setMouseTracking(True)
        
        # Setup window
        self._setup_window()
        self._create_ui()
        
        # Position window after a short delay
        QTimer.singleShot(100, self._position_window)
    
    def _setup_window(self) -> None:
        """Configure window flags and appearance."""
        # Frameless, always on top, tool window (no taskbar)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Enable transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set window title
        self.setWindowTitle("Subtitles")
        
        # Initial size
        self.resize(self._window_width, self._window_height)
    
    def _create_ui(self) -> None:
        """Create the UI elements."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # Add margin for resize handles
        layout.setSpacing(0)
        
        # Container frame with dark background
        self.container = QFrame()
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            #container {
                background-color: rgba(42, 42, 42, 230);
                border-radius: 12px;
            }
        """)
        # Allow mouse events to pass through container to the resizing window
        self.container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(self.container)
        
        # Container layout
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(8, 6, 8, 6)
        container_layout.setSpacing(5)
        
        # Subtitle label (main text)
        self.subtitle_label = QTextEdit()
        self.subtitle_label.setReadOnly(True)
        self.subtitle_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.subtitle_label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.subtitle_label.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.subtitle_label.setFrameStyle(QFrame.Shape.NoFrame)
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.document().setDocumentMargin(20)
        self.subtitle_label.setStyleSheet("""
            QTextEdit {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        # Allow mouse events to pass through text edits
        self.subtitle_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        container_layout.addWidget(self.subtitle_label)
        
        # Translation label
        self.translation_label = QTextEdit()
        self.translation_label.setReadOnly(True)
        self.translation_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.translation_label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.translation_label.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.translation_label.setFrameStyle(QFrame.Shape.NoFrame)
        self.translation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.translation_label.document().setDocumentMargin(20)
        self.translation_label.setStyleSheet("""
            QTextEdit {
                color: #90EE90;
                font-size: 20px;
                background: transparent;
                border: none;
            }
        """)
        self.translation_label.hide()
        # Allow mouse events to pass through text edits
        self.translation_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        container_layout.addWidget(self.translation_label)
        
        # No size grip needed anymore
    
    def _position_window(self) -> None:
        """Position the window at saved position or default."""
        screen = QApplication.primaryScreen()
        if screen is None: return
        screen_geo = screen.geometry()
        w, h = screen_geo.width(), screen_geo.height()
        
        # Dynamic width
        ratio = 0.40 if w >= 3840 else (0.55 if w >= 2560 else 0.70)
        self._window_width = int(w * ratio)
        
        # Restore position
        settings = get_settings_manager()
        sx = settings.get(f"{self._position_key}_x")
        sy = settings.get(f"{self._position_key}_y")
        
        if sx is not None and sy is not None:
            self.resize(self._window_width, self._window_height)
            self.move(int(sx), int(sy))
        else:
            x = (w - self._window_width) // 2
            y = int(h * 0.65)
            self.resize(self._window_width, self._window_height)
            self.move(x, y)
    
    def _save_position(self) -> None:
        """Save current position to settings."""
        settings = get_settings_manager()
        settings.set(f"{self._position_key}_x", self.x())
        settings.set(f"{self._position_key}_y", self.y())
        settings.save()

    # === Paint Event for Transparency ===
    def paintEvent(self, event):
        """Paint a nearly transparent background to catch mouse events."""
        painter = QPainter(self)
        # Use a very low alpha value (1/255) to make it invisible but clickable
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))
        
    # === Hit Testing & Resizing (Python Implementation) ===
    
    def _hit_test(self, pos: QPoint) -> int:
        """Determine which edge/corner the mouse is on."""
        rect = self.rect()
        x, y, w, h = pos.x(), pos.y(), rect.width(), rect.height()
        m = self.RESIZE_MARGIN
        
        # Edges
        on_left = x < m
        on_right = x > w - m
        on_top = y < m
        on_bottom = y > h - m
        
        # Corners
        if on_top and on_left: return 1  # Top-Left
        if on_top and on_right: return 2  # Top-Right
        if on_bottom and on_right: return 3  # Bottom-Right
        if on_bottom and on_left: return 4  # Bottom-Left
        
        # Sides
        if on_top: return 5     # Top
        if on_bottom: return 6  # Bottom
        if on_left: return 7    # Left
        if on_right: return 8   # Right
        
        return 0  # None (Center)
    
    def _update_cursor(self, edge: int):
        """Update cursor capability based on edge."""
        cursors = {
            1: Qt.CursorShape.SizeFDiagCursor, # Top-Left
            2: Qt.CursorShape.SizeBDiagCursor, # Top-Right
            3: Qt.CursorShape.SizeFDiagCursor, # Bottom-Right
            4: Qt.CursorShape.SizeBDiagCursor, # Bottom-Left
            5: Qt.CursorShape.SizeVerCursor,   # Top
            6: Qt.CursorShape.SizeVerCursor,   # Bottom
            7: Qt.CursorShape.SizeHorCursor,   # Left
            8: Qt.CursorShape.SizeHorCursor,   # Right
            0: Qt.CursorShape.ArrowCursor,     # Center
        }
        self.setCursor(cursors.get(edge, Qt.CursorShape.ArrowCursor))
    
    def mousePressEvent(self, event):
        """Handle mouse press for resize or drag."""
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._hit_test(event.pos())
            
            if edge != 0:
                # Start Resize
                self._resize_edge = edge
                self._initial_geometry = self.geometry()
                self._drag_pos = event.globalPosition().toPoint()
            else:
                # Start Move (if not on edges)
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for update cursor, resize, or drag."""
        # 1. Update Cursor (if no buttons pressed)
        if event.buttons() == Qt.MouseButton.NoButton:
            edge = self._hit_test(event.pos())
            self._update_cursor(edge)
            # Change to hand cursor if in center (draggable)
            if edge == 0:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            return
        
        # 2. Handle Action (if Left Button pressed)
        if event.buttons() & Qt.MouseButton.LeftButton:
            
            # Resizing
            if self._resize_edge:
                self._handle_resize(event.globalPosition().toPoint())
                event.accept()
                return

            # Moving
            if self._drag_pos and self._resize_edge is None:
                self.move(event.globalPosition().toPoint() - self._drag_pos)
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                event.accept()
    
    def _handle_resize(self, global_mouse_pos: QPoint):
        """Calculate and apply new geometry during resize."""
        if not self._initial_geometry or not self._drag_pos:
            return
            
        initial = self._initial_geometry
        delta = global_mouse_pos - self._drag_pos
        
        x, y, w, h = initial.x(), initial.y(), initial.width(), initial.height()
        dx, dy = delta.x(), delta.y()
        
        # Apply delta based on edge
        # 1:TL, 2:TR, 3:BR, 4:BL, 5:T, 6:B, 7:L, 8:R
        
        # X-axis
        if self._resize_edge in [1, 4, 7]: # Left side
            x += dx
            w -= dx
        elif self._resize_edge in [2, 3, 8]: # Right side
            w += dx
            
        # Y-axis
        if self._resize_edge in [1, 2, 5]: # Top side
            y += dy
            h -= dy
        elif self._resize_edge in [3, 4, 6]: # Bottom side
            h += dy
            
        # Min size constraints
        min_w, min_h = 200, 60
        if w < min_w: return
        if h < min_h: return
        
        self.setGeometry(x, y, w, h)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.LeftButton:
            # End ops
            self._resize_edge = None
            self._drag_pos = None
            self._initial_geometry = None
            
            self._save_position()
            
            # Reset cursor
            self._update_cursor(self._hit_test(event.pos()))
            event.accept()
    
    # === Window close ===
    def closeEvent(self, event):
        """Handle window close."""
        # Save position on close
        self._save_position()
        
        if self._on_close_callback:
            self._on_close_callback()
        event.accept()
    
    # === Public API ===
    def update_subtitle(
        self,
        text: str,
        language: str = "",
        translated_text: str = None,
        committed_translation: str = None,
        draft_translation: str = None,
    ) -> None:
        """Update the displayed subtitle.
        
        Args:
            text: Subtitle text to display
            language: Language code (unused currently)
            translated_text: Translated text (optional)
            committed_translation: Stable translation text (white)
            draft_translation: Unstable/draft translation text (green)
        """
        self.subtitle_label.setPlainText(text)
        # Auto-scroll to bottom to show latest content
        self.subtitle_label.verticalScrollBar().setValue(
            self.subtitle_label.verticalScrollBar().maximum()
        )
        
        # Auto-hide original text label if empty (fixes blank space in Translation Overlay)
        if text and text.strip():
            self.subtitle_label.show()
        else:
            self.subtitle_label.hide()
        
        # Handle translation with dual-color support (committed=white, draft=green)
        if committed_translation is not None or draft_translation is not None:
            committed = committed_translation or ""
            draft = draft_translation or ""
            
            # Build HTML with dual colors
            html_parts = []
            if committed:
                # White text for committed (stable)
                escaped_committed = committed.replace('\n', '<br>')
                html_parts.append(f'<span style="color: white;">{escaped_committed}</span>')
            if draft:
                # Green text for draft (in progress)
                escaped_draft = draft.replace('\n', '<br>')
                html_parts.append(f'<span style="color: #90EE90;">{escaped_draft}</span>')
            
            if html_parts:
                html_content = '<br>'.join(html_parts)
                self.translation_label.setHtml(html_content)
                self.translation_label.verticalScrollBar().setValue(
                    self.translation_label.verticalScrollBar().maximum()
                )
                self.translation_label.show()
            else:
                self.translation_label.hide()
        elif translated_text and translated_text.strip():
            # Simple mode: just show translated text in default color
            self.translation_label.setPlainText(translated_text)
            self.translation_label.verticalScrollBar().setValue(
                self.translation_label.verticalScrollBar().maximum()
            )
            self.translation_label.show()
        else:
            self.translation_label.hide()
        
        # Show if hidden
        if not self.isVisible():
            self.show()
    
    def clear(self) -> None:
        """Clear the subtitle display."""
        self.subtitle_label.setPlainText("")
        self.translation_label.setPlainText("")
        self.translation_label.hide()
    
    def set_multiline_mode(self, enabled: bool) -> None:
        """Enable multiline mode (taller overlay)."""
        if enabled:
            self._window_height = 180
            self.subtitle_label.setStyleSheet("""
                QTextEdit {
                    color: white;
                    font-size: 22px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }
            """)
        else:
            self._window_height = 120
            self.subtitle_label.setStyleSheet("""
                QTextEdit {
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }
            """)
        self.resize(self._window_width, self._window_height)
    
    def set_translation_mode(self, enabled: bool) -> None:
        """Configure as translation overlay (green text)."""
        if enabled:
            self.subtitle_label.setStyleSheet("""
                QTextEdit {
                    color: #90EE90;
                    font-size: 24px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }
            """)


# Test
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    overlay = SubtitleOverlay()
    overlay.show()
    overlay.update_subtitle("Hello, this is a test subtitle!", "en")
    
    # Test multiline
    def test_multiline():
        overlay.update_subtitle(
            "This is a very long subtitle that should wrap to multiple lines. "
            "Let's see how PyQt6 handles word wrapping compared to Tkinter.",
            "en",
            "這是一個很長的翻譯文字，應該要自動換行顯示。"
        )
    
    QTimer.singleShot(2000, test_multiline)
    
    sys.exit(app.exec())
