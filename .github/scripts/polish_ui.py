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

# Upgrade the default bot from a simple progress-first picker to a tactical
# evaluator. The game remains offline and deterministic in its rules.
ai_start = s.find("    private fun chooseBotToken(")
ai_end = s.find("\n    private fun detectPreset(", ai_start)
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
s = s[:ai_start] + smart_ai + s[ai_end:]

p.write_text(s, encoding="utf-8")
