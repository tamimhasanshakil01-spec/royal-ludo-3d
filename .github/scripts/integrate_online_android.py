from pathlib import Path

gradle = Path("app/build.gradle.kts")
s = gradle.read_text(encoding="utf-8")
s = s.replace("// implementation(platform(libs.firebase.bom))", "implementation(platform(libs.firebase.bom))")
s = s.replace("// implementation(libs.firebase.auth)", "implementation(libs.firebase.auth)")
s = s.replace("// implementation(libs.firebase.firestore)", "implementation(libs.firebase.firestore)\n  implementation(libs.firebase.functions)")
gradle.write_text(s, encoding="utf-8")

catalog = Path("gradle/libs.versions.toml")
s = catalog.read_text(encoding="utf-8")
if "firebase-functions =" not in s:
    s = s.replace('firebase-firestore = { group = "com.google.firebase", name = "firebase-firestore" }',
                  'firebase-firestore = { group = "com.google.firebase", name = "firebase-firestore" }\nfirebase-functions = { group = "com.google.firebase", name = "firebase-functions" }')
catalog.write_text(s, encoding="utf-8")

source = Path("app/src/main/java/com/example/game/OnlineGameRepository.kt")
source.parent.mkdir(parents=True, exist_ok=True)
source.write_text(r"""package com.example.game

import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.DocumentSnapshot
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.firestore.ListenerRegistration
import com.google.firebase.functions.FirebaseFunctions
import com.google.android.gms.tasks.Task

/**
 * Client transport for the server-authoritative online game.
 * All state mutations go through callable Cloud Functions; clients never write room documents.
 */
class OnlineGameRepository(
    private val auth: FirebaseAuth = FirebaseAuth.getInstance(),
    private val db: FirebaseFirestore = FirebaseFirestore.getInstance(),
    private val functions: FirebaseFunctions = FirebaseFunctions.getInstance("us-central1")
) {
    fun ensureSignedIn(): Task<String> {
        val current = auth.currentUser
        if (current != null) return com.google.android.gms.tasks.Tasks.forResult(current.uid)
        return auth.signInAnonymously().continueWith { task ->
            val user = task.result?.user ?: throw IllegalStateException("Anonymous sign-in returned no user.")
            user.uid
        }
    }

    fun createRoom(): Task<Map<String, Any>> = call("createRoom", emptyMap())

    fun joinRoom(roomId: String): Task<Map<String, Any>> =
        call("joinRoom", mapOf("roomId" to roomId.trim()))

    fun rollDice(roomId: String, stateVersion: Long): Task<Map<String, Any>> =
        call("rollDice", mapOf("roomId" to roomId, "stateVersion" to stateVersion))

    fun moveToken(roomId: String, stateVersion: Long, tokenIndex: Int): Task<Map<String, Any>> =
        call("moveToken", mapOf(
            "roomId" to roomId,
            "stateVersion" to stateVersion,
            "tokenIndex" to tokenIndex
        ))

    fun passTurn(roomId: String, stateVersion: Long): Task<Map<String, Any>> =
        call("passTurn", mapOf("roomId" to roomId, "stateVersion" to stateVersion))

    fun listenToRoom(roomId: String, onState: (DocumentSnapshot?, Exception?) -> Unit): ListenerRegistration {
        require(roomId.matches(Regex("[A-Za-z0-9_-]{8,64}"))) { "Invalid room ID." }
        return db.collection("rooms").document(roomId).addSnapshotListener { snapshot, error ->
            onState(snapshot, error)
        }
    }

    private fun call(name: String, data: Map<String, Any>): Task<Map<String, Any>> {
        return functions.getHttpsCallable(name).call(data).continueWith { task ->
            @Suppress("UNCHECKED_CAST")
            (task.result?.data as? Map<String, Any>)
                ?: throw IllegalStateException("$name returned an empty response.")
        }
    }
}
""", encoding="utf-8")
print("Firebase Auth, Firestore and callable Functions client transport installed.")
