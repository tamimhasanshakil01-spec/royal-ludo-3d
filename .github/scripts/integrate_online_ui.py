from pathlib import Path
import re
p = Path("app/src/main/java/com/example/MainActivity.kt")
s = p.read_text(encoding="utf-8")
imp = "import com.example.game.OnlineGameScreen\n"
if imp not in s:
    s = s.replace("import com.example.game.LudoViewModel\n", "import com.example.game.LudoViewModel\n" + imp)
pattern = r"(\s*AppTab\.PLAY -> \{\s*)PlayGameScreen\(.*?\n\s*\)\n(\s*\})"
replacement = r"""\1OnlineGameScreen(
                                    isBangla = isBangla,
                                    modifier = Modifier.weight(1f)
                                )
\2"""
s, count = re.subn(pattern, replacement, s, count=1, flags=re.S)
if count != 1:
    raise SystemExit("Could not find PLAY tab PlayGameScreen block")
p.write_text(s, encoding="utf-8")
print("Main PLAY tab now opens the Firebase online game screen.")

# Normalize the online lobby branch after extracting the base project. This keeps
# the generated Android source buildable even when the source ZIP contains the
# earlier malformed brace layout.
screen = Path("app/src/main/java/com/example/game/OnlineGameScreen.kt")
if screen.exists():
    content = screen.read_text(encoding="utf-8")
    start = content.find("        if (roomId.isBlank()) {")
    marker_match = re.search(r"^        } else {$", content[start:] if start >= 0 else "", re.MULTILINE)
    end = (start + marker_match.start()) if marker_match else -1
    if start >= 0 and end >= 0:
        lobby = """        if (roomId.isBlank()) {
            Card(Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(if (isBangla) "অনলাইন ম্যাচ শুরু করুন" else "Start an online match", style = MaterialTheme.typography.titleLarge)
                    Button(
                        onClick = {
                            repo.ensureSignedIn().addOnCompleteListener { auth ->
                                if (auth.isSuccessful) {
                                    handle(repo.createBotRoom()) { result ->
                                        roomId = result["roomId"].toString()
                                        message = if (isBangla) "বট ম্যাচ তৈরি হয়েছে" else "Bot match created"
                                    }
                                } else {
                                    error = auth.exception?.localizedMessage ?: "Sign-in failed"
                                }
                            }
                        },
                        enabled = !busy && uid != null,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(if (isBangla) "সার্ভার বটের সাথে খেলুন" else "Play server bot")
                    }
                }
            }
        } else {"""
        content = content[:start] + lobby + content[end + len("        } else {"): ]
        screen.write_text(content, encoding="utf-8")
        print("Normalized online game lobby Kotlin braces.")


# Replace the online screen with a lobby supporting both server-bot and private human matches.
screen = Path("app/src/main/java/com/example/game/OnlineGameScreen.kt")
screen.parent.mkdir(parents=True, exist_ok=True)
screen.write_text(r'''package com.example.game

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.google.firebase.firestore.DocumentSnapshot
import com.example.game.LudoUiState
import com.example.game.PlayerColor
import com.example.game.SeatControl
import com.example.ui.components.RoyalLudoBoard
import kotlinx.coroutines.delay

@Composable
fun OnlineGameScreen(isBangla: Boolean, modifier: Modifier = Modifier) {
    val repo = remember { OnlineGameRepository() }
    var uid by remember { mutableStateOf<String?>(null) }
    var roomId by remember { mutableStateOf("") }
    var roomCode by remember { mutableStateOf("") }
    var room by remember { mutableStateOf<Map<String, Any>?>(null) }
    var busy by remember { mutableStateOf(false) }
    var message by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }
    val botUid = "ROYEL_BOT"

    fun handle(task: com.google.android.gms.tasks.Task<Map<String, Any>>, success: (Map<String, Any>) -> Unit) {
        busy = true
        error = null
        task.addOnCompleteListener { done ->
            busy = false
            if (done.isSuccessful) done.result?.let(success)
            else error = done.exception?.localizedMessage ?: "Request failed"
        }
    }

    LaunchedEffect(Unit) {
        repo.ensureSignedIn().addOnCompleteListener { task ->
            if (task.isSuccessful) uid = task.result
            else error = task.exception?.localizedMessage ?: "Sign-in failed"
        }
    }

    DisposableEffect(roomId) {
        if (roomId.isBlank()) return@DisposableEffect onDispose { }
        val registration = repo.listenToRoom(roomId) { snapshot: DocumentSnapshot?, e: Exception? ->
            if (e != null) error = e.localizedMessage
            else if (snapshot != null && snapshot.exists()) room = snapshot.data
        }
        onDispose { registration.remove() }
    }

    val players = (room?.get("playerUids") as? List<*>)?.mapNotNull { it as? String } ?: emptyList()
    val currentTurn = room?.get("currentTurnUid") as? String
    val version = (room?.get("stateVersion") as? Number)?.toLong() ?: 0L
    val dice = (room?.get("diceValue") as? Number)?.toInt()
    val pieces = ((room?.get("gameState") as? Map<*, *>)?.get("pieces") as? Map<*, *>)
    val tokens = (pieces?.get(uid) as? List<*>)?.mapNotNull { (it as? Number)?.toInt() } ?: emptyList()
    val myTurn = uid != null && currentTurn == uid
    val active = room?.get("status") == "active"
    val waiting = room?.get("status") == "waiting"
    val winner = room?.get("winnerUid") as? String
    val myColor = PlayerColor.entries.getOrNull(players.indexOf(uid ?: "")) ?: PlayerColor.RED
    val onlineSeats = PlayerColor.entries.associateWith { color ->
        val player = players.getOrNull(color.ordinal)
        when {
            player == null -> SeatControl.OFF
            player == botUid -> SeatControl.BOT
            else -> SeatControl.HUMAN
        }
    }
    val onlinePieces = PlayerColor.entries.associateWith { color ->
        val player = players.getOrNull(color.ordinal)
        (pieces?.get(player) as? List<*>)?.mapNotNull { (it as? Number)?.toInt() } ?: listOf(-1, -1, -1, -1)
    }
    val onlineLegalMoves = if (myTurn && dice != null) {
        tokens.mapIndexedNotNull { index, progress ->
            if ((progress == -1 && dice == 6) || (progress >= 0 && progress < 56 && progress + dice <= 56)) index else null
        }.toSet()
    } else emptySet()
    val onlineUiState = LudoUiState(
        seats = onlineSeats,
        pieces = onlinePieces,
        currentTurn = PlayerColor.entries.getOrNull(players.indexOf(currentTurn ?: "")) ?: PlayerColor.RED,
        diceValue = dice ?: 1,
        hasRolled = dice != null,
        movableTokenIndices = onlineLegalMoves,
        winner = PlayerColor.entries.getOrNull(players.indexOf(winner ?: ""))
    )

    LaunchedEffect(roomId, currentTurn, version, uid) {
        if (roomId.isNotBlank() && uid != null && currentTurn == botUid && active && winner == null) {
            delay(500)
            repo.playBotTurn(roomId, version).addOnFailureListener { error = it.localizedMessage }
        }
    }

    Column(modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(if (isBangla) "অনলাইন লুডু" else "Online Ludo", style = MaterialTheme.typography.headlineMedium)
        Text(if (isBangla) "সার্ভার-নিয়ন্ত্রিত ডাইস ও চাল • লাইভ রুম" else "Server-authoritative dice and moves • live room sync")
        if (roomId.isBlank()) {
            Card(Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(if (isBangla) "অনলাইন ম্যাচ শুরু করুন" else "Start an online match", style = MaterialTheme.typography.titleLarge)
                    Button(onClick = {
                        repo.ensureSignedIn().addOnCompleteListener { auth ->
                            if (auth.isSuccessful) handle(repo.createBotRoom()) { result ->
                                roomId = result["roomId"].toString()
                                message = if (isBangla) "বট ম্যাচ তৈরি হয়েছে" else "Bot match created"
                            } else error = auth.exception?.localizedMessage ?: "Sign-in failed"
                        }
                    }, enabled = !busy && uid != null, modifier = Modifier.fillMaxWidth()) {
                        Text(if (isBangla) "সার্ভার বটের সাথে খেলুন" else "Play server bot")
                    }
                    OutlinedButton(onClick = {
                        repo.ensureSignedIn().addOnCompleteListener { auth ->
                            if (auth.isSuccessful) handle(repo.createRoom()) { result ->
                                roomId = result["roomId"].toString()
                                roomCode = roomId
                                message = if (isBangla) "রুম তৈরি হয়েছে—বন্ধুকে কোড দিন" else "Room created—share the code"
                            } else error = auth.exception?.localizedMessage ?: "Sign-in failed"
                        }
                    }, enabled = !busy && uid != null, modifier = Modifier.fillMaxWidth()) {
                        Text(if (isBangla) "বন্ধুর সাথে খেলার রুম তৈরি করুন" else "Create a private room")
                    }
                    OutlinedTextField(
                        value = roomCode,
                        onValueChange = { roomCode = it.trim() },
                        label = { Text(if (isBangla) "বন্ধুর রুম কোড" else "Friend's room code") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )
                    Button(onClick = {
                        repo.ensureSignedIn().addOnCompleteListener { auth ->
                            if (auth.isSuccessful) handle(repo.joinRoom(roomCode)) {
                                roomId = roomCode
                                message = if (isBangla) "রুমে যোগ দেওয়া হয়েছে" else "Joined room"
                            } else error = auth.exception?.localizedMessage ?: "Sign-in failed"
                        }
                    }, enabled = !busy && uid != null && roomCode.length >= 8, modifier = Modifier.fillMaxWidth()) {
                        Text(if (isBangla) "রুমে যোগ দিন" else "Join room")
                    }
                }
            }
        } else {
            Card(Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(if (isBangla) "রুম কোড" else "Room code", style = MaterialTheme.typography.labelLarge)
                    Text(roomId, style = MaterialTheme.typography.headlineSmall)
                    Text("${if (isBangla) "অবস্থা" else "Status"}: ${room?.get("status") ?: "connecting"}")
                    Text("${if (isBangla) "খেলোয়াড়" else "Players"}: ${players.size}/2")
                    players.forEachIndexed { index, player ->
                        Text("${index + 1}. ${if (player == botUid) "Royal Bot" else if (player == uid) (if (isBangla) "আপনি" else "You") else player.take(8)}")
                    }
                    if (waiting) Text(if (isBangla) "বন্ধুর যোগ দেওয়ার অপেক্ষায়... রুম কোড শেয়ার করুন" else "Waiting for a friend to join. Share the room code.")
                    if (winner != null) Text(if (winner == uid) (if (isBangla) "আপনি জিতেছেন!" else "You won!") else (if (isBangla) "ম্যাচ শেষ" else "Match complete"))
                    else if (active) Text(if (myTurn) (if (isBangla) "আপনার চাল" else "Your turn") else (if (isBangla) "প্রতিপক্ষের চাল" else "Opponent's turn"))
                }
            }
            if (room != null && active) {
                RoyalLudoBoard(
                    uiState = onlineUiState,
                    onTokenClick = { color, index ->
                        if (color == myColor && myTurn && dice != null) {
                            handle(repo.moveToken(roomId, version, index)) {
                                message = if (isBangla) "চাল সম্পন্ন" else "Move completed"
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth()
                )
            }
            if (active && winner == null) {
                Card(Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        Text(if (isBangla) "আপনার চারটি গুটি" else "Your four tokens", style = MaterialTheme.typography.titleMedium)
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            (0..3).forEach { index ->
                                val pos = tokens.getOrNull(index) ?: -1
                                OutlinedButton(onClick = {
                                    if (myTurn && dice != null) handle(repo.moveToken(roomId, version, index)) {
                                        message = if (isBangla) "চাল সম্পন্ন" else "Move completed"
                                    }
                                }, enabled = myTurn && dice != null && ((pos == -1 && dice == 6) || (pos >= 0 && pos < 56 && pos + dice <= 56)),
                                    modifier = Modifier.weight(1f)) {
                                    Text("${index + 1}\n${if (pos < 0) "HOME" else pos}")
                                }
                            }
                        }
                        Text(if (dice == null) (if (isBangla) "ডাইস: এখনো ফেলা হয়নি" else "Dice: not rolled") else "Dice: $dice")
                        Button(onClick = {
                            handle(repo.rollDice(roomId, version)) { message = "Dice: ${it["diceValue"]}" }
                        }, enabled = myTurn && dice == null && !busy, modifier = Modifier.fillMaxWidth()) {
                            Text(if (isBangla) "ডাইস ফেলুন" else "Roll dice")
                        }
                        val canMove = dice != null && tokens.any { (it == -1 && dice == 6) || (it >= 0 && it < 56 && it + dice <= 56) }
                        if (myTurn && dice != null && !canMove) {
                            Button(onClick = {
                                handle(repo.passTurn(roomId, version)) { message = if (isBangla) "চাল পাস" else "Turn passed" }
                            }, modifier = Modifier.fillMaxWidth()) {
                                Text(if (isBangla) "চাল পাস করুন" else "Pass turn")
                            }
                        }
                    }
                }
            }
            OutlinedButton(onClick = { roomId = ""; room = null; message = ""; error = null }, modifier = Modifier.fillMaxWidth()) {
                Text(if (isBangla) "লবি-তে ফিরুন" else "Back to lobby")
            }
        }
        if (busy) LinearProgressIndicator(Modifier.fillMaxWidth())
        if (message.isNotBlank()) Text(message, color = MaterialTheme.colorScheme.primary)
        error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        Text(
            if (isBangla) "সার্ভার-নিয়ন্ত্রিত ডাইস ও চাল। বন্ধুদের সাথে প্রাইভেট রুম অথবা সার্ভার বটের বিপক্ষে খেলুন।" else "Server-authoritative dice and moves. Play a private match with a friend or challenge the server bot.",
            style = MaterialTheme.typography.bodySmall
        )
    }
}
''', encoding="utf-8")
# The product mode is single-player versus the server bot only.
screen = Path("app/src/main/java/com/example/game/OnlineGameScreen.kt")
screen_text = screen.read_text(encoding="utf-8")
lobby_start = screen_text.find('if (roomId.isBlank())')
control_start = screen_text.find('                    OutlinedButton(onClick = {', lobby_start)
join_label = 'Text(if (isBangla) "রুমে যোগ দিন" else "Join room")'
join_start = screen_text.find(join_label, control_start)
control_end = screen_text.find('\\n                    }', join_start)
if min(lobby_start, control_start, join_start, control_end) < 0:
    raise SystemExit("Could not locate private-room controls; refusing a partial UI patch.")
control_end += len('\\n                    }')
screen_text = screen_text[:control_start] + screen_text[control_end:]
if removed != 1:
    raise SystemExit("Could not remove private-room controls; refusing a partial UI patch.")
screen_text = screen_text.replace(
    'if (waiting) Text(if (isBangla) "বন্ধুর যোগ দেওয়ার অপেক্ষায়... রুম কোড শেয়ার করুন" else "Waiting for a friend to join. Share the room code.")',
    ''
)
screen_text = screen_text.replace(
    '"সার্ভার-নিয়ন্ত্রিত ডাইস ও চাল। বন্ধুদের সাথে প্রাইভেট রুম অথবা সার্ভার বটের বিপক্ষে খেলুন."',
    '"সার্ভার-নিয়ন্ত্রিত ডাইস ও চাল। এককভাবে Royal Expert Bot-এর বিপক্ষে খেলুন."'
).replace(
    '"Server-authoritative dice and moves. Play a private match with a friend or challenge the server bot."',
    '"Server-authoritative dice and moves. Challenge the Royal Expert Bot in single-player mode."'
)
screen.write_text(screen_text, encoding="utf-8")
print("Single-player bot-only lobby applied; private-room controls removed.")

print("Online lobby now supports private two-player rooms and server-bot matches.")
