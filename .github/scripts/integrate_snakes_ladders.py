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
p.write_text(s, encoding="utf-8")
print("PLAY tab now contains Ludo / Snakes & Ladders selector.")
