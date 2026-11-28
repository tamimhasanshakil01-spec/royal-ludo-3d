package com.example.game

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.functions.FirebaseFunctions
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

private const val ADMIN_EMAIL = "tamimhasanshakil01@gmail.com"
private data class PlayerRow(val uid:String,val name:String,val email:String,val phone:String,val balance:Long)
private data class LedgerRow(val direction:String,val amount:Long,val note:String,val balance:Long,val time:Long)

@Composable
fun AdminDashboardScreen(isBangla:Boolean,onBack:()->Unit,modifier:Modifier=Modifier) {
    val auth= remember { FirebaseAuth.getInstance() }
    val fn= remember { FirebaseFunctions.getInstance("us-central1") }
    var email by remember { mutableStateOf(ADMIN_EMAIL) }
    var password by remember { mutableStateOf("") }
    var allowed by remember { mutableStateOf(false) }
    var busy by remember { mutableStateOf(false) }
    var players by remember { mutableStateOf(emptyList<PlayerRow>()) }
    var selected by remember { mutableStateOf("") }
    var ledger by remember { mutableStateOf(emptyList<LedgerRow>()) }
    var amount by remember { mutableStateOf("") }
    var note by remember { mutableStateOf("") }
    var direction by remember { mutableStateOf("credit") }
    var error by remember { mutableStateOf<String?>(null) }
    var message by remember { mutableStateOf("") }

    fun loadLedger(uid:String) {
        fn.getHttpsCallable("adminGetPlayerLedger").call(mapOf("playerUid" to uid,"limit" to 30))
            .addOnCompleteListener { t ->
                if(t.isSuccessful) {
                    @Suppress("UNCHECKED_CAST")
                    val rows=(t.result?.data as? Map<String,Any>)?.get("transactions") as? List<Map<String,Any>> ?: emptyList()
                    ledger=rows.map { r -> LedgerRow(r["direction"].toString(),(r["amount"] as? Number)?.toLong()?:0L,r["note"].toString(),(r["balanceAfter"] as? Number)?.toLong()?:0L,(r["createdAt"] as? Number)?.toLong()?:0L) }
                } else error=t.exception?.localizedMessage
            }
    }
    fun loadPlayers() {
        busy=true; error=null
        fn.getHttpsCallable("adminListPlayers").call(mapOf("limit" to 100)).addOnCompleteListener { t ->
            busy=false
            if(!t.isSuccessful) error=t.exception?.localizedMessage ?: "Player list failed"
            else {
                @Suppress("UNCHECKED_CAST")
                val rows=(t.result?.data as? Map<String,Any>)?.get("players") as? List<Map<String,Any>> ?: emptyList()
                players=rows.mapNotNull { r -> val uid=r["uid"]?.toString() ?: return@mapNotNull null
                    PlayerRow(uid,r["displayName"]?.toString() ?: "Player",r["email"]?.toString().orEmpty(),r["phoneNumber"]?.toString().orEmpty(),(r["balance"] as? Number)?.toLong()?:0L) }
                if(selected.isBlank() && players.isNotEmpty()) selected=players.first().uid
                if(selected.isNotBlank()) loadLedger(selected)
            }
        }
    }
    fun verifyAdmin() {
        val user=auth.currentUser
        if(user==null || !user.email.equals(ADMIN_EMAIL,true) || user.isEmailVerified!=true) {
            auth.signOut(); busy=false; allowed=false
            error=if(isBangla) "যাচাইকৃত নির্ধারিত অ্যাডমিন ইমেইল ব্যবহার করুন।" else "Use the verified designated admin email."
            return
        }
        user.getIdToken(true).addOnCompleteListener { t ->
            busy=false
            if(!t.isSuccessful) error=t.exception?.localizedMessage
            else if(t.result?.claims?.get("admin")!=true) error=if(isBangla) "Firebase-এ Admin অনুমতি এখনো দেওয়া হয়নি।" else "Firebase admin claim is not assigned yet."
            else { allowed=true; loadPlayers() }
        }
    }
    LaunchedEffect(Unit) {
        val u=auth.currentUser
        if(u?.email.equals(ADMIN_EMAIL,true) && u?.isEmailVerified==true) { busy=true; verifyAdmin() }
    }

    Column(modifier.fillMaxSize().padding(16.dp),verticalArrangement=Arrangement.spacedBy(10.dp)) {
        Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween) {
            Text(if(isBangla) "রয়্যাল অ্যাডমিন প্যানেল" else "ROYAL ADMIN PANEL",style=MaterialTheme.typography.titleLarge)
            TextButton(onClick=onBack) { Text(if(isBangla) "ফিরে যান" else "Back") }
        }
        Text(if(isBangla) "নিরাপদ নিয়ন্ত্রণ • কাল্পনিক গেম ব্যালেন্স" else "Secure controls • fictional game balance",style=MaterialTheme.typography.bodySmall)
        if(!allowed) {
            OutlinedTextField(email,{email=it.trim()},label={Text("Admin email")},singleLine=true,modifier=Modifier.fillMaxWidth())
            OutlinedTextField(password,{password=it},label={Text(if(isBangla) "পাসওয়ার্ড" else "Password")},visualTransformation=PasswordVisualTransformation(),singleLine=true,modifier=Modifier.fillMaxWidth())
            Button(enabled=!busy && email.equals(ADMIN_EMAIL,true) && password.length>=6,onClick={
                busy=true; error=null
                auth.signInWithEmailAndPassword(ADMIN_EMAIL,password).addOnCompleteListener { t ->
                    if(!t.isSuccessful) { busy=false; error=t.exception?.localizedMessage ?: "Sign-in failed" } else verifyAdmin()
                }
            },modifier=Modifier.fillMaxWidth()) { Text(if(busy) "…" else if(isBangla) "অ্যাডমিন লগইন" else "Admin sign in") }
            Text(if(isBangla) "নির্ধারিত ইমেইল, ইমেইল যাচাই এবং Firebase admin claim—তিনটিই প্রয়োজন।" else "Designated email, verified email and Firebase admin claim are required.",style=MaterialTheme.typography.bodySmall)
        } else {
            Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween) {
                Text(if(isBangla) "প্লেয়ার তালিকা" else "Players",style=MaterialTheme.typography.titleMedium)
                TextButton(onClick={loadPlayers()}) { Text(if(isBangla) "রিফ্রেশ" else "Refresh") }
            }
            if(busy) LinearProgressIndicator(Modifier.fillMaxWidth())
            LazyColumn(Modifier.weight(1f,fill=false).fillMaxWidth()) {
                items(players,key={it.uid}) { p ->
                    Card(onClick={selected=p.uid;loadLedger(p.uid)},modifier=Modifier.fillMaxWidth()) {
                        Column(Modifier.padding(10.dp)) {
                            Text(p.name,style=MaterialTheme.typography.titleMedium)
                            Text(p.email.ifBlank { p.phone.ifBlank { p.uid } },style=MaterialTheme.typography.bodySmall)
                            Text("৳ ${p.balance}",style=MaterialTheme.typography.titleMedium)
                            if(selected==p.uid) Text(if(isBangla) "নির্বাচিত" else "Selected",color=MaterialTheme.colorScheme.primary)
                        }
                    }
                }
            }
            Text(if(isBangla) "নির্বাচিত UID: $selected" else "Selected UID: $selected",style=MaterialTheme.typography.bodySmall)
            Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
                FilterChip(direction=="credit",{direction="credit"},label={Text(if(isBangla) "টাকা যোগ" else "Add")})
                FilterChip(direction=="debit",{direction="debit"},label={Text(if(isBangla) "টাকা কমাও" else "Deduct")})
            }
            OutlinedTextField(amount,{amount=it.filter(Char::isDigit).take(7)},label={Text(if(isBangla) "পরিমাণ" else "Amount")},singleLine=true,modifier=Modifier.fillMaxWidth())
            OutlinedTextField(note,{note=it.take(120)},label={Text(if(isBangla) "কারণ / নোট" else "Reason / note")},singleLine=true,modifier=Modifier.fillMaxWidth())
            Button(enabled=!busy && selected.isNotBlank() && (amount.toLongOrNull()?:0L) in 1..1_000_000 && note.trim().length>=3,onClick={
                busy=true; error=null
                fn.getHttpsCallable("adminAdjustFictionalWallet").call(mapOf("playerUid" to selected,"direction" to direction,"amount" to (amount.toLongOrNull()?:0L),"note" to note.trim())).addOnCompleteListener { t ->
                    busy=false
                    if(!t.isSuccessful) error=t.exception?.localizedMessage ?: "Update failed"
                    else { message=if(isBangla) "ভার্চুয়াল ব্যালেন্স আপডেট হয়েছে।" else "Fictional balance updated."; amount="";note="";loadPlayers();loadLedger(selected) }
                }
            },modifier=Modifier.fillMaxWidth()) { Text(if(isBangla) "পরিবর্তন সংরক্ষণ" else "Save adjustment") }
            Text(if(isBangla) "সাম্প্রতিক লেনদেন" else "Recent transactions",style=MaterialTheme.typography.titleMedium)
            LazyColumn(Modifier.weight(0.8f,fill=false).fillMaxWidth()) {
                items(ledger) { x ->
                    val date=if(x.time>0) SimpleDateFormat("dd MMM yyyy, hh:mm a",Locale.getDefault()).format(Date(x.time)) else "—"
                    Text("${if(x.direction=="credit") "+" else "−"}৳${x.amount} • ${x.note} • ৳${x.balance} • $date",style=MaterialTheme.typography.bodySmall)
                }
            }
            OutlinedButton(onClick={auth.signOut();allowed=false;password="";players=emptyList();ledger=emptyList()},modifier=Modifier.fillMaxWidth()) { Text(if(isBangla) "অ্যাডমিন লগআউট" else "Admin sign out") }
        }
        if(message.isNotBlank()) Text(message,color=MaterialTheme.colorScheme.primary)
        error?.let { Text(it,color=MaterialTheme.colorScheme.error) }
        Text(if(isBangla) "শুধু উত্তোলন/স্থানান্তর-অযোগ্য কাল্পনিক গেম ব্যালেন্স। বাস্তব টাকা, বাজি বা ক্যাশ-আউট নয়।" else "Fictional, non-withdrawable game balance only. No real money, wagers or cash-out.",style=MaterialTheme.typography.bodySmall)
    }
}
