from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QGridLayout, QScrollArea,QFileDialog
from PyQt6.QtGui import QIcon, QPixmap, QFont, QImage
from PyQt6.QtCore import Qt, QSize
import sys, os, cv2

MAIN_ICON = "./assets/icons/main_icon.png"

BG_COLOR = "#121212"
CANVAS_COLOR = "#212121"
SPANEL_COLOR = "#282828"
SPANEL_TXT_COLOR = "#787878"
SPANEL_HEADING_COLOR = "#3d3b3b"

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.zoom_factor = 1.0
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
            "Import": "Import.svg",
            "Select": "Select.svg",
            "Move": "Move.svg",
            "Crop": "Crop.svg",
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
            if name == "Import":
                button.clicked.connect(self.choose_image)

            elif name == "Zoom-in":
                button.clicked.connect(self.zoom_in)
            
            elif name == "Zoom-out":
                button.clicked.connect(self.zoom_out)

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

        self.image_label = QLabel(canvas)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setGeometry(0, 0, 900, 500)
        self.image_label.setScaledContents(False)
        
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
    
    def choose_image(self):
        #open a file dialogue for image selection
        file_dialogue = QFileDialog()
        file_path, _ = file_dialogue.getOpenFileName(self, "Select Image", "", "Images(*.png *.jpg *.jpeg )")

        if file_path:
            print(f"Selected image: {file_path}")
            self.display_image(file_path)
    
    def display_image(self, image_path):
        self.cv_image = cv2.imread(image_path)  
        if self.cv_image is not None:
            self.image_path = image_path  

            self.original_image = self.cv_image.copy()
            self.update_image_display()
        else:
            print("Error in importing the file :<")

    def update_image_display(self):
        """Updates QLabel with the image"""
        if self.cv_image is None:
            return
        
        # Resize the image based on the zoom factor
        height, width = self.cv_image.shape[:2]
        new_width = int(width * self.zoom_factor)
        new_height = int(height * self.zoom_factor)
        
        resized_image = cv2.resize(self.cv_image, (new_width, new_height))
        rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qimage = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)

        self.image_label.setPixmap(pixmap)
        self.image_label.resize(w, h)  
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def zoom_in(self):
        """Zoom in on the image"""
        if self.cv_image is not None:
            self.zoom_factor *= 1.2  # Increase zoom factor
            self.update_image_display()

    def zoom_out(self):
        """Zoom out on the image"""
        if self.cv_image is not None:
            self.zoom_factor /= 1.2  # Decrease zoom factor
            self.update_image_display()


def start():
    app = QApplication([])
    
    window = Window()
    window.show()

    sys.exit(app.exec())


#-------------------------------------------------------------------#
if __name__ == "__main__":
    start()
