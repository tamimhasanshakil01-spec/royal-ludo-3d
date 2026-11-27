from pathlib import Path
import re
p = Path("app/src/main/java/com/example/MainActivity.kt")
s = p.read_text(encoding="utf-8")
imp = "import com.example.game.OnlineGameScreen\\n"
if imp not in s:
    s = s.replace("import com.example.game.LudoViewModel\\n", "import com.example.game.LudoViewModel\\n" + imp)
pattern = r"(\s*AppTab\.PLAY -> \{\s*)PlayGameScreen\(.*?\n\s*\)\n(\s*\})"
replacement = r"""\1OnlineGameScreen(
                                    isBangla = isBangla,
                                    modifier = Modifier.weight(1f)
                                )
\2"""
s, count = re.subn(pattern, replacement, s, count=1, flags=re.S)
if count != 1:
    raise SystemExit("Could not find PLAY tab PlayGameScreen block")
p.write_text(s, encoding="utf-8")
print("Main PLAY tab now opens the Firebase online game screen.")
