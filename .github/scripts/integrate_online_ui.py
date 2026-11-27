from pathlib import Path
p = Path("app/src/main/java/com/example/MainActivity.kt")
s = p.read_text(encoding="utf-8")
imp = "import com.example.game.OnlineGameScreen\\n"
if imp not in s:
    s = s.replace("import com.example.game.LudoViewModel\\n", "import com.example.game.LudoViewModel\\n" + imp)
old = """                            AppTab.PLAY -> {
                                PlayGameScreen(
                                    uiState = uiState,
                                    isWideLayout = isExpandedLayout,
                                    onRollDice = viewModel::rollDice,
                                    onPlayVsBots = { viewModel.applyPreset(GamePreset.VS_BOTS) },
                                    onTokenClick = viewModel::moveToken,
                                    onPlayerClick = { editingIdentityPlayer = it },
                                    onNewGame = viewModel::resetCurrentGame,
                                    onOpenModeSetup = { showSetupDialog = true },
                                    onOpenRules = { showRulesDialog = true },
                                    modifier = Modifier.weight(1f)
                                )
                            }"""
new = """                            AppTab.PLAY -> {
                                OnlineGameScreen(
                                    isBangla = isBangla,
                                    modifier = Modifier.weight(1f)
                                )
                            }"""
if old not in s:
    raise SystemExit("Could not find PLAY tab block to replace")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("Main PLAY tab now opens the Firebase online game screen.")
