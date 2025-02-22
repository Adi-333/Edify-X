from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QGridLayout, QScrollArea
from PyQt6.QtGui import QIcon, QPixmap, QFont
from PyQt6.QtCore import Qt, QSize
import sys

MAIN_ICON = "./assets/icons/main_icon.png"

BG_COLOR = "#121212"
CANVAS_COLOR = "#212121"
SPANEL_COLOR = "#282828"
SPANEL_TXT_COLOR = "#787878"
SPANEL_HEADING_COLOR = "#3d3b3b"

class Window(QWidget):
    def __init__(self):
        super().__init__()

        # Get screen size
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.setGeometry(screen_geometry)

        # Window properties
        self.setWindowTitle("Edify-X")
        self.setWindowIcon(QIcon(MAIN_ICON))
        self.setStyleSheet(f"background-color: {BG_COLOR};")  # Apply main background color

        # Main layout (horizontal)
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Create and add toolbar
        toolbar_widget = self.create_toolbar()
        main_layout.addWidget(toolbar_widget)

        # Create and add canvas at the center
        self.canvas = self.create_canvas()
        main_layout.addWidget(self.canvas, 1)
        
        # Create and add side panel at the right side
        side_panel = self.create_side_panel()
        main_layout.addWidget(side_panel)

        # Push other elements to the right
        main_layout.addStretch()  # Push other elements to the right

    # ------- Left Toolbar ----------- #
    def create_toolbar(self):
        toolbar_widget = QWidget()  # Wrapper for styling
        toolbar_widget.setFixedWidth(45)  # Set toolbar width
        toolbar_widget.setStyleSheet(f"background-color: {CANVAS_COLOR};")  # Apply background color

        toolbar_layout = QVBoxLayout()
        toolbar_layout.setSpacing(30)
        toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icons = {
            "Select": "Select.svg",
            "Move": "Move.svg",
            "Crop": "Crop.svg",
            "Undo": "Undo.svg",
            "Redo": "Redo.svg",
            "Zoom-in": "Zoom-in.svg",
            "Zoom-out": "Zoom-out.svg",
            "Text": "Text.svg"
        }

        for name, icon in icons.items():
            button = QPushButton()
            button.setIcon(QIcon(f"./assets/icons/{icon}"))  # Set SVG as icon
            button.setIconSize(QSize(15, 15))  # Adjust icon size
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent; 
                    color: white; 
                    padding: 5px; 
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);  /* Light transparent white */
                    border-radius: 5px;
                }
            """)

            button.clicked.connect(lambda checked, n=name: self.button_clicked(n))  # Connect button click

            toolbar_layout.addWidget(button)

        toolbar_widget.setLayout(toolbar_layout)  # Set layout inside widget
        return toolbar_widget  # Return wrapped toolbar

    def button_clicked(self, name):
        print(f"{name} button clicked!")  # Example function

    #------- Center Canas ----------#
    def create_canvas(self):
        canvas_wrapper = QWidget()
        canvas_layout = QVBoxLayout(canvas_wrapper)
        canvas_layout.setContentsMargins(30, 30, 30, 30)

        canvas = QFrame()
        canvas.setStyleSheet(f"background-color: {CANVAS_COLOR}; border: 2px solid {SPANEL_COLOR};")
        canvas.setMinimumSize(900, 500)

        canvas_layout.addWidget(canvas, alignment = Qt.AlignmentFlag.AlignCenter)

        return canvas_wrapper

    # ----------------- Side Panel ------------------------ #
    def create_side_panel(self):
        side_panel_frame = QFrame()
        side_panel_frame.setStyleSheet(f"background-color: {CANVAS_COLOR}; border-radius: 8px;")
        side_panel_frame.setFixedWidth(220)
        
        # Use QVBoxLayout for better vertical alignment
        side_layout = QVBoxLayout(side_panel_frame)  
        side_layout.setSpacing(10)
        side_layout.setContentsMargins(10, 10, 10, 10)

        # -------- Blending Section --------
        blending_layout = QVBoxLayout()

        blending_label = QLabel("Blending")
        blending_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        blending_label.setStyleSheet(f"color: {SPANEL_HEADING_COLOR};")
        blending_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)  # Center align text
        blending_layout.addWidget(blending_label)

        # Add stretch above blending box to push it towards center
        blending_layout.addStretch(1)  

        blending_box = QFrame()
        blending_box.setStyleSheet(f"background-color: {SPANEL_COLOR}; border-radius: 8px; padding: 10px;")
        blending_box_layout = QVBoxLayout(blending_box)

        blending_options = ["Hue", "Saturation", "Luminosity"]
        for option in blending_options:
            btn = QPushButton(option)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent; 
                    color: #787878; 
                    padding: 5px; 
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);  /* Light transparent white */
                    border-radius: 5px;
                }
            """)
            blending_box_layout.addWidget(btn)

        blending_layout.addWidget(blending_box)

        # Add stretch below the blending box to push it towards center
        blending_layout.addStretch(2)  

        # -------- Adding to Side Panel Layout --------
        side_layout.addLayout(blending_layout)

        return side_panel_frame  # Return the frame instead of layout

def start():
    app = QApplication([])
    
    window = Window()
    window.show()

    sys.exit(app.exec())


#-------------------------------------------------------------------#
if __name__ == "__main__":
    start()
