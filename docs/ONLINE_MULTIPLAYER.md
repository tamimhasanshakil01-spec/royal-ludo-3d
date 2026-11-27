# Royal Ludo 3D — Online Multiplayer

## Implemented client/server flow

- Anonymous Firebase Authentication identifies each player.
- Callable Cloud Functions create a private waiting room, join a room, roll dice, move tokens, and pass turns.
- Firestore room documents are readable only by room members. Client writes are denied; trusted Cloud Functions own game state.
- The online Android lobby exposes server-bot matches and private two-player rooms. Share the generated room ID with the second player.

## Firebase project setup still required

1. Enable **Authentication → Sign-in method → Anonymous**.
2. Confirm the Android app registered in Firebase matches the application ID in `app/build.gradle.kts`.
3. Deploy Firestore rules and Cloud Functions from the repository root:
   `firebase deploy --only firestore:rules,functions --project royel-ludo-3d`
4. Ensure billing/plan and required Google Cloud APIs allow Cloud Functions deployment in the selected region (`us-central1`).

The GitHub Actions Android workflow builds the app and type-checks/tests Cloud Functions. A successful APK build does not itself deploy Firebase services; deployment requires an authenticated Firebase CLI session or a configured CI service-account secret.

## Manual acceptance test

- Install the same APK on two Android devices.
- Open Online Ludo on both devices and confirm anonymous sign-in succeeds.
- Device A creates a private room and shares its room ID.
- Device B joins using that room ID.
- Confirm both devices see the same room state and turns update live.
- Roll dice and attempt legal/illegal moves; verify the server accepts only legal moves and prevents out-of-turn actions.
- Play a separate server-bot match and confirm the bot acts only when its turn begins.
