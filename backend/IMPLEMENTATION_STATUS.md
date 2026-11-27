# Royal Ludo 3D — implementation and verification status

Last reviewed: 2026-11-28

## Verified in repository and latest successful CI run
- Canonical app branding is `Royal Ludo 3D`; the existing Firebase project ID remains exactly `royel-ludo-3d`.
- Firebase Android configuration exists at `firebase/google-services.json` for package `com.aistudio.royalludo.kqvmrx`.
- Firestore rules deny client writes to rooms, events, profiles and wallet data; server-side functions own game-state mutations.
- Firebase callable Cloud Functions implement authenticated bot-room creation, server-generated dice, validated token moves, pass-turn checks, server bot turns, and immutable game event records.
- Android build integration adds Firebase Auth, Firestore and Functions dependencies, anonymous sign-in, callable-function transport, room-state snapshot listening, and routes the PLAY tab to the online-game screen.
- Bot policy evaluates winning moves, captures, exposed-token threats, safe squares and progress. Dice are generated uniformly with cryptographic randomness; the bot does not manipulate dice.
- The latest verified GitHub Actions run (`46059534184`, commit `cd00b716020c26c62fce4ed222503f8a03cce0b0`) completed successfully. Its steps passed for Cloud Functions TypeScript build/tests, Android Firebase integration, UI integration, branding, source packaging, and debug APK assembly.
- That run uploaded `Royal-Ludo-3D-APK`, `Royal-Ludo-Source`, and `Royal-Firebase-SHA1-Fingerprint` artifacts.
- The current unit-test file contains tests for legal moves, captures, safe squares, victory, turn order and bot decision-making; the latest CI test step passed.

## Known limitations and work still required
- This backend currently implements human-versus-bot rooms only. `createRoom` and `joinRoom` deliberately reject human-versus-human play; matchmaking and player-versus-player online rooms are not implemented.
- Account/profile management, reconnect/resume flows, leaderboards, and production monitoring are not verified as complete.
- Firebase deployment has not been performed or verified. The successful CI run builds and tests code but does not deploy Firestore rules or Cloud Functions.
- Firestore emulator/security-rule tests and a real-device end-to-end test against the deployed Firebase project remain outstanding.
- The uploaded APK is a debug build, not a signed production release. Installation and gameplay on the user's device still need verification.
- Real-money deposits, wagering and withdrawals are intentionally disabled and are outside this completion stage. Any future money features require legal review, approved payment-provider support, KYC/AML and responsible-play safeguards.

Do not describe the app as production-ready or as completed human-versus-human online multiplayer until deployment, real-device end-to-end testing and the required feature work pass.


## Firebase deployment automation added
- Added a manual GitHub Actions workflow at `.github/workflows/firebase-deploy.yml`.
- The workflow builds and tests Cloud Functions, authenticates with a repository Actions secret named `FIREBASE_SERVICE_ACCOUNT_ROYEL_LUDO_3D`, then deploys Firestore rules and Cloud Functions to the existing project `royel-ludo-3d`.
- The workflow is manual-only; it does not deploy automatically on every push.
- Deployment remains blocked until the repository secret is added and the Google service account has the required project permissions. Cloud Functions deployment may also require the Firebase project to be on the Blaze billing plan; no billing change has been made or authorized.
