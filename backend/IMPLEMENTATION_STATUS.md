# Backend implementation status

Implemented foundation:
- Firebase project configuration and Firestore rules.
- Authenticated room creation and joining.
- Server-generated dice rolls using cryptographic randomness.
- Transactional state-version checks and immutable action events.

Not yet implemented:
- Server-side token movement and full Ludo rules engine.
- Bot decision engine running on the server.
- Reconnection/matchmaking queue, account UI and Firebase Android SDK integration.
- Wallet ledger, referral attribution, admin console and leaderboard aggregation.
- Automated emulator/security tests and deployment.

The app must not claim online play is ready until these pieces are completed and deployed. Real-money features remain disabled pending legal and payment-provider review.
