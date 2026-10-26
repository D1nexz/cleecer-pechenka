import os
import platform
import sys
import time
from datetime import datetime

IS_WINDOWS = (sys.platform == 'win32')

# =====================================================================
# Кроссплатформенная настройка DPI / графической среды
# =====================================================================
if IS_WINDOWS:
    import ctypes

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass
else:
    print(f"Платформа: {platform.system()} ({sys.platform}) — "
          "настройка DPI Windows пропущена (это нормально).")
    if 'WAYLAND_DISPLAY' in os.environ and 'DISPLAY' not in os.environ:
        print("ПРЕДУПРЕЖДЕНИЕ: обнаружена Wayland-сессия — pyautogui/mss "
              "не смогут делать скриншоты. Войдите как X11 (Xorg).")

import cv2
import numpy as np

# Скриншоты: предпочитаем mss (не требует scrot на Linux), иначе pyautogui.
try:
    import mss
    import mss.tools as mss_tools

    _MSS = mss.mss()
    USE_MSS = len(_MSS.monitors) > 1
except Exception:
    _MSS = None
    USE_MSS = False

# Папка для сохранения скриншотов (рядом со скриптом)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
save_dir = os.path.join(BASE_DIR, "screenshots")
os.makedirs(save_dir, exist_ok=True)

print("Начинаю делать скриншоты каждые 5 секунд...")
print("Нажмите Ctrl+C для остановки\n")

count = 0

def _make_screenshot():
    """Единая функция скриншота — через mss (быстрее) или pyautogui."""
    if USE_MSS:
        sct = _MSS
        monitor = sct.monitors[1]  # главный монитор
        img = sct.grab(monitor)
        arr = np.frombuffer(img.rgb, dtype=np.uint8).reshape(
            (monitor["height"], monitor["width"], 3))
        frame = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        return frame
    import pyautogui
    return np.array(pyautogui.screenshot())  # RGB

try:
    while True:
        # Делаем скриншот
        frame = _make_screenshot()

        # Формируем имя файла с датой и временем
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(save_dir, f"screenshot_{timestamp}.png")

        # cv2.imwrite() ждёт BGR.
        #   mss -> BGR (уже)
        #   pyautogui -> RGB (нужна конвертация)
        if USE_MSS:
            cv2.imwrite(filename, frame)
        else:
            cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        count += 1
        print(f"[{count}] Сохранено: {filename}")

        # Ждём 5 секунд
        time.sleep(5)

except KeyboardInterrupt:
    print(f"\nОстановлено. Всего сделано скриншотов: {count}")