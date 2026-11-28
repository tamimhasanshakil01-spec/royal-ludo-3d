from pathlib import Path

p = Path("app/src/main/java/com/example/MainActivity.kt")
s = p.read_text(encoding="utf-8")
nl = chr(10)

if "import com.example.game.AdminDashboardScreen" not in s:
    anchor = "import com.example.game.OnlineGameScreen"
    if anchor not in s:
        raise SystemExit("Admin integration stopped: online game import not found.")
    s = s.replace(anchor, anchor + nl + "import com.example.game.AdminDashboardScreen", 1)

call = "                                RoyalWalletScreen(" + nl + "                                    onDeposit = {"
if call in s:
    s = s.replace(call, "                                RoyalWalletScreen(" + nl + "                                    isBangla = isBangla," + nl + "                                    onDeposit = {", 1)

signature = nl.join(["private fun RoyalWalletScreen(", "    onDeposit: () -> Unit,"])
signature_new = nl.join(["private fun RoyalWalletScreen(", "    isBangla: Boolean,", "    onDeposit: () -> Unit,"])
if signature in s:
    s = s.replace(signature, signature_new, 1)

start = s.find("private fun RoyalWalletScreen(")
if start < 0:
    raise SystemExit("Admin integration stopped: generated RoyalWalletScreen not found.")
body_open = s.find(") {", start)
if body_open < 0:
    raise SystemExit("Admin integration stopped: wallet function body not found.")
body_open += 3

if "var showAdminPanel by rememberSaveable" not in s[start:]:
    wrapper = nl + "    var showAdminPanel by rememberSaveable { mutableStateOf(false) }" + nl + "    if (showAdminPanel) {" + nl + "        AdminDashboardScreen(isBangla = isBangla, onBack = { showAdminPanel = false }, modifier = modifier)" + nl + "    } else {"
    s = s[:body_open] + wrapper + s[body_open:]

if "showAdminPanel = true" not in s[start:]:
    title_pos = s.find("Text(", body_open)
    if title_pos < 0:
        raise SystemExit("Admin integration stopped: wallet heading not found.")
    line_end = s.find(nl, title_pos)
    if line_end < 0:
        raise SystemExit("Admin integration stopped: wallet heading line end not found.")
    button = nl.join([
        "        OutlinedButton(",
        "            onClick = { showAdminPanel = true },",
        "            modifier = Modifier.fillMaxWidth().height(46.dp),",
        "            shape = RoundedCornerShape(14.dp)",
        "        ) { Text(if (isBangla) \"⚙ অ্যাডমিন প্যানেল\" else \"⚙ Admin Panel\", color = RoyalGold) }"
    ])
    s = s[:line_end + 1] + button + nl + s[line_end + 1:]

end_marker = nl + "}" + nl + nl + "@Composable" + nl + "private fun ActionButtonRow("
pos = s.find(end_marker, start)
if pos < 0:
    raise SystemExit("Admin integration stopped: wallet function end not found.")
if "AdminDashboardScreen(isBangla = isBangla" in s[start:pos]:
    s = s[:pos] + nl + "    }" + s[pos:]

p.write_text(s, encoding="utf-8")
print("Admin dashboard entry integrated into the generated Royal Wallet screen.")
