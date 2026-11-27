import { initializeApp } from "firebase-admin/app";
import { FieldValue, getFirestore } from "firebase-admin/firestore";
import { randomInt } from "node:crypto";
import { HttpsError, onCall } from "firebase-functions/v2/https";

initializeApp();
const db = getFirestore();
const MAX_PLAYERS = 4;

function requireUid(request: { auth?: { uid: string } | null }): string {
  const uid = request.auth?.uid;
  if (!uid) throw new HttpsError("unauthenticated", "Sign in is required.");
  return uid;
}

export const createRoom = onCall(async (request) => {
  const uid = requireUid(request);
  const roomRef = db.collection("rooms").doc();
  await roomRef.create({
    status: "waiting",
    playerUids: [uid],
    currentTurnIndex: 0,
    currentTurnUid: uid,
    diceValue: null,
    stateVersion: 0,
    gameState: { pieces: {}, winnerUid: null },
    createdAt: FieldValue.serverTimestamp(),
    updatedAt: FieldValue.serverTimestamp()
  });
  return { roomId: roomRef.id, stateVersion: 0 };
});

export const joinRoom = onCall(async (request) => {
  const uid = requireUid(request);
  const roomId = String(request.data?.roomId ?? "").trim();
  if (!/^[A-Za-z0-9_-]{8,64}$/.test(roomId)) {
    throw new HttpsError("invalid-argument", "A valid room ID is required.");
  }
  const ref = db.collection("rooms").doc(roomId);
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (!snap.exists) throw new HttpsError("not-found", "Room not found.");
    const data = snap.data()!;
    const players = Array.isArray(data.playerUids) ? data.playerUids as string[] : [];
    if (players.includes(uid)) return;
    if (data.status !== "waiting" || players.length >= MAX_PLAYERS) {
      throw new HttpsError("failed-precondition", "This room is not accepting players.");
    }
    const next = [...players, uid];
    tx.update(ref, {
      playerUids: next,
      status: next.length >= 2 ? "active" : "waiting",
      stateVersion: FieldValue.increment(1),
      updatedAt: FieldValue.serverTimestamp()
    });
  });
  return { roomId, joined: true };
});

export const rollDice = onCall(async (request) => {
  const uid = requireUid(request);
  const roomId = String(request.data?.roomId ?? "").trim();
  const expectedVersion = Number(request.data?.stateVersion);
  if (!roomId || !Number.isSafeInteger(expectedVersion) || expectedVersion < 0) {
    throw new HttpsError("invalid-argument", "Room ID and state version are required.");
  }
  const ref = db.collection("rooms").doc(roomId);
  let result = 0;
  let nextVersion = 0;
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (!snap.exists) throw new HttpsError("not-found", "Room not found.");
    const room = snap.data()!;
    if (room.status !== "active") throw new HttpsError("failed-precondition", "The game is not active.");
    if (room.currentTurnUid !== uid) throw new HttpsError("permission-denied", "It is not your turn.");
    if (room.stateVersion !== expectedVersion) throw new HttpsError("aborted", "Game state changed. Refresh and retry.");
    if (room.diceValue !== null && room.diceValue !== undefined) {
      throw new HttpsError("failed-precondition", "The current dice roll has not been used.");
    }
    result = randomInt(1, 7);
    nextVersion = expectedVersion + 1;
    tx.update(ref, {
      diceValue: result,
      stateVersion: nextVersion,
      lastActionUid: uid,
      updatedAt: FieldValue.serverTimestamp()
    });
    tx.create(ref.collection("events").doc(), {
      type: "dice_rolled", uid, value: result,
      stateVersion: nextVersion,
      createdAt: FieldValue.serverTimestamp()
    });
  });
  return { diceValue: result, stateVersion: nextVersion };
});

// Token movement and turn settlement are intentionally not exposed until the
// shared server-side Ludo rules engine and its test suite are implemented.
// Never trust client-submitted positions, dice values, winners or balances.
