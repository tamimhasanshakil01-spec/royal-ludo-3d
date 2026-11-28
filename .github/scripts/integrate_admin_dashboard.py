from pathlib import Path

p = Path("app/src/main/java/com/example/MainActivity.kt")
s = p.read_text(encoding="utf-8")
nl = chr(10)

if "import com.example.game.AdminDashboardScreen" not in s:
    anchor = "import com.example.game.OnlineGameScreen"
    if anchor not in s:
        raise SystemExit("Admin integration stopped: online screen import missing.")
    s = s.replace(anchor, anchor + nl + "import com.example.game.AdminDashboardScreen", 1)

if "var showAdminPanel by rememberSaveable" not in s:
    anchor = "    var activeTab by rememberSaveable { mutableStateOf(AppTab.HOME) }"
    if anchor not in s:
        raise SystemExit("Admin integration stopped: activeTab state not found.")
    s = s.replace(anchor, anchor + nl + "    var showAdminPanel by rememberSaveable { mutableStateOf(false) }", 1)

wallet_open = nl.join([
    "                            AppTab.WALLET -> {",
    "                                RoyalWalletScreen("
])
wallet_replacement = nl.join([
    "                            AppTab.WALLET -> {",
    "                                if (showAdminPanel) {",
    "                                    AdminDashboardScreen(",
    "                                        isBangla = isBangla,",
    "                                        onBack = { showAdminPanel = false },",
    "                                        modifier = Modifier.weight(1f)",
    "                                    )",
    "                                } else {",
    "                                    RoyalWalletScreen("
])
if "onAdmin = { showAdminPanel = true }" not in s:
    if wallet_open not in s:
        raise SystemExit("Admin integration stopped: Wallet screen call not found.")
    s = s.replace(wallet_open, wallet_replacement, 1)
    s = s.replace(
        "                                    isBangla = isBangla," + nl + "                                    onDeposit = {",
        "                                    isBangla = isBangla," + nl + "                                    onAdmin = { showAdminPanel = true }," + nl + "                                    onDeposit = {",
        1
    )
    wallet_start = s.index("                            AppTab.WALLET -> {")
    close_anchor = nl.join([
        "                                    modifier = Modifier.weight(1f)",
        "                                )",
        "                            }",
        "                        }"
    ])
    close_at = s.find(close_anchor, wallet_start)
    if close_at < 0:
        raise SystemExit("Admin integration stopped: Wallet branch closing point not found.")
    s = s[:close_at] + close_anchor.replace("                            }", "                                }" + nl + "                            }", 1) + s[close_at + len(close_anchor):]

signature = nl.join([
    "private fun RoyalWalletScreen(",
    "    isBangla: Boolean,",
    "    onDeposit: () -> Unit,"
])
signature_new = nl.join([
    "private fun RoyalWalletScreen(",
    "    isBangla: Boolean,",
    "    onAdmin: () -> Unit,",
    "    onDeposit: () -> Unit,"
])
if signature in s:
    s = s.replace(signature, signature_new, 1)

actions = nl.join([
    "        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {",
    "            Button(",
    "                onClick = onDeposit,"
])
if "onClick = onAdmin" not in s:
    if actions not in s:
        raise SystemExit("Admin integration stopped: wallet action buttons not found.")
    button = nl.join([
        "        OutlinedButton(",
        "            onClick = onAdmin,",
        "            modifier = Modifier.fillMaxWidth().height(48.dp),",
        "            shape = RoundedCornerShape(14.dp)",
        "        ) { Text(if (isBangla) \"⚙ অ্যাডমিন প্যানেল\" else \"⚙ Admin Panel\", color = RoyalGold) }"
    ])
    s = s.replace(actions, button + nl + actions, 1)

p.write_text(s, encoding="utf-8")
print("Admin panel integrated into Wallet tab.")
