from pathlib import Path
import sys
p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
s = s.replace("import com.example.game.LudoUiState\n", "import com.example.game.GamePreset\nimport com.example.game.LudoUiState\n")
s = s.replace("                                    onRollDice = viewModel::rollDice,\n", "                                    onRollDice = viewModel::rollDice,\n                                    onPlayVsBots = { viewModel.applyPreset(GamePreset.VS_BOTS) },\n")
s = s.replace("    onRollDice: () -> Unit,\n", "    onRollDice: () -> Unit,\n    onPlayVsBots: () -> Unit,\n", 1)
s = s.replace("                RoyalWelcomeCard()\n                PlayerHudRow(", "                RoyalWelcomeCard()\n                RoyalQuickStartCard(\n                    gamesPlayed = uiState.totalGamesPlayed,\n                    wins = uiState.totalWins,\n                    onPlayVsBots = onPlayVsBots\n                )\n                PlayerHudRow(")
s = s.replace('text = "WELCOME TO THE ROYAL ARENA",', 'text = "ROYAL LUDO 3D  •  ROYAL ARENA",')
s = s.replace('text = "Make your move. Enjoy a fair game.",', 'text = "Play fair. Think smart. Rule the board.",')
anchor = "@Composable\nprivate fun ActionButtonRow("
card = '''@Composable
private fun RoyalQuickStartCard(gamesPlayed: Int, wins: Int, onPlayVsBots: () -> Unit) {
    val winRate = if (gamesPlayed > 0) wins * 100 / gamesPlayed else 0
    Column(
        modifier = Modifier.fillMaxWidth()
            .clip(RoundedCornerShape(18.dp))
            .background(Brush.linearGradient(listOf(Color(0xFF243A5E), Color(0xFF111D34))))
            .border(1.dp, RoyalGold.copy(alpha = 0.32f), RoundedCornerShape(18.dp))
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            Column {
                Text("YOUR ROYAL RECORD", style = MaterialTheme.typography.labelMedium, color = RoyalGold)
                Text("Every match makes you sharper", style = MaterialTheme.typography.bodySmall, color = RoyalTextSecondary)
            }
            Icon(Icons.Rounded.WorkspacePremium, contentDescription = null, tint = RoyalGold, modifier = Modifier.size(28.dp))
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
            RoyalStatTile("MATCHES", gamesPlayed.toString(), Modifier.weight(1f))
            RoyalStatTile("WINS", wins.toString(), Modifier.weight(1f))
            RoyalStatTile("WIN RATE", "$winRate%", Modifier.weight(1f))
        }
        Button(onClick = onPlayVsBots, modifier = Modifier.fillMaxWidth().height(48.dp).testTag("quick_play_bots"),
            shape = RoundedCornerShape(13.dp),
            colors = ButtonDefaults.buttonColors(containerColor = RoyalGold, contentColor = RoyalGoldTextOn)) {
            Icon(Icons.Rounded.Casino, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text("PLAY NOW  •  VS SMART BOTS", style = MaterialTheme.typography.labelLarge)
        }
    }
}

@Composable
private fun RoyalStatTile(label: String, value: String, modifier: Modifier = Modifier) {
    Column(modifier = modifier.clip(RoundedCornerShape(11.dp))
        .background(Color(0xFF0C172B).copy(alpha = 0.78f))
        .padding(vertical = 9.dp, horizontal = 5.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, style = MaterialTheme.typography.titleLarge, color = RoyalGold)
        Text(label, style = MaterialTheme.typography.labelSmall, color = RoyalTextSecondary, maxLines = 1)
    }
}

'''
if anchor not in s:
    raise SystemExit("ActionButtonRow anchor missing")
if "private fun RoyalQuickStartCard(" not in s:
    s = s.replace(anchor, card + anchor, 1)


# Wallet tab: UI-only placeholders, with no account collection or real-money flow.
s = s.replace("    INVITE\n}", "    INVITE,\n    WALLET\n}")
s = s.replace('''                                modifier = Modifier.testTag("nav_invite")
                            )
                        }
                    }
                }''', '''                                modifier = Modifier.testTag("nav_invite")
                            )
                            NavigationBarItem(
                                selected = activeTab == AppTab.WALLET,
                                onClick = { activeTab = AppTab.WALLET },
                                icon = { Text("৳") },
                                label = { Text("ওয়ালেট") },
                                colors = NavigationBarItemDefaults.colors(
                                    selectedIconColor = RoyalGoldTextOn,
                                    selectedTextColor = RoyalGold,
                                    indicatorColor = RoyalGold,
                                    unselectedIconColor = RoyalTextSecondary,
                                    unselectedTextColor = RoyalTextSecondary
                                ),
                                modifier = Modifier.testTag("nav_wallet")
                            )
                        }
                    }
                }''', 1)
s = s.replace('''                                modifier = Modifier.testTag("nav_invite")
                            )
                        }
                    }

                    Column(modifier = Modifier.fillMaxSize())''', '''                                modifier = Modifier.testTag("nav_invite")
                            )
                            Spacer(Modifier.height(8.dp))
                            NavigationRailItem(
                                selected = activeTab == AppTab.WALLET,
                                onClick = { activeTab = AppTab.WALLET },
                                icon = { Text("৳") },
                                label = { Text("ওয়ালেট") },
                                colors = NavigationRailItemDefaults.colors(
                                    selectedIconColor = RoyalGoldTextOn,
                                    selectedTextColor = RoyalGold,
                                    indicatorColor = RoyalGold,
                                    unselectedIconColor = RoyalTextSecondary,
                                    unselectedTextColor = RoyalTextSecondary
                                ),
                                modifier = Modifier.testTag("nav_wallet")
                            )
                        }
                    }

                    Column(modifier = Modifier.fillMaxSize())''', 1)
s = s.replace('''                            AppTab.INVITE -> {
                                InviteAndRulesScreen(''', '''                            AppTab.INVITE -> {
                                InviteAndRulesScreen(''', 1)
s = s.replace('''                                    modifier = Modifier.weight(1f)
                                )
                            }
                        }
                    }''', '''                                    modifier = Modifier.weight(1f)
                                )
                            }
                            AppTab.WALLET -> {
                                RoyalWalletScreen(
                                    onDeposit = {
                                        coroutineScope.launch {
                                            snackbarHostState.showSnackbar("ডেমো: জমা সেবা এখনো চালু হয়নি। কোনো টাকা পাঠাবেন না।")
                                        }
                                    },
                                    onWithdraw = {
                                        coroutineScope.launch {
                                            snackbarHostState.showSnackbar("ডেমো: উত্তোলন সেবা এখনো চালু হয়নি।")
                                        }
                                    },
                                    modifier = Modifier.weight(1f)
                                )
                            }
                        }
                    }''', 1)
wallet = '''
@Composable
private fun RoyalWalletScreen(
    onDeposit: () -> Unit,
    onWithdraw: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        Text("ROYAL WALLET", style = MaterialTheme.typography.headlineSmall, color = RoyalGold)
        Column(
            modifier = Modifier.fillMaxWidth()
                .clip(RoundedCornerShape(20.dp))
                .background(Brush.linearGradient(listOf(Color(0xFF243A5E), Color(0xFF111D34))))
                .border(1.dp, RoyalGold.copy(alpha = 0.35f), RoundedCornerShape(20.dp))
                .padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text("ওয়ালেট ব্যালেন্স", style = MaterialTheme.typography.labelLarge, color = RoyalTextSecondary)
            Text("৳ ০.০০", style = MaterialTheme.typography.displaySmall, color = RoyalGold)
            Text("এটি কেবল ডেমো ব্যালেন্স; বাস্তব অর্থ নয়।", style = MaterialTheme.typography.bodySmall, color = RoyalTextSecondary)
        }
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
            Button(
                onClick = onDeposit,
                modifier = Modifier.weight(1f).height(52.dp).testTag("wallet_deposit"),
                colors = ButtonDefaults.buttonColors(containerColor = RoyalGold, contentColor = RoyalGoldTextOn),
                shape = RoundedCornerShape(14.dp)
            ) { Text("＋ টাকা জমা") }
            OutlinedButton(
                onClick = onWithdraw,
                modifier = Modifier.weight(1f).height(52.dp).testTag("wallet_withdraw"),
                shape = RoundedCornerShape(14.dp)
            ) { Text("↑ টাকা উত্তোলন", color = RoyalGold) }
        }
        Column(
            modifier = Modifier.fillMaxWidth()
                .clip(RoundedCornerShape(16.dp))
                .background(RoyalNavyPanelBottom)
                .border(1.dp, RoyalNavyBorder, RoundedCornerShape(16.dp))
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text("লেনদেনের অবস্থা", style = MaterialTheme.typography.titleMedium, color = RoyalGold)
            Text("জমা ও উত্তোলনের অপশন রাখা হয়েছে। তবে এখনো কোনো পেমেন্ট গেটওয়ে, ব্যাংক/মোবাইল অ্যাকাউন্ট বা সার্ভার যুক্ত করা হয়নি।", color = RoyalTextPrimary, style = MaterialTheme.typography.bodyMedium)
            Text("নিরাপত্তা ও প্রয়োজনীয় আইনগত অনুমোদন নিশ্চিত না হওয়া পর্যন্ত বাস্তব টাকা পাঠাবেন না।", color = RoyalTextSecondary, style = MaterialTheme.typography.bodySmall)
        }
    }
}

'''
anchor = "@Composable\nprivate fun ActionButtonRow("
if anchor not in s:
    raise SystemExit("wallet insertion anchor missing")
if "private fun RoyalWalletScreen(" not in s:
    s = s.replace(anchor, wallet + anchor, 1)

# Upgrade the default bot from a simple progress-first picker to a tactical
# evaluator. The game remains offline and deterministic in its rules.
vm_path = p.parent / "game" / "LudoViewModel.kt"
vm_s = vm_path.read_text(encoding="utf-8")
ai_start = vm_s.find("    private fun chooseBotToken(")
ai_end = vm_s.find("\n    private fun detectPreset(", ai_start)
if ai_start < 0 or ai_end < 0:
    raise SystemExit("Could not locate chooseBotToken() for AI upgrade")
smart_ai = """    private fun chooseBotToken(
        bot: PlayerColor,
        movableIndices: Set<Int>,
        dice: Int,
        state: LudoUiState
    ): Int {
        val botPieces = state.pieces[bot].orEmpty()
        return movableIndices.maxByOrNull { tokenIndex ->
            val currentProgress = botPieces.getOrNull(tokenIndex) ?: LudoBoardGeometry.HOME_YARD
            val targetProgress = if (currentProgress == LudoBoardGeometry.HOME_YARD) 0
                else currentProgress + dice
            val targetAbs = LudoBoardGeometry.absoluteTrackIndex(bot, targetProgress)
            var score = 0

            // Core progress and finishing priorities.
            score += if (currentProgress == LudoBoardGeometry.HOME_YARD) 260 else dice * 24
            if (targetProgress == LudoBoardGeometry.GOAL_PROGRESS) score += 5000
            if (targetProgress in 51..55 && currentProgress <= 50) score += 520
            if (currentProgress in 0..50 && targetProgress > 50) score += 180
            if (currentProgress == LudoBoardGeometry.HOME_YARD && dice == 6) score += 300

            if (targetAbs != null) {
                val isSafe = targetAbs in LudoBoardGeometry.safeTrackIndices
                if (isSafe) score += 420

                // Capturing an opponent is a strong tactical move.
                if (!isSafe) {
                    val captured = PlayerColor.entries
                        .filter { it != bot }
                        .sumOf { opponent ->
                            state.pieces[opponent].orEmpty().count { opponentProgress ->
                                LudoBoardGeometry.absoluteTrackIndex(opponent, opponentProgress) == targetAbs
                            }
                        }
                    score += captured * 1350
                }

                // Avoid landing on exposed squares that an opponent can reach
                // with a single die roll on their next turn.
                if (!isSafe) {
                    var attackers = 0
                    for (opponent in PlayerColor.entries) {
                        if (opponent == bot) continue
                        for (opponentProgress in state.pieces[opponent].orEmpty()) {
                            val opponentAbs = LudoBoardGeometry.absoluteTrackIndex(opponent, opponentProgress)
                                ?: continue
                            val distance = (targetAbs - opponentAbs + LudoBoardGeometry.outerTrack.size) %
                                LudoBoardGeometry.outerTrack.size
                            if (distance in 1..6) attackers++
                        }
                    }
                    score -= attackers * 210
                }

                // Prefer moving a piece out of immediate danger.
                if (currentProgress in 0..50) {
                    val currentAbs = LudoBoardGeometry.absoluteTrackIndex(bot, currentProgress)
                    if (currentAbs != null && currentAbs !in LudoBoardGeometry.safeTrackIndices) {
                        val threatened = PlayerColor.entries.any { opponent ->
                            opponent != bot && state.pieces[opponent].orEmpty().any { opponentProgress ->
                                val opponentAbs = LudoBoardGeometry.absoluteTrackIndex(opponent, opponentProgress)
                                opponentAbs != null &&
                                    ((currentAbs - opponentAbs + LudoBoardGeometry.outerTrack.size) %
                                        LudoBoardGeometry.outerTrack.size) in 1..6
                            }
                        }
                        if (threatened) score += 160
                    }
                }
            }

            // Small stable tie-break preference for advancing the most developed piece.
            score += targetProgress.coerceAtLeast(0) * 2
            score + Random.nextInt(0, 18)
        } ?: movableIndices.first()
    }
"""
vm_s = vm_s[:ai_start] + smart_ai + vm_s[ai_end:]

# Add a persistent in-app Bangla/English switch in the header and key navigation.
if "var isBangla by rememberSaveable" not in s:
    s = s.replace(
        '    var activeTab by rememberSaveable { mutableStateOf(AppTab.PLAY) }',
        '    var activeTab by rememberSaveable { mutableStateOf(AppTab.PLAY) }\n    var isBangla by rememberSaveable { mutableStateOf(true) }'
    )
s = s.replace(
    '                            onOpenProfiles = { editingIdentityPlayer = uiState.currentTurn },',
    '                            onOpenProfiles = { editingIdentityPlayer = uiState.currentTurn },\n                            isBangla = isBangla,\n                            onToggleLanguage = { isBangla = !isBangla },'
)
s = s.replace(
    '    onOpenProfiles: () -> Unit,\n    modifier: Modifier = Modifier',
    '    onOpenProfiles: () -> Unit,\n    isBangla: Boolean,\n    onToggleLanguage: () -> Unit,\n    modifier: Modifier = Modifier'
)
# Replace navigation labels with language-aware labels.
s = s.replace('label = { Text(stringResource(R.string.nav_play)) }', 'label = { Text(if (isBangla) "খেলা" else "Play") }')
s = s.replace('label = { Text(stringResource(R.string.nav_invite)) }', 'label = { Text(if (isBangla) "আমন্ত্রণ" else "Invite") }')
s = s.replace('label = { Text("ওয়ালেট") }', 'label = { Text(if (isBangla) "ওয়ালেট" else "Wallet") }')
# Wallet page content follows the selected language.
s = s.replace('''RoyalWalletScreen(
                                    onDeposit = {''', '''RoyalWalletScreen(
                                    isBangla = isBangla,
                                    onDeposit = {''')
s = s.replace('''private fun RoyalWalletScreen(
    onDeposit: () -> Unit,''', '''private fun RoyalWalletScreen(
    isBangla: Boolean,
    onDeposit: () -> Unit,''')
s = s.replace('Text("ROYAL WALLET", style = MaterialTheme.typography.headlineSmall, color = RoyalGold)',
'''Text(if (isBangla) "রয়্যাল ওয়ালেট" else "ROYAL WALLET", style = MaterialTheme.typography.headlineSmall, color = RoyalGold)''')
s = s.replace('Text("ওয়ালেট ব্যালেন্স", style = MaterialTheme.typography.labelLarge, color = RoyalTextSecondary)',
'''Text(if (isBangla) "ওয়ালেট ব্যালেন্স" else "Wallet balance", style = MaterialTheme.typography.labelLarge, color = RoyalTextSecondary)''')
s = s.replace('Text("৳ ০.০০", style = MaterialTheme.typography.displaySmall, color = RoyalGold)',
'''Text(if (isBangla) "৳ ০.০০" else "৳ 0.00", style = MaterialTheme.typography.displaySmall, color = RoyalGold)''')
s = s.replace('Text("এটি কেবল ডেমো ব্যালেন্স; বাস্তব অর্থ নয়।", style = MaterialTheme.typography.bodySmall, color = RoyalTextSecondary)',
'''Text(if (isBangla) "এটি কেবল ডেমো ব্যালেন্স; বাস্তব অর্থ নয়।" else "Demo balance only — not real money.", style = MaterialTheme.typography.bodySmall, color = RoyalTextSecondary)''')
s = s.replace('''            ) { Text("＋ টাকা জমা") }''', '''            ) { Text(if (isBangla) "＋ টাকা জমা" else "＋ Deposit") }''')
s = s.replace('''            ) { Text("↑ টাকা উত্তোলন", color = RoyalGold) }''', '''            ) { Text(if (isBangla) "↑ টাকা উত্তোলন" else "↑ Withdraw", color = RoyalGold) }''')
s = s.replace('Text("লেনদেনের অবস্থা", style = MaterialTheme.typography.titleMedium, color = RoyalGold)',
'''Text(if (isBangla) "লেনদেনের অবস্থা" else "Transaction status", style = MaterialTheme.typography.titleMedium, color = RoyalGold)''')
s = s.replace('''            Text("জমা ও উত্তোলনের অপশন রাখা হয়েছে। তবে এখনো কোনো পেমেন্ট গেটওয়ে, ব্যাংক/মোবাইল অ্যাকাউন্ট বা সার্ভার যুক্ত করা হয়নি।", color = RoyalTextPrimary, style = MaterialTheme.typography.bodyMedium)
            Text("নিরাপত্তা ও প্রয়োজনীয় আইনগত অনুমোদন নিশ্চিত না হওয়া পর্যন্ত বাস্তব টাকা পাঠাবেন না।", color = RoyalTextSecondary, style = MaterialTheme.typography.bodySmall)''',
'''            Text(if (isBangla) "জমা ও উত্তোলনের অপশন রাখা হয়েছে। তবে এখনো কোনো পেমেন্ট গেটওয়ে, ব্যাংক/মোবাইল অ্যাকাউন্ট বা সার্ভার যুক্ত করা হয়নি।" else "Deposit and withdrawal are demo-only. No payment gateway, bank/mobile account, or server is connected.", color = RoyalTextPrimary, style = MaterialTheme.typography.bodyMedium)
            Text(if (isBangla) "নিরাপত্তা ও প্রয়োজনীয় আইনগত অনুমোদন নিশ্চিত না হওয়া পর্যন্ত বাস্তব টাকা পাঠাবেন না।" else "Do not send real money until security and legal approvals are in place.", color = RoyalTextSecondary, style = MaterialTheme.typography.bodySmall)''')
# Header control is visible on all tabs and preserves selection during recomposition.
s = s.replace('''            IconButton(
                onClick = onOpenProfiles,''', '''            OutlinedButton(
                onClick = onToggleLanguage,
                modifier = Modifier.height(38.dp).testTag("language_toggle"),
                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 0.dp),
                shape = RoundedCornerShape(18.dp)
            ) { Text(if (isBangla) "EN" else "বাংলা", color = RoyalGold) }

            IconButton(
                onClick = onOpenProfiles,''', 1)

p.write_text(s, encoding="utf-8")
vm_path.write_text(vm_s, encoding="utf-8")


# A vivid, adaptive launcher emblem: royal crown, four player colors and a dice.
icon_path = p.parents[3] / "res" / "drawable" / "ic_launcher_foreground.xml"
icon_path.write_text("""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp"
    android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#FFD54F"
        android:pathData="M24,30 L17,17 L35,26 L54,10 L73,26 L91,17 L84,30 L79,39 L29,39 Z" />
    <path android:fillColor="#FFF0A6"
        android:pathData="M29,34 L79,34 L75,43 L33,43 Z" />
    <path android:fillColor="#D99B26"
        android:pathData="M30,43 L78,43 L75,49 L33,49 Z" />
    <path android:fillColor="#F04452"
        android:pathData="M20,59 m-9,0 a9,9 0 1,0 18,0 a9,9 0 1,0 -18,0" />
    <path android:fillColor="#3989FF"
        android:pathData="M88,59 m-9,0 a9,9 0 1,0 18,0 a9,9 0 1,0 -18,0" />
    <path android:fillColor="#27C27A"
        android:pathData="M31,87 m-9,0 a9,9 0 1,0 18,0 a9,9 0 1,0 -18,0" />
    <path android:fillColor="#FFC928"
        android:pathData="M77,87 m-9,0 a9,9 0 1,0 18,0 a9,9 0 1,0 -18,0" />
    <path android:fillColor="#FFFDF6"
        android:pathData="M37,49 L71,49 Q77,49 77,55 L77,79 Q77,85 71,85 L37,85 Q31,85 31,79 L31,55 Q31,49 37,49 Z" />
    <path android:fillColor="#DCE6F4"
        android:pathData="M31,76 L77,76 L77,80 Q77,85 71,85 L37,85 Q31,85 31,80 Z" />
    <path android:fillColor="#F04452"
        android:pathData="M43,59 m-4,0 a4,4 0 1,0 8,0 a4,4 0 1,0 -8,0" />
    <path android:fillColor="#3989FF"
        android:pathData="M65,59 m-4,0 a4,4 0 1,0 8,0 a4,4 0 1,0 -8,0" />
    <path android:fillColor="#27C27A"
        android:pathData="M43,75 m-4,0 a4,4 0 1,0 8,0 a4,4 0 1,0 -8,0" />
    <path android:fillColor="#FFC928"
        android:pathData="M65,75 m-4,0 a4,4 0 1,0 8,0 a4,4 0 1,0 -8,0" />
    <path android:fillColor="#D99B26"
        android:pathData="M54,67 m-3.5,0 a3.5,3.5 0 1,0 7,0 a3.5,3.5 0 1,0 -7,0" />
</vector>
""", encoding="utf-8")


# ---------------------------------------------------------------------------
# Premium Royal Ludo lobby: make this the first screen shown when the APK opens.
# The actual game remains behind PLAY NOW; this lobby is real Compose UI, not a
# flattened screenshot, so its controls remain interactive and accessible.
main_path = p.parent.parent / "src" / "main" / "java" / "com" / "example" / "MainActivity.kt"
ms = main_path.read_text(encoding="utf-8")

ms = ms.replace("enum class AppTab {\\n    PLAY,", "enum class AppTab {\\n    HOME,\\n    PLAY,", 1)
ms = ms.replace("var activeTab by rememberSaveable { mutableStateOf(AppTab.PLAY) }",
                "var activeTab by rememberSaveable { mutableStateOf(AppTab.HOME) }", 1)
ms = ms.replace("if (activeTab != AppTab.PLAY) {\\n        BackHandler { activeTab = AppTab.PLAY }",
                "if (activeTab != AppTab.HOME) {\\n        BackHandler { activeTab = AppTab.HOME }", 1)

# Insert HOME navigation item in compact bottom navigation and wide navigation rail.
mobile_anchor = """                            NavigationBarItem(
                                selected = activeTab == AppTab.PLAY,"""
mobile_home = """                            NavigationBarItem(
                                selected = activeTab == AppTab.HOME,
                                onClick = { activeTab = AppTab.HOME },
                                icon = { Text("👑") },
                                label = { Text(if (isBangla) "হোম" else "Home") },
                                colors = NavigationBarItemDefaults.colors(
                                    selectedIconColor = RoyalGoldTextOn,
                                    selectedTextColor = RoyalGold,
                                    indicatorColor = RoyalGold,
                                    unselectedIconColor = RoyalTextSecondary,
                                    unselectedTextColor = RoyalTextSecondary
                                ),
                                modifier = Modifier.testTag("nav_home")
                            )
                            NavigationBarItem(
                                selected = activeTab == AppTab.PLAY,"""
if 'testTag("nav_home")' not in ms:
    ms = ms.replace(mobile_anchor, mobile_home, 1)

rail_anchor = """                            NavigationRailItem(
                                selected = activeTab == AppTab.PLAY,"""
rail_home = """                            NavigationRailItem(
                                selected = activeTab == AppTab.HOME,
                                onClick = { activeTab = AppTab.HOME },
                                icon = { Text("👑") },
                                label = { Text(if (isBangla) "হোম" else "Home") },
                                colors = NavigationRailItemDefaults.colors(
                                    selectedIconColor = RoyalGoldTextOn,
                                    selectedTextColor = RoyalGold,
                                    indicatorColor = RoyalGold,
                                    unselectedIconColor = RoyalTextSecondary,
                                    unselectedTextColor = RoyalTextSecondary
                                ),
                                modifier = Modifier.testTag("nav_home")
                            )
                            Spacer(Modifier.height(8.dp))
                            NavigationRailItem(
                                selected = activeTab == AppTab.PLAY,"""
if ms.count('testTag("nav_home")') < 2:
    ms = ms.replace(rail_anchor, rail_home, 1)

# Route the HOME tab to the lobby and keep the existing PLAY tab as the game.
when_anchor = """                        when (activeTab) {
                            AppTab.PLAY -> {"""
when_home = """                        when (activeTab) {
                            AppTab.HOME -> {
                                RoyalLobbyScreen(
                                    isBangla = isBangla,
                                    onPlay = { activeTab = AppTab.PLAY },
                                    onInvite = { activeTab = AppTab.INVITE },
                                    onWallet = { activeTab = AppTab.WALLET },
                                    onRules = { showRulesDialog = true },
                                    onToggleLanguage = { isBangla = !isBangla },
                                    modifier = Modifier.weight(1f)
                                )
                            }
                            AppTab.PLAY -> {"""
if "RoyalLobbyScreen(" not in ms:
    ms = ms.replace(when_anchor, when_home, 1)

lobby = r'''
@Composable
private fun RoyalLobbyScreen(
    isBangla: Boolean,
    onPlay: () -> Unit,
    onInvite: () -> Unit,
    onWallet: () -> Unit,
    onRules: () -> Unit,
    onToggleLanguage: () -> Unit,
    modifier: Modifier = Modifier
) {
    val gold = Color(0xFFFFD45A)
    val deep = Color(0xFF080F2D)
    Column(
        modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState())
            .background(Brush.verticalGradient(listOf(Color(0xFF142A70), deep, Color(0xFF240C42))))
            .padding(horizontal = 12.dp, vertical = 8.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(22.dp))
                .background(Brush.horizontalGradient(listOf(Color(0xFF101B43), Color(0xFF243A72))))
                .border(1.dp, gold.copy(alpha = .8f), RoundedCornerShape(22.dp))
                .padding(10.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(48.dp).clip(RoundedCornerShape(24.dp))
                    .background(Brush.radialGradient(listOf(Color(0xFFFFE28A), Color(0xFFB66A12)))),
                    contentAlignment = Alignment.Center) {
                    Text("👑", style = MaterialTheme.typography.headlineMedium)
                }
                Spacer(Modifier.width(9.dp))
                Column {
                    Text(if (isBangla) "রয়্যাল প্লেয়ার" else "ROYAL PLAYER",
                        color = Color.White, style = MaterialTheme.typography.titleMedium)
                    Text(if (isBangla) "স্বাগতম" else "WELCOME BACK",
                        color = gold, style = MaterialTheme.typography.labelSmall)
                }
            }
            OutlinedButton(onClick = onToggleLanguage, contentPadding = PaddingValues(horizontal = 12.dp, vertical = 2.dp),
                shape = RoundedCornerShape(18.dp)) {
                Text(if (isBangla) "EN" else "বাংলা", color = gold)
            }
        }

        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text("👑  ROYAL", color = gold, style = MaterialTheme.typography.displaySmall)
            Text("LUDO 3D", color = Color.White, style = MaterialTheme.typography.displayMedium)
            Text(if (isBangla) "খেলো • উপভোগ করো • জেতো" else "PLAY  •  ENJOY  •  WIN",
                color = Color(0xFFFFE9A6), style = MaterialTheme.typography.titleSmall)
        }

        // Decorative 3D-inspired board made from live Compose elements.
        Column(
            Modifier.fillMaxWidth().clip(RoundedCornerShape(22.dp))
                .background(Brush.verticalGradient(listOf(Color(0xFFFFD979), Color(0xFF9C5417))))
                .border(2.dp, Color(0xFFFFE9A6), RoundedCornerShape(22.dp)).padding(7.dp)
        ) {
            Row(Modifier.fillMaxWidth().height(104.dp)) {
                LobbyBoardHome(Color(0xFFD92742), "🔴", Modifier.weight(1f))
                LobbyBoardHome(Color(0xFF22A96B), "🟢", Modifier.weight(1f))
            }
            Box(Modifier.fillMaxWidth().height(48.dp).background(Color(0xFFFFF5D8)),
                contentAlignment = Alignment.Center) {
                Text("⚄     🎲     ⚄", style = MaterialTheme.typography.headlineLarge, color = Color(0xFF15264C))
            }
            Row(Modifier.fillMaxWidth().height(104.dp)) {
                LobbyBoardHome(Color(0xFF2479E8), "🔵", Modifier.weight(1f))
                LobbyBoardHome(Color(0xFFF4BE22), "🟡", Modifier.weight(1f))
            }
        }

        Button(
            onClick = onPlay,
            modifier = Modifier.fillMaxWidth().height(66.dp)
                .border(2.dp, Color(0xFFFFE8A1), RoundedCornerShape(20.dp))
                .testTag("lobby_play_now"),
            shape = RoundedCornerShape(20.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFC51E2C), contentColor = Color.White),
            contentPadding = PaddingValues(10.dp)
        ) {
            Text("▶", color = gold, style = MaterialTheme.typography.headlineMedium)
            Spacer(Modifier.width(12.dp))
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(if (isBangla) "এখনই খেলুন" else "PLAY NOW", style = MaterialTheme.typography.headlineSmall)
                Text(if (isBangla) "গেম স্ক্রিন খুলুন" else "ENTER THE GAME", style = MaterialTheme.typography.labelSmall)
            }
        }

        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            LobbyAction("🎁", if (isBangla) "দৈনিক পুরস্কার" else "Daily Rewards", Modifier.weight(1f)) { onRules() }
            LobbyAction("🏆", if (isBangla) "লিডারবোর্ড" else "Leaderboard", Modifier.weight(1f)) { onRules() }
            LobbyAction("👑", "VIP Club", Modifier.weight(1f)) { onRules() }
        }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            LobbyAction("💼", if (isBangla) "ওয়ালেট" else "Wallet", Modifier.weight(1f), onWallet)
            LobbyAction("🤝", if (isBangla) "বন্ধু আমন্ত্রণ" else "Refer & Invite", Modifier.weight(1f), onInvite)
            LobbyAction("❔", if (isBangla) "কীভাবে খেলবেন" else "How to Play", Modifier.weight(1f), onRules)
        }
        Text(if (isBangla) "ROYAL LUDO 3D  •  স্মার্টভাবে খেলুন" else "ROYAL LUDO 3D  •  PLAY SMART",
            color = gold, style = MaterialTheme.typography.labelMedium,
            textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp))
    }
}

@Composable
private fun LobbyBoardHome(color: Color, pawn: String, modifier: Modifier = Modifier) {
    Box(modifier.fillMaxSize().padding(3.dp).clip(RoundedCornerShape(13.dp))
        .background(Brush.linearGradient(listOf(color, color.copy(alpha = .68f))))
        .border(1.dp, Color.White.copy(alpha = .75f), RoundedCornerShape(13.dp)),
        contentAlignment = Alignment.Center) {
        Text(pawn, style = MaterialTheme.typography.displayLarge)
    }
}

@Composable
private fun LobbyAction(icon: String, label: String, modifier: Modifier = Modifier, onClick: () -> Unit) {
    OutlinedButton(
        onClick = onClick, modifier = modifier.height(76.dp),
        shape = RoundedCornerShape(15.dp),
        contentPadding = PaddingValues(4.dp),
        colors = androidx.compose.material3.ButtonDefaults.outlinedButtonColors(
            containerColor = Color(0xFF171B45), contentColor = Color.White
        )
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
            Text(icon, style = MaterialTheme.typography.titleLarge)
            Text(label, style = MaterialTheme.typography.labelSmall, textAlign = TextAlign.Center, maxLines = 2)
        }
    }
}

'''
if "private fun RoyalLobbyScreen(" not in ms:
    ms += "\n" + lobby

main_path.write_text(ms, encoding="utf-8")
