"""Ad-hoc smoke test for a Windows toast notification when a token is bought."""
import time

from wintoast import ToastNotifier

toaster = ToastNotifier()

toaster.show_toast(
    "Token has been bought",
    "New list bot",
    # icon_path=r"assets/icons/y.ico",
    duration=5,
    threaded=True,
)

while toaster.notification_active():
    time.sleep(0.1)
