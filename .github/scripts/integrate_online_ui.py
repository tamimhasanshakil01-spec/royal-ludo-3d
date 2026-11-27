from pathlib import Path
import re
p = Path("app/src/main/java/com/example/MainActivity.kt")
s = p.read_text(encoding="utf-8")
imp = "import com.example.game.OnlineGameScreen\n"
if imp not in s:
    s = s.replace("import com.example.game.LudoViewModel\n", "import com.example.game.LudoViewModel\n" + imp)
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

# Normalize the online lobby branch after extracting the base project. This keeps
# the generated Android source buildable even when the source ZIP contains the
# earlier malformed brace layout.
screen = Path("app/src/main/java/com/example/game/OnlineGameScreen.kt")
if screen.exists():
    content = screen.read_text(encoding="utf-8")
    start = content.find("        if (roomId.isBlank()) {")
    marker = "        } else {"
    end = content.find(marker, start + 1) if start >= 0 else -1
    if start >= 0 and end >= 0:
        lobby = """        if (roomId.isBlank()) {
            Card(Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(if (isBangla) "অনলাইন ম্যাচ শুরু করুন" else "Start an online match", style = MaterialTheme.typography.titleLarge)
                    Button(
                        onClick = {
                            repo.ensureSignedIn().addOnCompleteListener { auth ->
                                if (auth.isSuccessful) {
                                    handle(repo.createBotRoom()) { result ->
                                        roomId = result["roomId"].toString()
                                        message = if (isBangla) "বট ম্যাচ তৈরি হয়েছে" else "Bot match created"
                                    }
                                } else {
                                    error = auth.exception?.localizedMessage ?: "Sign-in failed"
                                }
                            }
                        },
                        enabled = !busy && uid != null,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(if (isBangla) "সার্ভার বটের সাথে খেলুন" else "Play server bot")
                    }
                }
            }
        } else {"""
        content = content[:start] + lobby + content[end + len(marker):]
        screen.write_text(content, encoding="utf-8")
        print("Normalized online game lobby Kotlin braces.")
