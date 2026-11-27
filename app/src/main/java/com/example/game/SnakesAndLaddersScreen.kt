package com.example.game

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import kotlin.random.Random

private data class LadderPlayer(val name: String, val color: Color, val bot: Boolean, val position: Int = 0)

@Composable
fun SnakesAndLaddersScreen(isBangla: Boolean, modifier: Modifier = Modifier) {
    val starts = mapOf(4 to 14, 9 to 31, 20 to 38, 28 to 84, 40 to 59, 51 to 67, 63 to 81, 71 to 91)
    val drops = mapOf(17 to 7, 54 to 34, 62 to 19, 64 to 60, 87 to 24, 93 to 73, 95 to 75, 99 to 78)
    var count by remember { mutableIntStateOf(2) }
    var players by remember { mutableStateOf(listOf(
        LadderPlayer(if (isBangla) "আপনি" else "You", Color(0xFFE9B949), false),
        LadderPlayer(if (isBangla) "বট ১" else "Bot 1", Color(0xFF55C6A9), true),
        LadderPlayer(if (isBangla) "বট ২" else "Bot 2", Color(0xFFEA7180), true),
        LadderPlayer(if (isBangla) "বট ৩" else "Bot 3", Color(0xFF70A7F5), true)
    )) }
    var turn by remember { mutableIntStateOf(0) }
    var dice by remember { mutableIntStateOf(0) }
    var rolling by remember { mutableStateOf(false) }
    var message by remember { mutableStateOf(if (isBangla) "পাশা ফেলুন" else "Roll the dice") }
    var winner by remember { mutableIntStateOf(-1) }
    val active = players.take(count)
    fun roll() {
        if (rolling || winner >= 0) return
        rolling = true
    }
    LaunchedEffect(rolling) {
        if (rolling) {
            repeat(8) { dice = Random.nextInt(1, 7); delay(65) }
            val value = dice
            val old = active[turn].position
            val raw = old + value
            val landed = if (raw > 100) old else drops[raw] ?: starts[raw] ?: raw
            players = players.mapIndexed { i, p -> if (i == turn) p.copy(position = landed) else p }
            message = when {
                raw > 100 -> if (isBangla) "১০০-তে পৌঁছাতে সঠিক সংখ্যা লাগবে" else "Need exact roll to reach 100"
                drops.containsKey(raw) -> if (isBangla) "সাপ! $raw থেকে $landed" else "Snake! $raw to $landed"
                starts.containsKey(raw) -> if (isBangla) "সিঁড়ি! $raw থেকে $landed" else "Ladder! $raw to $landed"
                landed == 100 -> if (isBangla) "${active[turn].name} জিতেছে!" else "${active[turn].name} wins!"
                else -> if (isBangla) "${active[turn].name}: $landed ঘর" else "${active[turn].name}: $landed"
            }
            if (landed == 100) winner = turn
            else if (value != 6) turn = (turn + 1) % count
            rolling = false
        }
    }
    Column(modifier.fillMaxSize().padding(12.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(if (isBangla) "🐍 সাপ-লুডু" else "🐍 Snakes & Ladders", style = MaterialTheme.typography.headlineSmall, color = Color(0xFFE9B949), fontWeight = FontWeight.Bold)
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(if (isBangla) "খেলোয়াড়" else "Players", color = Color.White)
            (2..4).forEach { n -> FilterChip(selected = count == n, onClick = { if (winner < 0) { count = n; turn %= n } }, label = { Text("$n") }) }
            Spacer(Modifier.weight(1f))
            Text(if (isBangla) "অফলাইন • বটসহ" else "Offline • Bots included", color = Color(0xFF9BAAC3), style = MaterialTheme.typography.labelSmall)
        }
        LazyVerticalGrid(columns = GridCells.Fixed(10), modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(3.dp), horizontalArrangement = Arrangement.spacedBy(3.dp)) {
            items((100 downTo 1).toList()) { cell ->
                val row = (100 - cell) / 10
                val col = (100 - cell) % 10
                val number = if (row % 2 == 0) cell else row * 10 + (11 - col)
                val occupants = active.filter { it.position == number }
                Box(Modifier.aspectRatio(1f).border(1.dp, Color(0xFF52627C), RoundedCornerShape(4.dp)).background(
                    when { starts.containsKey(number) -> Color(0xFF285B4D); drops.containsKey(number) -> Color(0xFF713B49); else -> if ((row + col) % 2 == 0) Color(0xFF172943) else Color(0xFF203653) },
                    RoundedCornerShape(4.dp)), contentAlignment = Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("$number", color = Color.White, style = MaterialTheme.typography.labelSmall)
                        if (starts.containsKey(number)) Text("🪜", style = MaterialTheme.typography.labelSmall)
                        if (drops.containsKey(number)) Text("🐍", style = MaterialTheme.typography.labelSmall)
                        if (occupants.isNotEmpty()) Text(occupants.joinToString("") { "●" }, color = occupants.first().color)
                    }
                }
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
            Text("🎲 $dice", color = Color(0xFFE9B949), style = MaterialTheme.typography.headlineMedium)
            Column(Modifier.weight(1f)) {
                Text(message, color = Color.White)
                Text(if (winner >= 0) (if (isBangla) "নতুন গেম শুরু করুন" else "Start a new game") else "${active[turn].name} • ${if (isBangla) "টার্ন" else "turn"}", color = Color(0xFF9BAAC3))
            }
            Button(onClick = { if (winner >= 0) { players = players.map { it.copy(position = 0) }; turn = 0; winner = -1; dice = 0; message = if (isBangla) "পাশা ফেলুন" else "Roll the dice" } else roll() }, enabled = !rolling) {
                Text(if (winner >= 0) (if (isBangla) "আবার" else "Restart") else (if (isBangla) "পাশা" else "Roll"))
            }
        }
        Text(active.joinToString("   ") { "${it.name}: ${it.position}" }, color = Color(0xFFB8C5D8), style = MaterialTheme.typography.bodySmall)
    }
}

@Composable
fun RoyalGameHub(isBangla: Boolean, modifier: Modifier = Modifier) {
    var selected by remember { mutableIntStateOf(0) }
    Column(modifier.fillMaxSize()) {
        Row(Modifier.fillMaxWidth().padding(horizontal = 12.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            FilterChip(selected = selected == 0, onClick = { selected = 0 }, label = { Text(if (isBangla) "♟ লুডু" else "♟ Ludo") })
            FilterChip(selected = selected == 1, onClick = { selected = 1 }, label = { Text(if (isBangla) "🐍 সাপ-লুডু" else "🐍 Snakes & Ladders") })
        }
        if (selected == 0) OnlineGameScreen(isBangla = isBangla, modifier = Modifier.weight(1f))
        else SnakesAndLaddersScreen(isBangla = isBangla, modifier = Modifier.weight(1f))
    }
}
