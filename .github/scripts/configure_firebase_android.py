#!/usr/bin/env python3
from pathlib import Path
import tomllib

root = Path(".")
gradle = root / "app/build.gradle.kts"
s = gradle.read_text()
s = s.replace("// implementation(platform(libs.firebase.bom))", "implementation(platform(libs.firebase.bom))")
s = s.replace("// implementation(libs.firebase.firestore)", "implementation(libs.firebase.firestore)")
s = s.replace("// implementation(libs.firebase.auth)", "implementation(libs.firebase.auth)")
if "implementation(libs.firebase.functions)" not in s:
    s = s.replace("implementation(libs.firebase.auth)", "implementation(libs.firebase.auth)\n  implementation(libs.firebase.functions)")
gradle.write_text(s)

catalog = root / "gradle/libs.versions.toml"
s = catalog.read_text()
if "firebase-functions =" not in s:
    needle = 'firebase-firestore = { group = "com.google.firebase", name = "firebase-firestore" }'
    if needle not in s:
        raise SystemExit("Firebase Firestore version-catalog entry not found")
    s = s.replace(needle, needle + '\n' + 'firebase-functions = { group = "com.google.firebase", name = "firebase-functions" }')
tomllib.loads(s)
catalog.write_text(s)

manifest = root / "app/src/main/AndroidManifest.xml"
s = manifest.read_text()
if "android.permission.INTERNET" not in s:
    s = s.replace("    <application", '    <uses-permission android:name="android.permission.INTERNET" />\n\n    <application', 1)
manifest.write_text(s)

backend = root / "app/src/main/java/com/example/FirebaseBackend.kt"
backend.parent.mkdir(parents=True, exist_ok=True)
backend.write_text("""package com.example

import android.content.Context
import com.google.android.gms.tasks.Task
import com.google.firebase.FirebaseApp
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.FirebaseUser
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.functions.FirebaseFunctions

object FirebaseBackend {
    @Volatile private var app: FirebaseApp? = null

    @Synchronized
    fun initialize(context: Context): Boolean {
        if (app != null) return true
        app = try { FirebaseApp.initializeApp(context.applicationContext) } catch (_: Exception) { null }
        return app != null
    }

    val isConfigured: Boolean get() = app != null
    fun auth(): FirebaseAuth? = app?.let { FirebaseAuth.getInstance(it) }
    fun firestore(): FirebaseFirestore? = app?.let { FirebaseFirestore.getInstance(it) }
    fun functions(region: String = "us-central1"): FirebaseFunctions? =
        app?.let { FirebaseFunctions.getInstance(it, region) }

    fun signInAnonymously(): Task<FirebaseUser>? = auth()?.signInAnonymously()?.continueWith { task ->
        if (!task.isSuccessful) throw task.exception ?: IllegalStateException("Anonymous sign-in failed")
        task.result.user ?: throw IllegalStateException("Firebase returned no user")
    }
}
""")

activity = root / "app/src/main/java/com/example/MainActivity.kt"
s = activity.read_text()
if "FirebaseBackend.initialize(applicationContext)" not in s:
    needle = "        enableEdgeToEdge()\n"
    if needle not in s:
        raise SystemExit("MainActivity initialization point not found")
    s = s.replace(needle, needle + "        FirebaseBackend.initialize(applicationContext)\n", 1)
activity.write_text(s)
print("Firebase Android SDK integration configured.")
