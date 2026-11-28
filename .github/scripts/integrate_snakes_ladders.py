from pathlib import Path
p = Path("app/src/main/java/com/example/MainActivity.kt")
s = p.read_text(encoding="utf-8")
old = """                                OnlineGameScreen(
                                    isBangla = isBangla,
                                    modifier = Modifier.weight(1f)
                                )"""
new = """                                RoyalGameHub(
                                    isBangla = isBangla,
                                    modifier = Modifier.weight(1f)
                                )"""
if old in s:
    s = s.replace(old, new, 1)
elif "RoyalGameHub(" not in s:
    raise SystemExit("Could not locate PLAY screen route; refusing unsafe patch")
imp = "import com.example.game.RoyalGameHub"
if imp not in s:
    marker = "import com.example.game.OnlineGameScreen"
    if marker in s: s = s.replace(marker, marker + "\\n" + imp)
    else: s = s.replace("package com.example\\n", "package com.example\\n\\n" + imp + "\\n", 1)
p.write_text(s, encoding="utf-8")
print("PLAY tab now contains Ludo / Snakes & Ladders selector.")
