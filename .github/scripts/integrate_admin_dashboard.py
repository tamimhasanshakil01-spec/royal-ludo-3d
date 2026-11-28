from pathlib import Path

main = Path("app/src/main/java/com/example/MainActivity.kt")
source = main.read_text(encoding="utf-8")
nl = chr(10)

if "import com.example.game.AdminDashboardScreen" not in source:
    source = source.replace(
        "import com.example.game.OnlineGameScreen",
        "import com.example.game.OnlineGameScreen" + nl + "import com.example.game.AdminDashboardScreen",
        1
    )

if "var showAdminPanel by rememberSaveable" not in source:
    anchor = "    var activeTab by rememberSaveable { mutableStateOf(AppTab.HOME) }"
    if anchor not in source:
        raise SystemExit("Admin integration stopped: activeTab state anchor not found.")
    source = source.replace(anchor, anchor + nl + "    var showAdminPanel by rememberSaveable { mutableStateOf(false) }", 1)

anchor = """                            AppTab.WALLET -> {
                                RoyalWalletScreen(
                                    isBangla = isBangla,
                                    onDeposit = {"""
replacement = """                            AppTab.WALLET -> {
                                if (showAdminPanel) {
                                    AdminDashboardScreen(
                                        isBangla = isBangla,
                                        onBack = { showAdminPanel = false },
                                        modifier = Modifier.weight(1f)
                                    )
                                } else {
                                    RoyalWalletScreen(
                                        isBangla = isBangla,
                                        onAdmin = { showAdminPanel = true },
                                        onDeposit = {"""
if "onAdmin = { showAdminPanel = true }" not in source:
    if anchor not in source:
        raise SystemExit("Admin integration stopped: wallet screen call not found.")
    source = source.replace(anchor, replacement, 1)

close_anchor = """                                    modifier = Modifier.weight(1f)
                                )
                            }
                        }"""
close_replacement = """                                    modifier = Modifier.weight(1f)
                                    )
                                }
                            }
                        }"""
if "AdminDashboardScreen(" in source and close_anchor in source:
    source = source.replace(close_anchor, close_replacement, 1)

signature = """private fun RoyalWalletScreen(
    isBangla: Boolean,
    onDeposit: () -> Unit,"""
signature_new = """private fun RoyalWalletScreen(
    isBangla: Boolean,
    onAdmin: () -> Unit,
    onDeposit: () -> Unit,"""
if signature in source:
    source = source.replace(signature, signature_new, 1)

wallet_anchor = """        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
            Button(
                onClick = onDeposit,"""
wallet_new = """        OutlinedButton(
            onClick = onAdmin,
            modifier = Modifier.fillMaxWidth().height(48.dp),
            shape = RoundedCornerShape(14.dp)
        ) { Text(if (isBangla) "⚙ অ্যাডমিন প্যানেল" else "⚙ Admin Panel", color = RoyalGold) }
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
            Button(
                onClick = onDeposit,"""
if "onClick = onAdmin" not in source:
    if wallet_anchor not in source:
        raise SystemExit("Admin integration stopped: wallet action row not found.")
    source = source.replace(wallet_anchor, wallet_new, 1)

main.write_text(source, encoding="utf-8")
print("Admin panel integrated into the existing Wallet tab.")
