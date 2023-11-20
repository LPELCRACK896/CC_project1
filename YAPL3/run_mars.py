import sys
import subprocess
import time
import pygetwindow as gw
import pyautogui

file_path = sys.argv[1]

# Start Mars application
subprocess.Popen(['java', '-jar', 'Mars4_5.jar'])

# Wait for Mars to fully launch
time.sleep(7)

# Find the Mars window and bring it to the foreground
mars_window = gw.getWindowsWithTitle("MARS")[0]
mars_window.activate()

# Use pyautogui to simulate GUI interactions with hotkeys
pyautogui.hotkey('alt', 'f')  # Press Alt+F to open the File menu
time.sleep(1)

pyautogui.press('o')  # Press 'o' to open the Open dialog
time.sleep(1)

pyautogui.write(file_path)  # Type the file path
time.sleep(1)

# Press 'enter' to open the file
pyautogui.press('enter')
time.sleep(1)

# Use pyautogui to simulate GUI interactions with hotkeys
pyautogui.hotkey('alt', 'r')  # Press Alt+R to open the Run menu
time.sleep(1)

pyautogui.press('f3')  # f3 to compile