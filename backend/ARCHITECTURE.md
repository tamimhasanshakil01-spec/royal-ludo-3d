# Royal Ludo 3D — Online Backend Plan

## Product constraints
- Online-only: no local/pass-and-play game session may start without a verified server session.
- Keep the existing Android/Jetpack Compose app and evolve it; do not rebuild from zero.
- Bengali and English UI are required.
- Ludo dice, legal moves, captures, turn order, wins and rewards must be authoritative on the server. The client only renders state and sends player intent.
- The bot must obey the same rules and dice probabilities as a human. No hidden outcome manipulation or forced wins/losses.

## Proposed stack
- Firebase Authentication: account identity (phone sign-in only after SMS abuse controls and project setup).
- Cloud Firestore: profiles, matchmaking rooms, game snapshots, immutable wallet ledger, referrals and leaderboard projections.
- Cloud Functions (callable/HTTPS): create/join room, roll dice, submit move, advance turn, settle match, referral attribution and admin actions.
- App Check: reduce unauthorized client traffic.
- Admin SDK: only trusted server functions may change game state, balances or rewards.

## Data model (initial)
- `users/{uid}`: displayName, locale, createdAt, status, referralCode, referredBy.
- `rooms/{roomId}`: status, playerUids, currentTurnUid, stateVersion, gameState, createdAt, updatedAt.
- `rooms/{roomId}/events/{eventId}`: server-sequenced action/event log.
- `wallets/{uid}`: derived balance only; never client writable.
- `wallets/{uid}/ledger/{entryId}`: immutable signed entries, idempotencyKey, reason, amount, createdAt.
- `referrals/{code}`: ownerUid, createdAt, attribution records.
- `leaderboards/{seasonId}/entries/{uid}`: server-maintained stats.

## Required server commands
1. `createRoom` / `joinRoom`: verify auth, eligibility, room capacity and duplicate membership.
2. `rollDice`: verify it is the caller's turn; generate randomness on the server; persist result and event atomically.
3. `moveToken`: recompute legal moves server-side; reject stale stateVersion, illegal token, replay and out-of-turn requests.
4. `finishMatch`: calculate outcome from server state and settle non-cash points/rewards idempotently.
5. `submitBotTurn`: server-side bot uses the same legal move engine; never trust a client-provided bot move.

## Security and fairness
- Never accept a client-supplied dice result, winner, balance, deposit confirmation or withdrawal approval.
- Use Firestore transactions and idempotency keys for all state transitions.
- Keep an append-only event history for dispute review and anti-cheat checks.
- Rate-limit authentication, matchmaking and economic actions; enable App Check.
- Do not ship service-account keys or payment secrets in the APK.
- Real-money deposits, wagers or withdrawals remain disabled until legal review in each target jurisdiction, compliant payment-provider approval, KYC/AML and responsible-play controls are completed. Initial development uses non-cash test points only.

## Delivery milestones
1. Backend foundation and Firestore security rules.
2. Firebase project registration, Android app registration and `google-services.json`.
3. Authentication and online-only launch gate.
4. Authoritative game engine, rooms, reconnection and bot turns.
5. Automated rule/security tests and closed beta.
6. Non-cash wallet/referrals/admin reporting; legal review before any real-money feature.

## Current blocker
The Firebase project has not yet been created and no `google-services.json` is present. Firebase credentials/configuration must be supplied through the user's own Firebase console; never share passwords or OTPs.
