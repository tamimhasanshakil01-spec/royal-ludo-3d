from pathlib import Path

root = Path("app/src/main/java/com/example/game")
account = root / "AccountAccessScreen.kt"
repo = root / "OnlineGameRepository.kt"

s = account.read_text(encoding="utf-8")
# Keep the existing verified-email implementation as a base and add a phone OTP
# entry point in the same screen. Fail loudly if the expected generated file changes.
if "private enum class AccountMethod" in s:
    print("Phone authentication is already integrated; no changes needed.")
    raise SystemExit(0)

s = r'''package com.example.game

import android.app.Activity
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.PhoneAuthOptions
import com.google.firebase.auth.PhoneAuthProvider
import com.google.firebase.functions.FirebaseFunctions
import java.util.concurrent.TimeUnit

private enum class AccountMethod { EMAIL, PHONE }

@Composable
fun OnlineGameScreen(isBangla: Boolean, modifier: Modifier = Modifier) {
    val auth = remember { FirebaseAuth.getInstance() }
    var signedIn by remember {
        mutableStateOf(auth.currentUser != null &&
            (auth.currentUser?.isEmailVerified == true || !auth.currentUser?.phoneNumber.isNullOrBlank()))
    }
    if (signedIn) {
        OnlineGameContent(isBangla = isBangla, modifier = modifier)
    } else {
        AccountAccessScreen(isBangla = isBangla, modifier = modifier) {
            signedIn = auth.currentUser != null &&
                (auth.currentUser?.isEmailVerified == true || !auth.currentUser?.phoneNumber.isNullOrBlank())
        }
    }
}

@Composable
private fun AccountAccessScreen(isBangla: Boolean, modifier: Modifier, onSignedIn: () -> Unit) {
    val auth = remember { FirebaseAuth.getInstance() }
    val functions = remember { FirebaseFunctions.getInstance("us-central1") }
    val context = LocalContext.current
    var method by remember { mutableStateOf(AccountMethod.EMAIL) }
    var register by remember { mutableStateOf(true) }
    var name by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var phone by remember { mutableStateOf("") }
    var otp by remember { mutableStateOf("") }
    var verificationId by remember { mutableStateOf<String?>(null) }
    var busy by remember { mutableStateOf(false) }
    var message by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }

    fun savePhoneProfile() {
        val user = auth.currentUser
        if (user == null) {
            busy = false
            error = if (isBangla) "লগইন সেশন পাওয়া যায়নি।" else "Could not create an account session."
            return
        }
        val displayName = name.trim().ifBlank { user.phoneNumber ?: "Royal Player" }
        functions.getHttpsCallable("registerProfile").call(mapOf("displayName" to displayName))
            .addOnCompleteListener { result ->
                busy = false
                if (result.isSuccessful) onSignedIn()
                else error = result.exception?.localizedMessage ?: "Could not save player profile"
            }
    }

    Column(
        modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(if (isBangla) "Royal Ludo 3D অ্যাকাউন্ট" else "Royal Ludo 3D Account",
            style = MaterialTheme.typography.headlineSmall)
        Text(if (isBangla) "ইমেইল অথবা মোবাইল নম্বর দিয়ে স্থায়ী অ্যাকাউন্ট খুলুন।"
             else "Create a permanent account with email or mobile number.")

        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            FilterChip(
                selected = method == AccountMethod.EMAIL,
                onClick = { method = AccountMethod.EMAIL; message = ""; error = null },
                label = { Text(if (isBangla) "ইমেইল" else "Email") }
            )
            FilterChip(
                selected = method == AccountMethod.PHONE,
                onClick = { method = AccountMethod.PHONE; message = ""; error = null },
                label = { Text(if (isBangla) "ফোন নম্বর" else "Phone number") }
            )
        }

        if (method == AccountMethod.EMAIL) {
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
                                    else "Could not send verification email: " + sent.exception?.localizedMessage
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
            Text(if (isBangla) "ইমেইল যাচাই বাধ্যতামূলক।" else "Email verification is required.",
                style = MaterialTheme.typography.bodySmall)
        } else {
            if (register) {
                OutlinedTextField(value = name, onValueChange = { name = it },
                    label = { Text(if (isBangla) "আপনার নাম" else "Display name") },
                    singleLine = true, modifier = Modifier.fillMaxWidth())
            }
            OutlinedTextField(
                value = phone, onValueChange = { phone = it.filter { ch -> ch.isDigit() || ch == '+' } },
                label = { Text(if (isBangla) "মোবাইল নম্বর (+8801XXXXXXXXX)" else "Mobile number (+8801XXXXXXXXX)") },
                singleLine = true, modifier = Modifier.fillMaxWidth()
            )
            if (verificationId == null) {
                Button(enabled = !busy && phone.filter { it.isDigit() }.length >= 10 && (!register || name.isNotBlank()),
                    modifier = Modifier.fillMaxWidth(), onClick = {
                        val raw = phone.trim().replace(" ", "").replace("-", "")
                        val normalized = when {
                            raw.startsWith("+") -> raw
                            raw.startsWith("880") -> "+" + raw
                            raw.startsWith("0") -> "+88" + raw
                            else -> "+" + raw
                        }
                        val activity = context as? Activity
                        if (activity == null) {
                            error = "Phone verification requires an Android Activity."
                        } else {
                            busy = true
                            error = null
                            message = ""
                            val callbacks = object : PhoneAuthProvider.OnVerificationStateChangedCallbacks() {
                                override fun onVerificationCompleted(credential: com.google.firebase.auth.PhoneAuthCredential) {
                                    auth.signInWithCredential(credential).addOnCompleteListener { result ->
                                        if (result.isSuccessful) savePhoneProfile()
                                        else {
                                            busy = false
                                            error = result.exception?.localizedMessage ?: "Phone sign-in failed"
                                        }
                                    }
                                }
                                override fun onVerificationFailed(e: com.google.firebase.FirebaseException) {
                                    busy = false
                                    error = e.localizedMessage ?: "Could not send SMS verification code."
                                }
                                override fun onCodeSent(id: String, token: PhoneAuthProvider.ForceResendingToken) {
                                    verificationId = id
                                    busy = false
                                    message = if (isBangla) "SMS-এ ৬ সংখ্যার OTP পাঠানো হয়েছে।" else "A 6-digit SMS code has been sent."
                                }
                            }
                            val options = PhoneAuthOptions.newBuilder(auth)
                                .setPhoneNumber(normalized)
                                .setTimeout(60L, TimeUnit.SECONDS)
                                .setActivity(activity)
                                .setCallbacks(callbacks)
                                .build()
                            PhoneAuthProvider.verifyPhoneNumber(options)
                        }
                    }) {
                    Text(if (busy) (if (isBangla) "পাঠানো হচ্ছে..." else "Sending...")
                         else (if (isBangla) "SMS OTP পাঠান" else "Send SMS OTP"))
                }
            } else {
                OutlinedTextField(value = otp, onValueChange = { otp = it.filter(Char::isDigit).take(6) },
                    label = { Text(if (isBangla) "৬ সংখ্যার OTP" else "6-digit OTP") },
                    singleLine = true, modifier = Modifier.fillMaxWidth())
                Button(enabled = !busy && otp.length == 6,
                    modifier = Modifier.fillMaxWidth(), onClick = {
                        busy = true
                        error = null
                        val credential = PhoneAuthProvider.getCredential(verificationId!!, otp)
                        auth.signInWithCredential(credential).addOnCompleteListener { result ->
                            if (result.isSuccessful) savePhoneProfile()
                            else {
                                busy = false
                                error = result.exception?.localizedMessage ?: "Invalid verification code."
                            }
                        }
                    }) {
                    Text(if (busy) (if (isBangla) "যাচাই হচ্ছে..." else "Verifying...")
                         else (if (isBangla) "OTP যাচাই করে লগইন" else "Verify OTP & sign in"))
                }
                TextButton(onClick = { verificationId = null; otp = ""; message = "" }) {
                    Text(if (isBangla) "নম্বর পরিবর্তন করুন" else "Change phone number")
                }
            }
            Text(if (isBangla) "বাংলাদেশি নম্বর 01XXXXXXXXX অথবা আন্তর্জাতিক +8801XXXXXXXXX লিখুন। SMS OTP যাচাই বাধ্যতামূলক।"
                 else "Enter a Bangladesh number (01XXXXXXXXX) or international format (+8801XXXXXXXXX). SMS OTP verification is required.",
                style = MaterialTheme.typography.bodySmall)
        }

        if (message.isNotBlank()) Text(message, color = MaterialTheme.colorScheme.primary)
        error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
    }
}
'''
account.write_text(s, encoding="utf-8")

rs = repo.read_text(encoding="utf-8")
old = "if (current != null && current.isEmailVerified)"
new = "if (current != null && (current.isEmailVerified || !current.phoneNumber.isNullOrBlank()))"
if old in rs:
    rs = rs.replace(old, new, 1)
    rs = rs.replace("A verified permanent account is required.", "A verified email or phone account is required.")
elif new not in rs:
    raise SystemExit("Could not find ensureSignedIn verification gate in OnlineGameRepository.kt")
repo.write_text(rs, encoding="utf-8")
print("Integrated phone-number SMS OTP and kept verified-email login.")
