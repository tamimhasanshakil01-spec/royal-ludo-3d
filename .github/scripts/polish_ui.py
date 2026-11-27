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
p.write_text(s, encoding="utf-8")
