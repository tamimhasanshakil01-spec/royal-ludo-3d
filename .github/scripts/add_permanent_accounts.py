from pathlib import Path

repo = Path("app/src/main/java/com/example/game/OnlineGameRepository.kt")
s = repo.read_text(encoding="utf-8")
start = s.index("    fun ensureSignedIn(): Task<String> {")
end = s.index("\n    fun createRoom()", start)
s = s[:start] + """    fun currentUid(): String? = auth.currentUser?.uid

    fun registerProfile(displayName: String): Task<Map<String, Any>> =
        call("registerProfile", mapOf("displayName" to displayName.trim()))

    fun ensureSignedIn(): Task<String> {
        val current = auth.currentUser
        if (current != null && current.isEmailVerified) {
            return com.google.android.gms.tasks.Tasks.forResult(current.uid)
        }
        return com.google.android.gms.tasks.Tasks.forException(
            IllegalStateException("A verified permanent account is required.")
        )
    }
""" + s[end:]
repo.write_text(s, encoding="utf-8")

screen = Path("app/src/main/java/com/example/game/OnlineGameScreen.kt")
s = screen.read_text(encoding="utf-8")
s = s.replace("fun OnlineGameScreen(isBangla: Boolean, modifier: Modifier = Modifier) {",
              "fun OnlineGameContent(isBangla: Boolean, modifier: Modifier = Modifier) {", 1)
screen.write_text(s, encoding="utf-8")

account = Path("app/src/main/java/com/example/game/AccountAccessScreen.kt")
account.write_text(r'''package com.example.game

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.functions.FirebaseFunctions

@Composable
fun OnlineGameScreen(isBangla: Boolean, modifier: Modifier = Modifier) {
    val auth = remember { FirebaseAuth.getInstance() }
    var signedIn by remember { mutableStateOf(auth.currentUser != null && auth.currentUser?.isEmailVerified == true) }
    if (signedIn) {
        OnlineGameContent(isBangla = isBangla, modifier = modifier)
    } else {
        AccountAccessScreen(isBangla = isBangla, modifier = modifier) {
            signedIn = auth.currentUser != null && auth.currentUser?.isEmailVerified == true
        }
    }
}

@Composable
private fun AccountAccessScreen(isBangla: Boolean, modifier: Modifier, onSignedIn: () -> Unit) {
    val auth = remember { FirebaseAuth.getInstance() }
    val functions = remember { FirebaseFunctions.getInstance("us-central1") }
    var register by remember { mutableStateOf(true) }
    var name by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var message by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }

    Column(modifier.fillMaxSize().padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(if (isBangla) "Royal Ludo 3D অ্যাকাউন্ট" else "Royal Ludo 3D Account",
            style = MaterialTheme.typography.headlineSmall)
        Text(if (isBangla) "অনলাইন খেলতে স্থায়ী অ্যাকাউন্ট খুলুন বা লগইন করুন।" else "Create a permanent account or sign in to play online.")
        if (register) {
            OutlinedTextField(value = name, onValueChange = { name = it },
                label = { Text(if (isBangla) "আপনার নাম" else "Display name") },
                singleLine = true, modifier = Modifier.fillMaxWidth())
        }
        OutlinedTextField(value = email, onValueChange = { email = it.trim() },
            label = { Text(if (isBangla) "ইমেইল" else "Email") },
            singleLine = true, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(value = password, onValueChange = { password = it },
            label = { Text(if (isBangla) "পাসওয়ার্ড (কমপক্ষে ৬ অক্ষর)" else "Password (at least 6 characters)") },
            visualTransformation = PasswordVisualTransformation(), singleLine = true,
            modifier = Modifier.fillMaxWidth())
        Button(enabled = !busy && email.contains("@") && password.length >= 6 && (!register || name.isNotBlank()),
            modifier = Modifier.fillMaxWidth(), onClick = {
                busy = true
                error = null
                message = ""
                val task = if (register) auth.createUserWithEmailAndPassword(email, password)
                           else auth.signInWithEmailAndPassword(email, password)
                task.addOnCompleteListener { result ->
                    if (!result.isSuccessful) {
                        busy = false
                        error = result.exception?.localizedMessage ?: "Authentication failed"
                    } else {
                        val user = auth.currentUser
                        if (user == null) {
                            busy = false
                            error = "Account session could not be created."
                        } else if (!user.isEmailVerified) {
                            user.sendEmailVerification().addOnCompleteListener { sent ->
                                auth.signOut()
                                busy = false
                                message = if (sent.isSuccessful)
                                    (if (isBangla) "ইমেইলে যাচাই লিংক পাঠানো হয়েছে। যাচাই করে লগইন করুন।" else "Verification link sent. Verify your email, then sign in.")
                                else "Could not send verification email: \${sent.exception?.localizedMessage}"
                            }
                        } else {
                            val profileName = if (register) name.trim() else (user.displayName ?: email.substringBefore("@"))
                            functions.getHttpsCallable("registerProfile").call(mapOf("displayName" to profileName))
                                .addOnCompleteListener { profile ->
                                    busy = false
                                    if (profile.isSuccessful) onSignedIn()
                                    else error = profile.exception?.localizedMessage ?: "Could not save player profile"
                                }
                        }
                    }
                }
            }) {
            Text(if (busy) (if (isBangla) "অপেক্ষা করুন..." else "Please wait...")
                 else if (register) (if (isBangla) "অ্যাকাউন্ট খুলুন" else "Create account")
                 else (if (isBangla) "লগইন" else "Sign in"))
        }
        TextButton(onClick = { register = !register; message = ""; error = null }) {
            Text(if (register) (if (isBangla) "আগে অ্যাকাউন্ট আছে? লগইন" else "Already registered? Sign in")
                 else (if (isBangla) "নতুন অ্যাকাউন্ট খুলুন" else "Create a new account"))
        }
        if (message.isNotBlank()) Text(message, color = MaterialTheme.colorScheme.primary)
        error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        Text(if (isBangla) "ইমেইল যাচাই বাধ্যতামূলক। Player ID আপনার Firebase UID।" else "Email verification is required. Your Player ID is your Firebase UID.",
            style = MaterialTheme.typography.bodySmall)
    }
}
''', encoding="utf-8")
print("Permanent verified-email account gate generated.")
