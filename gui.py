from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QFileDialog, QSlider,QInputDialog
from PyQt6.QtGui import QIcon, QPixmap, QFont, QImage, QMouseEvent, QKeyEvent
from PyQt6.QtCore import Qt, QSize, QPoint
import sys, os
import numpy as np
import cv2

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

        self.image_selected = False
        self.dragging = False
        self.image_pos = QPoint(0,0)
        self.last_mouse_pos = QPoint(0,0)

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
            "Export": "Export.svg",
            "Brush": "Brush.svg",
            "Select": "Select.svg",
            "Rotate": "Rotate.svg",
            "Crop": "Crop.svg",
            "Zoom-in": "Zoom-in.svg",
            "Zoom-out": "Zoom-out.svg",
            "Trash": "Trash.svg"
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

            elif name == "Export":
                button.clicked.connect(self.export_image)

            elif name == "Select":
                button.clicked.connect(self.enable_selection)

            elif name == "Rotate":
                button.clicked.connect(self.rotate_image)

            elif name == "Crop":
                button.clicked.connect(self.start_crop)

            elif name == "Zoom-in":
                button.clicked.connect(self.zoom_in)
            
            elif name == "Zoom-out":
                button.clicked.connect(self.zoom_out)
            
            elif name == "Trash":
                button.clicked.connect(self.clear_canvas)
            
            elif name == "Export":
                button.clicked.connect(self.export_image)

            elif name == "Crop":
                button.clicked.connect(self.start_crop)
            
            elif name == "Brush":
                button.clicked.connect(self.enable_brush)


            toolbar_layout.addWidget(button)

        toolbar_widget.setLayout(toolbar_layout)  # Set layout inside widget
        return toolbar_widget  # Return wrapped toolbar


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

    # ----------------- Side Panel ------------------------ 
    def create_side_panel(self):
        side_panel_frame = QFrame()
        side_panel_frame.setStyleSheet(f"background-color: {CANVAS_COLOR}; border-radius: 8px;")
        side_panel_frame.setFixedWidth(220)
        
        side_layout = QVBoxLayout(side_panel_frame)  
        side_layout.setSpacing(10)
        side_layout.setContentsMargins(10, 10, 10, 10)

        # -------- Blending Section --------
        blending_layout = QVBoxLayout()

        blending_label = QLabel("Blending")
        blending_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        blending_label.setStyleSheet(f"color: {SPANEL_HEADING_COLOR};")
        blending_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
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
                    background-color: rgba(255, 255, 255, 0.1);  
                    border-radius: 5px;
                }
            """)
            btn.clicked.connect(lambda checked, opt=option: self.adjust_blending(opt))  # Connect to adjust_blending method
            blending_box_layout.addWidget(btn)

            # Add a slider below each button
            if option == "Hue":
                self.hue_slider = QSlider(Qt.Orientation.Horizontal)
                self.hue_slider.setRange(0, 360)  # Hue ranges from 0 to 360 degrees
                self.hue_slider.setValue(0)  # Default value
                self.hue_slider.setVisible(False)  # Initially hidden
                self.hue_slider.valueChanged.connect(self.update_hue)  # Connect to update_hue method
                blending_box_layout.addWidget(self.hue_slider)

            elif option == "Saturation":
                self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
                self.saturation_slider.setRange(0, 200)  # Saturation ranges from 0% to 200%
                self.saturation_slider.setValue(100)  # Default value (100% saturation)
                self.saturation_slider.setVisible(False)  # Initially hidden
                self.saturation_slider.valueChanged.connect(self.update_saturation)  # Connect to update_saturation method
                blending_box_layout.addWidget(self.saturation_slider)
            
            elif option == "Luminosity":
                self.luminosity_slider = QSlider(Qt.Orientation.Horizontal)
                self.luminosity_slider.setRange(0, 200)  # Luminosity ranges from 0% to 200%
                self.luminosity_slider.setValue(100)  # Default value (100% luminosity)
                self.luminosity_slider.setVisible(False)  # Initially hidden
                self.luminosity_slider.valueChanged.connect(self.update_luminosity)  # Connect to update_luminosity method
                blending_box_layout.addWidget(self.luminosity_slider)

        blending_layout.addWidget(blending_box)

        # Add stretch below the blending box to push it towards center
        blending_layout.addStretch(2)  

        # -------- Adding to Side Panel Layout --------
        side_layout.addLayout(blending_layout)

        return side_panel_frame

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

            # Enable selection by clicking on the image
            self.image_label.mousePressEvent = self.select_image
            self.image_label.mouseMoveEvent = self.move_image
            self.image_label.mouseReleaseEvent = self.stop_moving

            # Enable deselection when clicking outside the image
            self.canvas.mousePressEvent = self.deselect_image


    def update_image_display(self, image = None):
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


        if self.image_selected:
            self.image_label.setStyleSheet("border: 3px solid #6B679C;")  # Green border
        else:
            self.image_label.setStyleSheet("border: none;")


    def enable_brush(self):
        """Activates brush mode and asks user for brush settings"""
        print("Brush Mode Enabled")

        # Disable other tools
        self.is_cropping = False
        self.is_moving = False
        self.is_drawing = False  # Ensure brush is reset

        # Ask for brush color
        color, ok = QInputDialog.getText(self, "Brush Color", "Enter Hex Color Code (#RRGGBB):")
        if not ok or not color.startswith("#") or len(color) != 7:
            print("Invalid color! Defaulting to blue.")
            color = "#0000FF"  # Default to blue if input is invalid

        # Ask for brush size
        size, ok = QInputDialog.getInt(self, "Brush Size", "Enter Brush Size:", min=1, max=50)
        if not ok:
            print("Invalid size! Defaulting to 3px.")
            size = 3  # Default size if input is invalid

        # Convert hex color to BGR (OpenCV format)
        self.brush_color = tuple(int(color[i:i+2], 16) for i in (5, 3, 1))  # Convert hex to BGR
        self.brush_size = size

        # Enable drawing mode
        self.is_drawing = True

        # Assign drawing events
        self.image_label.mousePressEvent = self.start_drawing
        self.image_label.mouseMoveEvent = self.draw
        self.image_label.mouseReleaseEvent = self.stop_drawing


    def start_drawing(self, event):
        """Starts drawing on the image"""
        if self.is_drawing and event.button() == Qt.MouseButton.LeftButton:
            self.last_point = event.pos()


    def draw(self, event):
        """Draws on the image with the brush"""
        if self.is_drawing and self.last_point is not None:
            if self.cv_image is None:
                return

            img_height, img_width = self.cv_image.shape[:2]
            label_width = self.image_label.width()
            label_height = self.image_label.height()

            scale_x = img_width / label_width
            scale_y = img_height / label_height

            x1 = int(self.last_point.x() * scale_x)
            y1 = int(self.last_point.y() * scale_y)
            x2 = int(event.pos().x() * scale_x)
            y2 = int(event.pos().y() * scale_y)

            cv2.line(self.cv_image, (x1, y1), (x2, y2), self.brush_color, self.brush_size)  # Brush color: Blue, Thickness: 3px
            
            self.last_point = event.pos()  # Update last position
            self.update_image_display()  # Refresh image display

    def stop_drawing(self, event):
        """Stops drawing when the mouse is released"""
        if self.is_drawing:
            self.last_point = None

    
    def enable_selection(self):
        """Activates selection mode and disables other tools"""
        print("Selection Mode Enabled")

        # Disable brush mode
        self.is_drawing = False

        self.image_selected = True
        self.update_image_display()

        # Assign movement-related events to the image label
        self.image_label.mousePressEvent = self.select_image
        self.image_label.mouseMoveEvent = self.move_image
        self.image_label.mouseReleaseEvent = self.stop_moving

    def select_image(self, event):
        """Selects the image and enables movement"""
        if self.image_selected:
            self.dragging = True
            self.last_mouse_pos = event.pos()  # Store initial mouse position
            print("Image Selected for Movement")

    def deselect_image(self, event):
        """Deselects the image when clicking outside it"""
        print("Image Deselected")
        self.image_selected = False
        self.dragging = False
        self.update_image_display()

    def move_image(self, event: QMouseEvent):
        """Moves the image when dragging"""
        if self.dragging:
            new_pos = event.pos() - self.last_mouse_pos
            self.image_pos += new_pos  # Update image position
            self.image_label.move(self.image_pos)  # Move QLabel
            self.last_mouse_pos = event.pos() 

    def stop_moving(self, event):
        """Stops moving the image when mouse is released"""
        if self.dragging:
            self.dragging = False
            print("Stopped Moving Image")

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

    def clear_canvas(self):
        """Clear the canvas and reset the image label"""
        self.cv_image = None  # Clear the current image
        self.zoom_factor = 1.0  # Reset zoom factor
        self.image_label.clear()  # Clear the image label

    def export_image(self):
        """Open a file dialog to save the modified image"""
        if self.cv_image is None:
            print("No image to export.")
            return  # Exit if there is no image to export

        # Open a file dialog to choose the save location
        file_dialogue = QFileDialog()
        file_path, _ = file_dialogue.getSaveFileName(self, "Save Image", "", "Images (*.png *.jpg *.jpeg)")

        if file_path:
            # Save the current image to the chosen file path
            success = cv2.imwrite(file_path, self.cv_image)
            if success:
                print(f"Image saved successfully at: {file_path}")
            else:
                print("Error saving the image.")

    def start_crop(self):
        """Implementing crop"""
        self.is_cropping = True
        self.start_point = None
        self.end_point = None
        self.image_label.setCursor(Qt.CursorShape.CrossCursor)
        self.image_label.mousePressEvent = self.mouse_press_event
        self.image_label.mouseMoveEvent = self.mouse_move_event
        self.image_label.mouseReleaseEvent = self.mouse_release_event


    def mouse_press_event(self, event):
        """Get the starting coordinates of the mouse"""
        if event.button() == Qt.MouseButton.LeftButton and self.is_cropping:
            self.start_point = event.pos()
            self.end_point = event.pos() 

    def mouse_move_event(self, event):
        """Updates the end point of mouse while dragging"""
        if self.is_cropping and self.start_point is not None:
            self.end_point = event.pos()
            self.update_crop_rectangle()

    def mouse_release_event(self, event):
        """Finalizez the crop selection"""
        if event.button() == Qt.MouseButton.LeftButton and self.is_cropping:
            self.is_cropping = False
            self.crop_image()
            self.image_label.setCursor(Qt.CursorShape.ArrowCursor)
            self.image_label.mousePressEvent = None
            self.image_label.mouseMoveEvent = None
            self.image_label.mouseReleaseEvent = None

    def crop_image(self):
        """Crops the selected area from the image"""
        if self.start_point and self.end_point:

            if not hasattr(self, "original_image") or self.original_image is None:
                print("Error: No original image to crop from!")
                return

            label_width = self.image_label.width()
            label_height = self.image_label.height()
            img_height, img_width = self.cv_image.shape[:2]


            scale_x = img_width / label_width
            scale_y = img_height / label_height

            x1 = int(round(min(self.start_point.x(), self.end_point.x()) * scale_x))
            y1 = int(round(min(self.start_point.y(), self.end_point.y()) * scale_y))
            x2 = int(round(max(self.start_point.x(), self.end_point.x()) * scale_x))
            y2 = int(round(max(self.start_point.y(), self.end_point.y()) * scale_y))
            
            # Ensure the coordinates are within the image bounds
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(img_width, x2)
            y2 = min(img_height, y2)

            # Crop the image
            self.cv_image = self.original_image[y1:y2, x1:x2].copy()
            self.update_image_display()
            
            self.is_cropping = False
            self.start_point = None
            self.end_point = None

            self.image_label.setCursor(Qt.CursorShape.ArrowCursor)
            self.image_label.mousePressEvent = self.select_image
            self.image_label.mouseMoveEvent = self.move_image
            self.image_label.mouseReleaseEvent = self.stop_moving

    def update_crop_rectangle(self):
        if self.start_point and self.end_point:

            temp_image = self.cv_image.copy()

            label_width = self.image_label.width()
            label_height = self.image_label.height()
            img_height, img_width = self.cv_image.shape[:2]

            scale_x = img_width / label_width
            scale_y = img_height / label_height

            """Get the coordinates for the rectangle"""
            x1 = int(min(self.start_point.x(), self.end_point.x()) * scale_x)
            y1 = int(min(self.start_point.y(), self.end_point.y()) * scale_y)
            x2 = int(max(self.start_point.x(), self.end_point.x()) * scale_x)
            y2 = int(max(self.start_point.y(), self.end_point.y()) * scale_y)

            cv2.rectangle(temp_image, (x1, y1), (x2, y2), (0, 255, 255), 2)  # White rectangle
        
            self.update_image_display(temp_image)


    def adjust_blending(self, option):
        """Show the slider for adjusting the selected blending option"""
        if option == "Hue":
            self.hue_slider.setVisible(True)  # Show the hue slider
            self.saturation_slider.setVisible(False)  # Hide the saturation slider
            self.luminosity_slider.setVisible(False)  # Hide the luminosity slider
        elif option == "Saturation":
            self.saturation_slider.setVisible(True)  # Show the saturation slider
            self.hue_slider.setVisible(False)  # Hide the hue slider
            self.luminosity_slider.setVisible(False)  # Hide the luminosity slider
        elif option == "Luminosity":
            self.luminosity_slider.setVisible(True)  # Show the luminosity slider
            self.hue_slider.setVisible(False)  # Hide the hue slider
            self.saturation_slider.setVisible(False)  # Hide the saturation slider

    def update_hue(self):
        """Update the image hue based on the slider value"""
        if self.cv_image is not None:
            hue_value = self.hue_slider.value()  # Get the current value of the slider

            hue_shift = hue_value % 100
            # Convert the image to HSV
            hsv_image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2HSV)
            # Adjust the hue
            hsv_image[:, :, 0] = (hsv_image[:, :, 0] + hue_shift) % 100  # OpenCV uses 0-179 for hue
            # Convert back to BGR
            self.cv_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
            self.update_image_display()  # Update the displayed image

    def update_saturation(self):
        """Update the image saturation based on the slider value"""
        if self.cv_image is not None:
            saturation_value = self.saturation_slider.value() / 100.0  # Get the current value of the slider (0.0 to 2.0)

            # Convert the image to HSV
            hsv_image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2HSV)
            # Adjust the saturation
            hsv_image[:, :, 1] = np.clip(hsv_image[:, :, 1] * saturation_value, 0, 255)  # OpenCV uses 0-255 for saturation
            # Convert back to BGR
            self.cv_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
            self.update_image_display()  # Update the displayed image

    def update_luminosity(self):
        """Update the image luminosity based on the slider value"""
        if self.cv_image is not None:
            luminosity_value = self.luminosity_slider.value() / 100.0  # Get the current value of the slider (0.0 to 2.0)

            # Convert the image to HSV
            hsv_image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2HSV)
            # Adjust the luminosity (V channel in HSV)
            hsv_image[:, :, 2] = np.clip(hsv_image[:, :, 2] * luminosity_value, 0, 255)  # OpenCV uses 0-255 for value
            # Convert back to BGR
            self.cv_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
            self.update_image_display()  # Update the displayed image
    
    def rotate_image(self):
        """Rotates the image by a user-defined angle."""
        if self.cv_image is not None:
            # Create input dialog for rotation angle
            dialog = QInputDialog(self)
            dialog.setWindowTitle("Rotate Image")
            dialog.setLabelText("Enter rotation angle (degrees):")
            dialog.setStyleSheet("QWidget { background-color: white; }")  # Set text box color to white

            angle, ok = dialog.getInt(self, "Rotate Image", "Enter rotation angle (degrees):", 0, -360, 360, 1)

            if ok:  # Check if the user clicked OK
            # Rotate the image
                self.cv_image = self.rotate_image_by_angle(self.cv_image, angle)
                self.update_image_display()
                print(f"Image Rotated by {angle} degrees")

    def rotate_image_by_angle(self, image, angle):
        """Rotates the image by the specified angle."""
        # Get the image dimensions
        (h, w) = image.shape[:2]
        # Calculate the center of the image
        center = (w // 2, h // 2)
        # Create the rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        # Perform the rotation
        rotated_image = cv2.warpAffine(image, M, (w, h))
        return rotated_image

def start():
    app = QApplication([])
    
    window = Window()
    window.show()

    sys.exit(app.exec())

#-------------------------------------------------------------------#
if __name__ == "__main__":
    start()
