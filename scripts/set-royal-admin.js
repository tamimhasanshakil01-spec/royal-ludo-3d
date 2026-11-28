/**
 * One-time, owner-run bootstrap for the Royal Ludo 3D Firebase administrator.
 *
 * Run ONLY in the Google Cloud Shell of the correct Firebase project, while
 * signed in as a project owner with permission to manage Firebase Auth users.
 * This script does not expose a public admin-promotion endpoint.
 */
const { applicationDefault, initializeApp } = require("firebase-admin/app");
const { getAuth } = require("firebase-admin/auth");

const ADMIN_EMAIL = "tamimhasanshakil01@gmail.com";

initializeApp({ credential: applicationDefault() });

async function main() {
  const auth = getAuth();
  const user = await auth.getUserByEmail(ADMIN_EMAIL);

  if (user.disabled) {
    throw new Error("The target Firebase Auth account is disabled.");
  }
  if (user.email?.toLowerCase() !== ADMIN_EMAIL) {
    throw new Error("Firebase Auth returned a different email.");
  }
  if (user.emailVerified !== true) {
    throw new Error("Verify the target email in Firebase Authentication first.");
  }

  const claims = { ...(user.customClaims || {}), admin: true };
  await auth.setCustomUserClaims(user.uid, claims);

  const updated = await auth.getUser(user.uid);
  if (updated.customClaims?.admin !== true) {
    throw new Error("Could not verify the admin custom claim.");
  }

  console.log("Royal Ludo 3D admin claim successfully assigned.");
  console.log("Email:", updated.email);
  console.log("UID:", updated.uid);
  console.log("Next: sign out and sign in again in the app to refresh the ID token.");
}

main().catch((error) => {
  console.error("Admin setup failed:", error.message || error);
  process.exitCode = 1;
});
