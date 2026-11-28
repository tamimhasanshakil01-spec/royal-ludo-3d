from pathlib import Path

vm = Path("app/src/main/java/com/example/game/LudoViewModel.kt")
s = vm.read_text(encoding="utf-8")
old = """        val sanitizedSeats = if (activePlayers.size >= 2) {
            seats
        } else {
            mapOf(
                PlayerColor.RED to SeatControl.HUMAN,
                PlayerColor.BLUE to SeatControl.HUMAN,
                PlayerColor.YELLOW to SeatControl.HUMAN,
                PlayerColor.GREEN to SeatControl.HUMAN
            )
        }"""
new = """        val sanitizedSeats = when {
            activePlayers.size >= 2 -> seats
            activePlayers.size == 1 -> {
                val onlyPlayer = activePlayers.first()
                val expertBot = if (onlyPlayer == PlayerColor.BLUE) PlayerColor.RED else PlayerColor.BLUE
                PlayerColor.entries.associateWith { color ->
                    when (color) {
                        onlyPlayer -> seats[color] ?: SeatControl.HUMAN
                        expertBot -> SeatControl.BOT
                        else -> SeatControl.OFF
                    }
                }
            }
            else -> mapOf(
                PlayerColor.RED to SeatControl.HUMAN,
                PlayerColor.BLUE to SeatControl.BOT,
                PlayerColor.YELLOW to SeatControl.BOT,
                PlayerColor.GREEN to SeatControl.BOT
            )
        }"""
if old not in s:
    raise SystemExit("Expected startNewGame seat validation block was not found; refusing unsafe patch.")
s = s.replace(old, new, 1)
vm.write_text(s, encoding="utf-8")

dialog = Path("app/src/main/java/com/example/ui/components/DialogsAndSheets.kt")
d = dialog.read_text(encoding="utf-8")
if "val isValid = activeCount >= 2" not in d:
    raise SystemExit("Expected player-count validation was not found.")
d = d.replace("val isValid = activeCount >= 2", "val isValid = activeCount >= 1", 1)
dialog.write_text(d, encoding="utf-8")
print("Applied one-human-versus-one-expert-bot support and minimum-one-player validation.")
