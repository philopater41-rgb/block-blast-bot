import time
from kivy.config import Config
Config.set('graphics', 'width', '0')
Config.set('graphics', 'height', '0')

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform

# Bot imports (Assuming they are in the same folder)
import vision
import solver
import numpy as np
import cv2

if platform == 'android':
    from jnius import autoclass, cast
    from android.runnable import run_on_ui_thread

    # Android Classes
    PythonService = autoclass('org.kivy.android.PythonService')
    Context = autoclass('android.content.Context')
    WindowManager = autoclass('android.view.WindowManager')
    LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
    PixelFormat = autoclass('android.graphics.PixelFormat')
    Gravity = autoclass('android.view.Gravity')
    Button = autoclass('android.widget.Button')
    FrameLayout = autoclass('android.widget.FrameLayout')
    Color = autoclass('android.graphics.Color')
    View = autoclass('android.view.View')
    Paint = autoclass('android.graphics.Paint')
    Canvas = autoclass('android.graphics.Canvas')

    service = PythonService.mService
    wm = service.getSystemService(Context.WINDOW_SERVICE)

else:
    # Dummy classes for PC testing
    service = None
    wm = None

class OverlayView:
    def __init__(self):
        self.btn_layout = None
        self.overlay_layout = None
        self.wm = wm
        self.btn_params = None
        self.overlay_params = None
        self.drawing_view = None

    def create_floating_button(self):
        if not self.wm: return

        # Layout Params for the Button (Top-Left, small)
        self.btn_params = LayoutParams(
            200, 200, # Width, Height
            LayoutParams.TYPE_APPLICATION_OVERLAY, # Android 8+
            LayoutParams.FLAG_NOT_FOCUSABLE | LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH,
            PixelFormat.TRANSLUCENT
        )
        self.btn_params.gravity = Gravity.TOP | Gravity.LEFT
        self.btn_params.x = 0
        self.btn_params.y = 200

        # Create Button
        self.btn = Button(service)
        self.btn.setText("SOLVE")
        self.btn.setBackgroundColor(Color.RED)
        self.btn.setTextColor(Color.WHITE)
        self.btn.setOnClickListener(ClickProxy(self.on_solve_click))

        # Add to Window
        self.wm.addView(self.btn, self.btn_params)

    def on_solve_click(self):
        print("Solve Clicked!")
        try:
            # 1. Capture Screen (Local Mode)
            # Try capturing with 'screencap' (requires permission or trickery)
            # OR read latest screenshot
            img = vision.capture_screen(use_adb=False)
            
            if img is None:
                # Fallback: Read latest file in Screenshots folder
                print("Capture failed, trying safe fallback...")
                
                img = self.get_latest_screenshot()
                
                if img is None:
                    print("No screenshot found.")
                    return

            # 2. Parse and Solve
            board = vision.parse_board(img)
            shapes_data = vision.parse_shapes(img)
            shapes = [s[0] for s in shapes_data]
            bboxes = [s[1] for s in shapes_data]
            
            solution = solver.solve(board, shapes)
            
            if solution:
                print("Solution Found!")
                self.draw_solution(solution, bboxes)
            else:
                print("No Solution")

        except Exception as e:
            print(f"Error in solve: {e}")

    def draw_solution(self, solution, bboxes):
        if not self.wm: return

        # Remove previous overlay if exists
        if self.drawing_view:
            self.wm.removeView(self.drawing_view)
            self.drawing_view = None

        # Create full screen transparent overlay
        self.overlay_params = LayoutParams(
            LayoutParams.MATCH_PARENT, 
            LayoutParams.MATCH_PARENT,
            LayoutParams.TYPE_APPLICATION_OVERLAY,
            LayoutParams.FLAG_NOT_FOCUSABLE | LayoutParams.FLAG_NOT_TOUCHABLE, # Let clicks pass through
            PixelFormat.TRANSLUCENT
        )
        
        # Custom View for drawing
        self.drawing_view = CustomDrawingView(service, solution, bboxes)
        self.wm.addView(self.drawing_view, self.overlay_params)

        # Clear overlay after 3 seconds
        Clock.schedule_once(lambda dt: self.clear_overlay(), 3)

    def clear_overlay(self):
        if self.drawing_view and self.wm:
            self.wm.removeView(self.drawing_view)
            self.drawing_view = None

# Java Proxy for Click Listener
if platform == 'android':
    from jnius import PythonJavaClass, java_method

    class ClickProxy(PythonJavaClass):
        __javainterfaces__ = ['android/view/View$OnClickListener']
        def __init__(self, callback):
            super().__init__()
            self.callback = callback
        
        @java_method('(Landroid/view/View;)V')
        def onClick(self, v):
            self.callback()

    class CustomDrawingView(View):
        __javainterfaces__ = ['android/view/View']
        def __init__(self, context, solution, bboxes):
            super().__init__(context)
            self.solution = solution
            self.bboxes = bboxes
            self.paint = Paint()
            self.paint.setStrokeWidth(5)
            self.paint.setStyle(Paint.Style.STROKE)

        @java_method('(Landroid/graphics/Canvas;)V')
        def onDraw(self, canvas):
            # Draw rectangles
            colors = [Color.RED, Color.GREEN, Color.BLUE]
            
            for i, (shape_idx, r, c) in enumerate(self.solution):
                color_int = colors[i % 3]
                self.paint.setColor(color_int)
                
                # Draw Box on Shape (Source)
                if self.bboxes[shape_idx]:
                    bx, by, bw, bh = self.bboxes[shape_idx]
                    canvas.drawRect(float(bx), float(by), float(bx+bw), float(by+bh), self.paint)
                
                # Draw Box on Board (Destination)
                # Use dynamic coordinates from vision module
                board_x = vision.BOARD_X
                board_y = vision.BOARD_Y
                cell_size = vision.CELL_SIZE
                
                dest_x = board_x + (c * cell_size)
                dest_y = board_y + (r * cell_size)
                
                canvas.drawRect(float(dest_x), float(dest_y), 
                                float(dest_x + cell_size), float(dest_y + cell_size), self.paint)

    def get_latest_screenshot(self):
        """Fallback: Find the latest screenshot in common directories."""
        import os
        search_paths = [
            '/sdcard/Pictures/Screenshots/',
            '/sdcard/DCIM/Screenshots/',
            '/sdcard/Screenshots/'
        ]
        
        latest_file = None
        latest_time = 0
        
        for path in search_paths:
            if not os.path.exists(path): continue
            
            for f in os.listdir(path):
                if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    full_path = os.path.join(path, f)
                    try:
                        mtime = os.path.getmtime(full_path)
                        if mtime > latest_time:
                            latest_time = mtime
                            latest_file = full_path
                    except:
                        pass
        
        if latest_file:
            print(f"Found latest screenshot: {latest_file}")
            return cv2.imread(latest_file)
        return None


if __name__ == '__main__':
    if platform == 'android':
        overlay = OverlayView()
        # Run on UI thread to interact with WindowManager
        @run_on_ui_thread
        def start_overlay():
            overlay.create_floating_button()
        
        start_overlay()
        
        # Keep service alive
        while True:
            time.sleep(1)
    else:
        print("This service is designed for Android only.")
