"""
Checks bot/seller.py's exit-rule decision logic against the two cases it
was designed around (see docs/ALGORITHM.md#the-exit-rule): a fluctuating
uptrend should not trigger a sell, but a confirmed reversal from a peak
should. Runs without selenium/a browser, since Seller._is_downtrend is
plain Python.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bot"))

from seller import Seller

# fluctuating but still trending up overall -- should NOT sell
uptrend = [10, 20, 30, 40, 50, 60, 70, 80, 90, 70, 60, 80, 90, 100]
assert Seller._is_downtrend(uptrend) is False

# peaked at +170%, then 160 -> 150 -> 140 -> falling -- should sell
peaked_and_falling = [100, 140, 170, 160, 150, 140]
assert Seller._is_downtrend(peaked_and_falling) is True

# a short dip (like the 90 -> 70 -> 60 blip in the uptrend above) should
# not be enough on its own
short_dip = [50, 60, 90, 70, 60]
assert Seller._is_downtrend(short_dip) is False

# not enough history yet
assert Seller._is_downtrend([100, 90]) is False

print("all seller._is_downtrend cases passed")
