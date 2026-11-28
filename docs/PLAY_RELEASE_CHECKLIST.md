# Royal Ludo 3D — Play release checklist

## Build and signing
- [ ] Set GitHub Actions secrets: UPLOAD_KEYSTORE_BASE64, UPLOAD_STORE_PASSWORD, UPLOAD_KEY_PASSWORD.
- [ ] Create a persistent upload keystore with alias `upload`; back it up securely. Never commit it.
- [ ] Set ADMOB_APP_ID and ADMOB_BANNER_ID to the publisher's real AdMob IDs. Test IDs are for development only.
- [ ] Build a signed Android App Bundle (AAB), verify signature and install/test the release build.
- [ ] Confirm application ID and versionCode; increment versionCode for every update.

## App and backend
- [ ] Deploy Firebase Cloud Functions and Firestore rules to the intended production project.
- [ ] Run emulator/security-rule tests and real-device online tests.
- [ ] Verify crash-free launch, game rules, bot turns, reconnect, offline behavior and network failure handling.
- [ ] Complete any promised multiplayer features before advertising them in the listing.

## Google Play Console
- [ ] Complete developer account identity and payment profile as applicable.
- [ ] Complete Data safety, Ads, App access, Target audience, Content rating and other declarations truthfully.
- [ ] Provide public privacy-policy URL and support contact.
- [ ] Upload 512x512 icon, 1024x500 feature graphic and real screenshots.
- [ ] Complete the testing track and any required tester period for the account.
- [ ] Resolve all Play Console warnings and policy review issues before production rollout.

## Monetization
- [ ] Create/verify AdMob publisher account and app.
- [ ] Configure real ad unit IDs and consent/privacy messaging for applicable regions.
- [ ] Test ads using Google's test IDs during development; never click live ads yourself.
- [ ] Do not add real-money wagering, cash prizes or cash withdrawals.
- [ ] If in-app digital purchases/subscriptions are added later, use Google Play Billing and complete policy/legal review.
