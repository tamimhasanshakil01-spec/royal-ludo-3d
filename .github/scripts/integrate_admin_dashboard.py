from pathlib import Path
import re

p = Path("app/src/main/java/com/example/MainActivity.kt")
s = p.read_text(encoding="utf-8")
nl = chr(10)

if "import com.example.game.AdminDashboardScreen" not in s:
    match = re.search(r"^import com\\.example\\.game\\.OnlineGameScreen$", s, re.M)
    if not match:
        raise SystemExit("Admin integration stopped: OnlineGameScreen import not found.")
    s = s[:match.end()] + nl + "import com.example.game.AdminDashboardScreen" + s[match.end():]

if "var showAdminPanel by rememberSaveable" not in s:
    m = re.search(r"^([ \\t]*)var activeTab by rememberSaveable[^\\n]*$", s, re.M)
    if not m:
        raise SystemExit("Admin integration stopped: activeTab state not found.")
    indent = m.group(1)
    s = s[:m.end()] + nl + indent + "var showAdminPanel by rememberSaveable { mutableStateOf(false) }" + s[m.end():]

if "onAdmin = { showAdminPanel = true }" not in s:
    pattern = r"(?m)^(\\s*)AppTab\\.WALLET -> \\{\\s*\\n\\1    RoyalWalletScreen\\("
    repl = r"\\1AppTab.WALLET -> {\\n\\1    if (showAdminPanel) {\\n\\1        AdminDashboardScreen(isBangla = isBangla, onBack = { showAdminPanel = false }, modifier = Modifier.weight(1f))\\n\\1    } else {\\n\\1        RoyalWalletScreen("
    s, count = re.subn(pattern, repl, s, count=1)
    if count != 1:
        raise SystemExit("Admin integration stopped: Wallet tab branch not found.")
    s = s.replace(
        "                                    isBangla = isBangla,\\n                                    onDeposit = {",
        "                                    isBangla = isBangla,\\n                                    onAdmin = { showAdminPanel = true },\\n                                    onDeposit = {",
        1
    )
    close = r"(?m)^(\\s*)\\)\\n(\\s*)\\}\\n(\\s*)AppTab\\."
    m = re.search(close, s)
    # Add the closing brace for the new else immediately before the Wallet branch closes.
    wallet_start = s.index("AppTab.WALLET -> {")
    next_tab = s.find("AppTab.", wallet_start + 10)
    if next_tab < 0:
        raise SystemExit("Admin integration stopped: next navigation branch not found.")
    wallet_segment = s[wallet_start:next_tab]
    tail = re.search(r"(?m)^(\\s*)\\}\\s*$", wallet_segment.rstrip())
    if not tail:
        raise SystemExit("Admin integration stopped: Wallet branch closing brace not found.")
    absolute = wallet_start + tail.start()
    s = s[:absolute] + "                                }" + nl + s[absolute:]

sig = """private fun RoyalWalletScreen(
    isBangla: Boolean,
    onDeposit: () -> Unit,"""
if sig in s:
    s = s.replace(sig, """private fun RoyalWalletScreen(
    isBangla: Boolean,
    onAdmin: () -> Unit,
    onDeposit: () -> Unit,""", 1)

wallet_actions = """        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
            Button(
                onClick = onDeposit,"""
if "onClick = onAdmin" not in s:
    if wallet_actions not in s:
        raise SystemExit("Admin integration stopped: wallet actions not found.")
    s = s.replace(wallet_actions, """        OutlinedButton(
            onClick = onAdmin,
            modifier = Modifier.fillMaxWidth().height(48.dp),
            shape = RoundedCornerShape(14.dp)
        ) { Text(if (isBangla) "⚙ অ্যাডমিন প্যানেল" else "⚙ Admin Panel", color = RoyalGold) }
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
            Button(
                onClick = onDeposit,""", 1)

p.write_text(s, encoding="utf-8")
print("Admin panel integrated into Wallet tab.")
