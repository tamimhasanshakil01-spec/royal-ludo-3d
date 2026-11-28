# Royal Ludo 3D — one-time Firebase admin setup

The repository contains the protected server-side callables `adminListPlayers`, `adminGetPlayerLedger`, and `adminAdjustFictionalWallet`. All three require the Firebase Auth custom claim `admin: true`; changing an email address in app code does not grant administrator rights.

## Owner-only bootstrap

1. Open the correct Firebase project in Google Cloud Console and start Cloud Shell.
2. Confirm the active project is the Royal Ludo 3D Firebase project.
3. Run:

```bash
mkdir -p ~/royal-ludo-admin && cd ~/royal-ludo-admin
npm init -y
npm install firebase-admin
```

4. Copy `scripts/set-royal-admin.js` from this repository into this folder.
5. Run `node set-royal-admin.js`.

Cloud Shell must be authenticated as a trusted project owner/service identity with
permission to manage Firebase Authentication users. The script refuses to proceed
unless the target account exists, is enabled, and has a verified email address.

## After bootstrap

The admin signs out and signs back in so the app receives a fresh ID token.
The Admin Panel is reachable from Wallet → Admin Panel. It checks the exact verified email and refreshes the Firebase ID token; the server independently verifies the custom claim for every list, ledger, and balance operation. The app calls the protected server functions; it never writes wallet documents directly.
Never add a public endpoint that lets users grant themselves admin privileges.

## Important wallet boundary

This wallet is fictional game balance only. It is not money and cannot be purchased,
redeemed, withdrawn, transferred, or used for stakes. This setup does not configure
bKash/Nagad merchant payments or deploy Cloud Functions.


## Deploying the admin server functions

The Android build checks the TypeScript functions but does not deploy them. Deploy with `firebase deploy --only functions --project royel-ludo-3d` from a trusted, authenticated environment. Cloud Functions deployment may require the Firebase project to use the Blaze billing plan. Confirm the project's billing plan and budget alerts before deployment. Never paste service-account private keys into chat or commit them to the repository.
