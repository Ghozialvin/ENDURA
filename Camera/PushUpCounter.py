import cv2
import numpy as np
import PoseModule as pm
from PIL import Image, ImageDraw, ImageFont
import os
import ctypes

def get_screen_size():
    """Get the size of the primary monitor."""
    try:
        if os.name == 'nt':  # Windows
            user32 = ctypes.windll.user32
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            return screen_width, screen_height
        else:  # Try using PIL.ImageGrab for other platforms if available
            try:
                from PIL import ImageGrab
                img = ImageGrab.grab()
                return img.size
            except:
                return 1920, 1080  # Default fallback
    except:
        return 1920, 1080  # Default fallback

def setup_camera():
    """Initializes the video capture object."""
    return cv2.VideoCapture(0)

def get_video_dimensions(cap):
    """Returns the dimensions of the video frame."""
    width = int(cap.get(3))  # CV_CAP_PROP_FRAME_WIDTH is 3
    height = int(cap.get(4))  # CV_CAP_PROP_FRAME_HEIGHT is 4
    return width, height

def calculate_optimal_window_size(video_width, video_height, screen_width, screen_height, scale_factor=0.8):
    """Calculate optimal window size based on screen resolution and video size."""
    # Determine maximum window size that fits on screen with some margin
    max_width = int(screen_width * scale_factor)
    max_height = int(screen_height * scale_factor)
    
    # Maintain aspect ratio
    aspect_ratio = video_width / video_height
    
    if video_width > max_width or video_height > max_height:
        if max_width / aspect_ratio <= max_height:
            # Width limited
            new_width = max_width
            new_height = int(max_width / aspect_ratio)
        else:
            # Height limited
            new_height = max_height
            new_width = int(max_height * aspect_ratio)
    else:
        # If video is small enough, use original size or scale up slightly
        scale_up = min(max_width/video_width, max_height/video_height, 1.5)
        new_width = int(video_width * scale_up)
        new_height = int(video_height * scale_up)
    
    return new_width, new_height

def relative_position(img_width, img_height, x_percent, y_percent):
    """Calculate position relative to image dimensions using percentages."""
    x = int(img_width * (x_percent / 100))
    y = int(img_height * (y_percent / 100))
    return x, y

def update_feedback_and_count(elbow, shoulder, hip, direction, count, form):
    """Determines the feedback message and updates the count based on the angles."""
    feedback = "Fix Form"
    if elbow > 160 and shoulder > 40 and hip > 160:
        form = 1
    if form == 1:
        if elbow <= 90 and hip > 160:
            feedback = "Up"
            if direction == 0:
                count += 0.5
                direction = 1
        elif elbow > 160 and shoulder > 40 and hip > 160:
            feedback = "Down"
            if direction == 1:
                count += 0.5
                direction = 0
        else:
            feedback = "Fix Form"
    return feedback, count, direction, form

def draw_text_with_custom_font(img, text, position, font_path, font_size, color):
    """Draw text with custom font using PIL and merge with OpenCV image."""
    # Convert OpenCV image (BGR) to PIL Image (RGB)
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        # Fallback to default font if custom font not found
        font = ImageFont.load_default()
    
    # Draw text on the PIL image
    draw.text(position, text, font=font, fill=color)
    
    # Convert back to OpenCV image (BGR)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def draw_ui(img, per, bar, count, feedback, form, font_path=None):
    """Draws the UI elements on the image that adapt to the screen size."""
    # Get image dimensions
    img_height, img_width = img.shape[:2]
    
    # Scale font sizes relative to image dimensions
    base_font_size = min(img_width, img_height) / 40
    large_font_size = int(base_font_size * 3)
    medium_font_size = int(base_font_size * 1.5)
    small_font_size = int(base_font_size)
    
    # Define colors
    red_color = (3, 0, 233)  # BGR format of #E90003
    red_color_rgb = (233, 0, 3)  # RGB format for PIL
    white_color = (255, 255, 255)
    dark_overlay = (50, 50, 50)
    
    # Create a slightly transparent overlay for the bottom of the screen
    overlay = img.copy()
    bottom_overlay_height = int(img_height * 0.15)  # 15% of image height
    cv2.rectangle(overlay, 
                 (0, img_height - bottom_overlay_height), 
                 (img_width, img_height), 
                 (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
    
    # Progress bar (only when form is correct)
    if form == 1:
        # Calculate progress bar dimensions relative to screen size
        bar_height = int(img_height * 0.6)  # 60% of image height
        bar_width = max(8, int(img_width * 0.01))  # At least 8px or 1% of width
        
        # Position on right side with some padding
        x_position = img_width - int(img_width * 0.05)
        y_top = int((img_height - bar_height) / 2)
        
        # Background of the bar
        cv2.rectangle(img, 
                     (x_position, y_top), 
                     (x_position + bar_width, y_top + bar_height), 
                     dark_overlay, -1)
        
        # Fill level based on progress
        progress_height = int(bar_height * (per / 100))
        cv2.rectangle(img, 
                     (x_position, y_top + bar_height - progress_height), 
                     (x_position + bar_width, y_top + bar_height), 
                     red_color, -1)
        
        # Position for percentage text
        percent_x = x_position - int(img_width * 0.03)
        percent_y = y_top + bar_height + int(img_height * 0.03)
        
        # Percentage text with custom font if available
        if font_path:
            img = draw_text_with_custom_font(
                img, f'{int(per)}%', 
                (percent_x, percent_y - int(img_height * 0.03)),
                font_path, small_font_size, red_color_rgb
            )
        else:
            cv2.putText(img, f'{int(per)}%', 
                      (percent_x, percent_y), 
                      cv2.FONT_HERSHEY_SIMPLEX, small_font_size / 30, white_color, 2)

    # Counter display positions (bottom left)
    count_x = int(img_width * 0.05)
    count_y = img_height - int(img_height * 0.05)
    reps_x = count_x + int(img_width * 0.1)
    reps_y = count_y
    
    # Counter display with custom font if available
    if font_path:
        img = draw_text_with_custom_font(
            img, str(int(count)), 
            (count_x, count_y - int(img_height * 0.07)),
            font_path, large_font_size, (255, 255, 255)
        )
        img = draw_text_with_custom_font(
            img, "REPS", 
            (reps_x, reps_y - int(img_height * 0.03)),
            font_path, medium_font_size, red_color_rgb
        )
    else:
        cv2.putText(img, str(int(count)), 
                  (count_x, count_y), 
                  cv2.FONT_HERSHEY_SIMPLEX, large_font_size / 30, white_color, 2)
        cv2.putText(img, "REPS", 
                  (reps_x, reps_y), 
                  cv2.FONT_HERSHEY_SIMPLEX, medium_font_size / 30, red_color, 2)
    
    # Top feedback bar
    top_bar_height = int(img_height * 0.08)  # 8% of image height
    cv2.rectangle(img, (0, 0), (img_width, top_bar_height), (0, 0, 0), -1)
    
    # Feedback text position
    feedback_x = int(img_width * 0.5) - int(len(feedback) * img_width * 0.01)
    feedback_y = int(top_bar_height * 0.7)
    
    # Logo position
    logo_x = int(img_width * 0.02)
    logo_y = int(top_bar_height * 0.7)
    
    # Reset button position (top right)
    reset_x = img_width - int(img_width * 0.15)
    reset_y = int(top_bar_height * 0.7)
    
    if font_path:
        img = draw_text_with_custom_font(
            img, feedback, 
            (feedback_x, int(top_bar_height * 0.2)),
            font_path, medium_font_size, red_color_rgb
        )
        
        # Add ENDURA logo
        img = draw_text_with_custom_font(
            img, "ENDURA", 
            (logo_x, int(top_bar_height * 0.2)),
            font_path, medium_font_size, red_color_rgb
        )
        
        # Add reset button text
        img = draw_text_with_custom_font(
            img, "Press 'R' to Reset", 
            (reset_x, int(top_bar_height * 0.2)),
            font_path, small_font_size, red_color_rgb
        )
    else:
        cv2.putText(img, feedback, 
                  (feedback_x, feedback_y), 
                  cv2.FONT_HERSHEY_SIMPLEX, medium_font_size / 30, red_color, 2)
        
        # Add ENDURA logo with OpenCV text
        cv2.putText(img, "ENDURA", 
                  (logo_x, logo_y),
                  cv2.FONT_HERSHEY_SIMPLEX, medium_font_size / 30, red_color, 2)
        
        # Add reset button text with OpenCV
        cv2.putText(img, "Press 'R' to Reset", 
                  (reset_x, reset_y),
                  cv2.FONT_HERSHEY_SIMPLEX, small_font_size / 30, red_color, 2)
    
    return img

def main():
    # Get screen size
    screen_width, screen_height = get_screen_size()
    print(f"Screen dimensions: {screen_width}x{screen_height}")
    
    # Initialize camera
    cap = setup_camera()
    detector = pm.poseDetector()
    count = 0
    direction = 0
    form = 0
    
    # Get video dimensions
    video_width, video_height = get_video_dimensions(cap)
    print(f"Video capture dimensions: {video_width}x{video_height}")
    
    # Calculate optimal window size
    window_width, window_height = calculate_optimal_window_size(
        video_width, video_height, screen_width, screen_height
    )
    print(f"Window size: {window_width}x{window_height}")
    
    # Set window properties
    window_name = 'ENDURA - Push-up Counter'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, window_width, window_height)
    
    # Try to center the window on screen
    if os.name == 'nt':  # Windows
        try:
            x_pos = (screen_width - window_width) // 2
            y_pos = (screen_height - window_height) // 2
            cv2.moveWindow(window_name, x_pos, y_pos)
        except:
            pass  # Ignore if window positioning fails
    
    # Try to find GeForce font - check a few common paths
    font_path = None
    possible_font_paths = [
        "fonts/geforce.ttf",  # Local directory
        "fonts/GeForce-Bold.ttf",
        "C:/Windows/Fonts/geforce.ttf",  # Windows font directory
        os.path.join(os.path.dirname(__file__), "fonts/geforce.ttf"),  # Script directory
    ]
    
    for path in possible_font_paths:
        if os.path.exists(path):
            font_path = path
            print(f"Using GeForce font from: {font_path}")
            break
    
    if not font_path:
        print("GeForce font not found, using default font")

    while cap.isOpened():
        ret, img = cap.read()
        if not ret:
            break
        
        # Process the frame
        img = detector.findPose(img, False)
        lmList = detector.findPosition(img, False)

        if len(lmList) != 0:
            elbow = detector.findAngle(img, 11, 13, 15)
            shoulder = detector.findAngle(img, 13, 11, 23)
            hip = detector.findAngle(img, 11, 23, 25)
            per = np.interp(elbow, (90, 160), (0, 100))
            bar = np.interp(elbow, (90, 160), (380, 50))
            feedback, count, direction, form = update_feedback_and_count(elbow, shoulder, hip, direction, count, form)
            img = draw_ui(img, per, bar, count, feedback, form, font_path)
        else:
            # Still draw minimal UI even if no pose detected
            img = draw_ui(img, 0, 0, count, "Stand in Frame", 0, font_path)
        
        # Resize for display if needed (maintaining aspect ratio)
        display_img = img
        if img.shape[1] != window_width or img.shape[0] != window_height:
            display_img = cv2.resize(img, (window_width, window_height))
        
        cv2.imshow(window_name, display_img)
        key = cv2.waitKey(10) & 0xFF
        
        # Handle key presses
        if key == ord('q'):  # Quit
            break
        elif key == ord('r'):  # Reset counter
            count = 0
            direction = 0
            form = 0
            feedback = "Fix Form"
            print("Counter reset!")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


import cv2
import mediapipe as mp
import numpy as np
import PoseModule as pm



cap = cv2.VideoCapture(0)
detector = pm.poseDetector()
count = 0
direction = 0
form = 0
feedback = "Fix Form"


while cap.isOpened():
    ret, img = cap.read() #640 x 480
    #Determine dimensions of video - Help with creation of box in Line 43
    width  = cap.get(3)  # float `width`
    height = cap.get(4)  # float `height`
    # print(width, height)
    
    img = detector.findPose(img, False)
    lmList = detector.findPosition(img, False)
    # print(lmList)
    if len(lmList) != 0:
        elbow = detector.findAngle(img, 11, 13, 15)
        shoulder = detector.findAngle(img, 13, 11, 23)
        hip = detector.findAngle(img, 11, 23,25)
        
        #Percentage of success of pushup
        per = np.interp(elbow, (90, 160), (0, 100))
        
        #Bar to show Pushup progress
        bar = np.interp(elbow, (90, 160), (380, 50))

        #Check to ensure right form before starting the program
        if elbow > 160 and shoulder > 40 and hip > 160:
            form = 1
    
        #Check for full range of motion for the pushup
        if form == 1:
            if per == 0:
                if elbow <= 90 and hip > 160:
                    feedback = "Up"
                    if direction == 0:
                        count += 0.5
                        direction = 1
                else:
                    feedback = "Fix Form"
                    
            if per == 100:
                if elbow > 160 and shoulder > 40 and hip > 160:
                    feedback = "Down"
                    if direction == 1:
                        count += 0.5
                        direction = 0
                else:
                    feedback = "Fix Form"
                        # form = 0
                
                    
    
        print(count)
        
        #Draw Bar
        if form == 1:
            cv2.rectangle(img, (580, 50), (600, 380), (0, 255, 0), 3)
            cv2.rectangle(img, (580, int(bar)), (600, 380), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(per)}%', (565, 430), cv2.FONT_HERSHEY_PLAIN, 2,
                        (255, 0, 0), 2)


        #Pushup counter
        cv2.rectangle(img, (0, 380), (100, 480), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(int(count)), (25, 455), cv2.FONT_HERSHEY_PLAIN, 5,
                    (255, 0, 0), 5)
        
        #Feedback 
        cv2.rectangle(img, (500, 0), (640, 40), (255, 255, 255), cv2.FILLED)
        cv2.putText(img, feedback, (500, 40 ), cv2.FONT_HERSHEY_PLAIN, 2,
                    (0, 255, 0), 2)

        
    cv2.imshow('Pushup counter', img)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()