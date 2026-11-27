from pathlib import Path
import sys

path = Path(sys.argv[1])
source = path.read_text(encoding="utf-8")
anchor = "@Composable\\nprivate fun ActionButtonRow("
card = '''@Composable
private fun RoyalWelcomeCard() {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(18.dp))
            .background(
                Brush.linearGradient(
                    colors = listOf(Color(0xFF35496D), Color(0xFF1A2945), Color(0xFF142039))
                )
            )
            .border(1.dp, RoyalGold.copy(alpha = 0.42f), RoundedCornerShape(18.dp))
            .padding(horizontal = 14.dp, vertical = 12.dp)
    ) {
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier
                .size(46.dp)
                .clip(RoundedCornerShape(14.dp))
                .background(Brush.linearGradient(listOf(RoyalGold, Color(0xFFD99B35))))
        ) {
            Icon(
                imageVector = Icons.Rounded.WorkspacePremium,
                contentDescription = null,
                tint = RoyalNavyDeep,
                modifier = Modifier.size(27.dp)
            )
        }
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = "WELCOME TO THE ROYAL ARENA",
                style = MaterialTheme.typography.labelLarge,
                color = RoyalGold,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
            Spacer(Modifier.height(3.dp))
            Text(
                text = "Make your move. Enjoy a fair game.",
                style = MaterialTheme.typography.bodySmall,
                color = RoyalTextSecondary,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
        }
        Box(
            modifier = Modifier
                .clip(RoundedCornerShape(30.dp))
                .background(RoyalGold.copy(alpha = 0.13f))
                .border(1.dp, RoyalGold.copy(alpha = 0.35f), RoundedCornerShape(30.dp))
                .padding(horizontal = 9.dp, vertical = 6.dp)
        ) {
            Text(
                text = "3D EDITION",
                style = MaterialTheme.typography.labelSmall,
                color = RoyalGold,
                maxLines = 1
            )
        }
    }
}

\'''
if source.count("                PlayerHudRow(\\n") != 2:
    raise SystemExit("Expected exactly two game HUD insertion points; no source changed")
if anchor not in source:
    raise SystemExit("ActionButtonRow anchor not found; no source changed")
source = source.replace("                PlayerHudRow(\\n", "                RoyalWelcomeCard()\\n                PlayerHudRow(\\n")
source = source.replace(anchor, card + anchor, 1)
path.write_text(source, encoding="utf-8")
print(f"Updated {path}: added premium Royal Arena welcome card to both layouts")
