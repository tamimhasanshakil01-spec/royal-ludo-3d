# Backend implementation status

## Implemented in repository
- Firebase Android app configuration is present in `firebase/google-services.json` and copied into the Android build.
- Firestore rules deny all client writes to game state, profiles and wallet data.
- Callable functions require Firebase Authentication.
- Room creation and joining are transactional; each player receives four home tokens.
- Dice are generated server-side using cryptographic randomness.
- `moveToken` validates membership, turn, state version, token index and legal progress on the server; captures, safe squares, exact home entry, bonus rolls and match completion are calculated server-side.
- `passTurn` only permits a pass when no legal token move exists.
- Game actions are recorded in immutable server-created event documents.
- Android debug build workflow compiles and uploads a debug APK artifact.

## Not yet complete or verified
- The Android client is not yet wired to call the room, dice, move and pass callable functions or subscribe to the authoritative room state. Its current gameplay logic still runs locally.
- Server-side bot turns, matchmaking/reconnection, account/profile flows and end-to-end online UX are not complete.
- Emulator/unit/security tests and deployment to the Firebase project have not been run.
- The Android workflow's successful build demonstrates compilation only, not online gameplay or release readiness.
- Real-money deposits, wagering and withdrawals remain disabled. Any future money feature requires jurisdiction-specific legal review, compliant payment-provider approval, KYC/AML and responsible-play safeguards.

Do not advertise the app as a completed online multiplayer game until client integration, tests, deployment and end-to-end verification pass.
