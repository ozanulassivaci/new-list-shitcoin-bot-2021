"""Ad-hoc smoke test for reading a contract address off the clipboard."""
import pyperclip as pc

text = pc.paste()
print(text)
