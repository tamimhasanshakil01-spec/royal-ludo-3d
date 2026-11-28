# Royal Ludo 3D — one-time Firebase admin setup

The repository already contains the server-side callable `adminAdjustFictionalWallet`.
It checks the Firebase Auth custom claim `admin: true`; changing an email address
in app code does not grant administrator rights.

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
The app must call the protected callable function; the server verifies the claim.
Never add a public endpoint that lets users grant themselves admin privileges.

## Important wallet boundary

This wallet is fictional game balance only. It is not money and cannot be purchased,
redeemed, withdrawn, transferred, or used for stakes. This setup does not configure
bKash/Nagad merchant payments or deploy Cloud Functions.
