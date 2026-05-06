import win32gui
import win32ui
import win32con
import win32api
import ctypes
import numpy as np
import cv2
import os
import time

class GameControl:
    def __init__(self, window_title):
        self.hwnd = win32gui.FindWindow(None, window_title)
        
        if not self.hwnd:
            print(f"Exact match failed for '{window_title}'. Trying partial match...")
            hwnd_list = []
            def enum_handler(hwnd, ctx):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if window_title in title:
                        hwnd_list.append(hwnd)
            
            win32gui.EnumWindows(enum_handler, None)
            
            if hwnd_list:
                self.hwnd = hwnd_list[0]
                print(f"Found window by partial match: '{win32gui.GetWindowText(self.hwnd)}'")

        if not self.hwnd:
            print("Available visible windows:")
            def print_window(hwnd, ctx):
                if win32gui.IsWindowVisible(hwnd):
                    t = win32gui.GetWindowText(hwnd)
                    if t:
                        print(f" - {t}")
            win32gui.EnumWindows(print_window, None)
            raise Exception(f"Window not found: {window_title}")
        
        print(f"Connected to window: {window_title} (HWND: {self.hwnd})")

    def background_screenshot(self):
        """
        Captures a screenshot of the window even if it's in the background.
        Returns a numpy array (OpenCV image).
        """
        if not win32gui.IsWindow(self.hwnd):
            raise Exception("ไม่พบหน้าต่างเกม (Window closed)")

        if win32gui.IsIconic(self.hwnd):
            raise Exception("หน้าต่างเกมถูกพับอยู่ (Window minimized)")

        # Get window dimensions
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        width = right - left
        height = bottom - top

        # Create device contexts
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()

        # Create bitmap object
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
        cDC.SelectObject(dataBitMap)

        # Copy window content to bitmap
        # PrintWindow is often better for background windows than BitBlt
        try:
            result = ctypes.windll.user32.PrintWindow(self.hwnd, cDC.GetSafeHdc(), 2)
        except Exception:
            result = 0
        
        if result == 0:
            # Fallback to BitBlt if PrintWindow fails
            cDC.BitBlt((0, 0), (width, height), dcObj, (0, 0), win32con.SRCCOPY)

        # Convert to numpy array
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')
        img.shape = (height, width, 4) # BGRA

        # Cleanup
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # Drop alpha channel and return
        return img[..., :3]

    def find_image(self, template_path, threshold=0.8):
        """
        Finds the template image on the screen.
        Returns (x, y) center coordinates if found, else None.
        """
        if not os.path.exists(template_path):
            print(f"Template not found: {template_path}")
            return None

        # Load template
        template = cv2.imread(template_path)
        if template is None:
            return None

        # Capture screen
        screen = self.background_screenshot()
        
        # Convert to BGR if necessary (OpenCV uses BGR)
        # Note: background_screenshot returns BGRA or BGR depending on processing
        # Let's ensure both are compatible.
        
        # Match template
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            # Calculate center
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y)
        
        return None

    def click(self, x, y):
        """
        Sends a click to the specific coordinates.
        Uses foreground method for reliable clicking.
        """
        # Get window position
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        
        # Bring window to foreground
        win32gui.SetForegroundWindow(self.hwnd)
        time.sleep(0.1)
        
        # Move cursor to target position (screen coordinates)
        screen_x = left + x
        screen_y = top + y
        win32api.SetCursorPos((screen_x, screen_y))
        time.sleep(0.05)
        
        # Perform click
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        
        print(f"Clicked at ({x}, {y}) -> screen ({screen_x}, {screen_y})")

    def background_click(self, x, y):
        """
        Sends a background click to the specific coordinates.
        Does not move the mouse cursor.
        """
        # Ensure coordinates are integers
        x, y = int(x), int(y)
        
        # Convert Window-relative coordinates (from find_image) to Client-relative coordinates
        # find_image uses GetWindowDC which includes borders/title bar
        # PostMessage expects Client coordinates (excluding borders/title bar)
        try:
            # Get Window Rect (Screen coords)
            window_rect = win32gui.GetWindowRect(self.hwnd) # (left, top, right, bottom)
            
            # Calculate Screen coordinates of the click
            screen_x = window_rect[0] + x
            screen_y = window_rect[1] + y
            
            # Convert Screen coordinates to Client coordinates
            client_point = win32gui.ScreenToClient(self.hwnd, (int(screen_x), int(screen_y)))
            client_x, client_y = client_point
            
            print(f"Coords: Window({x}, {y}) -> Screen({screen_x}, {screen_y}) -> Client({client_x}, {client_y})")
        except Exception as e:
            print(f"Coordinate conversion failed: {e}")
            client_x, client_y = x, y

        # Create lParam for coordinates
        # Low word is x, High word is y
        lParam = win32api.MAKELONG(client_x, client_y)
        
        # Send mouse down and up messages
        win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        time.sleep(0.05)
        win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, lParam)
        
        print(f"Background clicked at Client({client_x}, {client_y})")
