import { initializeApp } from "firebase-admin/app";
import { FieldValue, getFirestore } from "firebase-admin/firestore";
import { randomInt } from "node:crypto";
import { HttpsError, onCall } from "firebase-functions/v2/https";
import { applyMove, chooseBotTokenIndex, legalTokenIndices, nextTurn, Pieces } from "./ludo";

initializeApp();
const db = getFirestore();
const MAX_PLAYERS = 4;

function requireUid(request: { auth?: { uid: string } | null }): string {
  const uid = request.auth?.uid;
  if (!uid) throw new HttpsError("unauthenticated", "Sign in is required.");
  return uid;
}

function roomIdFrom(data: any): string {
  const roomId = String(data?.roomId ?? "").trim();
  if (!/^[A-Za-z0-9_-]{8,64}$/.test(roomId)) {
    throw new HttpsError("invalid-argument", "A valid room ID is required.");
  }
  return roomId;
}

function checkVersion(value: unknown): number {
  const version = Number(value);
  if (!Number.isSafeInteger(version) || version < 0) {
    throw new HttpsError("invalid-argument", "A valid state version is required.");
  }
  return version;
}

/** Creates a private two-player room. The room remains waiting until another player joins. */
export const createRoom = onCall(async (request) => {
  const uid = requireUid(request);
  const roomRef = db.collection("rooms").doc();
  await roomRef.create({
    status: "waiting",
    playerUids: [uid],
    currentTurnIndex: 0,
    currentTurnUid: null,
    diceValue: null,
    stateVersion: 0,
    gameState: { pieces: { [uid]: [-1, -1, -1, -1] }, winnerUid: null },
    createdAt: FieldValue.serverTimestamp(),
    updatedAt: FieldValue.serverTimestamp()
  });
  return { roomId: roomRef.id, stateVersion: 0, status: "waiting" };
});

/** Creates or updates a verified player's public profile using the authenticated UID. */
export const registerProfile = onCall(async (request) => {
  const uid = requireUid(request);
  const email = String(request.auth?.token?.email ?? "").trim().toLowerCase();
  const emailVerified = request.auth?.token?.email_verified === true;
  const displayName = String(request.data?.displayName ?? "").trim().slice(0, 40);
  if (!email || !emailVerified) {
    throw new HttpsError("failed-precondition", "A verified email address is required.");
  }
  if (displayName.length < 2) {
    throw new HttpsError("invalid-argument", "A display name of at least 2 characters is required.");
  }
  const ref = db.collection("users").doc(uid);
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    const profile: Record<string, unknown> = {
      uid, email, displayName, status: "active",
      updatedAt: FieldValue.serverTimestamp()
    };
    if (!snap.exists) profile.createdAt = FieldValue.serverTimestamp();
    tx.set(ref, profile, { merge: true });
  });
  return { playerId: uid, displayName };
});

const BOT_UID = "ROYEL_BOT";

/** Creates a real server-authoritative human-vs-bot room. */
export const createBotRoom = onCall(async (request) => {
  const uid = requireUid(request);
  const roomRef = db.collection("rooms").doc();
  await roomRef.create({
    status: "active",
    playerUids: [uid, BOT_UID],
    currentTurnIndex: 0,
    currentTurnUid: uid,
    diceValue: null,
    stateVersion: 0,
    gameState: { pieces: { [uid]: [-1, -1, -1, -1], [BOT_UID]: [-1, -1, -1, -1] }, winnerUid: null },
    createdAt: FieldValue.serverTimestamp(),
    updatedAt: FieldValue.serverTimestamp()
  });
  return { roomId: roomRef.id, stateVersion: 0, opponent: "Royel Bot" };
});

/** Executes one bot turn on the trusted server; clients cannot choose bot dice or moves. */
export const playBotTurn = onCall(async (request) => {
  const uid = requireUid(request);
  const roomId = roomIdFrom(request.data);
  const expectedVersion = checkVersion(request.data?.stateVersion);
  const ref = db.collection("rooms").doc(roomId);
  let response: Record<string, unknown> | null = null;
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (!snap.exists) throw new HttpsError("not-found", "Room not found.");
    const room = snap.data()!;
    const players = room.playerUids as string[];
    if (!players.includes(uid)) throw new HttpsError("permission-denied", "You are not in this room.");
    if (room.status !== "active" || room.currentTurnUid !== BOT_UID) {
      throw new HttpsError("failed-precondition", "It is not the bot's turn.");
    }
    if (room.stateVersion !== expectedVersion) throw new HttpsError("aborted", "Game state changed. Refresh and retry.");
    const pieces = (room.gameState?.pieces ?? {}) as Pieces;
    const dice = randomInt(1, 7);
    const tokenIndex = chooseBotTokenIndex(players, pieces, BOT_UID, dice);
    const nextVersion = expectedVersion + 1;
    if (tokenIndex === null) {
      const nextIndex = nextTurn(players, Number(room.currentTurnIndex));
      tx.update(ref, {
        diceValue: null,
        currentTurnIndex: nextIndex,
        currentTurnUid: players[nextIndex],
        stateVersion: nextVersion,
        updatedAt: FieldValue.serverTimestamp()
      });
      tx.create(ref.collection("events").doc(), {
        type: "bot_turn_passed", uid: BOT_UID, dice,
        stateVersion: nextVersion, createdAt: FieldValue.serverTimestamp()
      });
      response = { stateVersion: nextVersion, diceValue: dice, tokenIndex: null, passed: true };
      return;
    }
    const result = applyMove(players, pieces, BOT_UID, tokenIndex, dice);
    const nextIndex = result.bonusRoll ? Number(room.currentTurnIndex) : nextTurn(players, Number(room.currentTurnIndex));
    const nextUid = result.bonusRoll ? BOT_UID : players[nextIndex];
    const status = result.winnerUid ? "completed" : "active";
    tx.update(ref, {
      gameState: { ...(room.gameState ?? {}), pieces: result.pieces, winnerUid: result.winnerUid },
      diceValue: null,
      currentTurnIndex: nextIndex,
      currentTurnUid: nextUid,
      status,
      winnerUid: result.winnerUid,
      stateVersion: nextVersion,
      lastActionUid: BOT_UID,
      updatedAt: FieldValue.serverTimestamp()
    });
    tx.create(ref.collection("events").doc(), {
      type: "bot_token_moved", uid: BOT_UID, tokenIndex, dice,
      capturedUids: result.capturedUids, winnerUid: result.winnerUid,
      bonusRoll: result.bonusRoll, stateVersion: nextVersion,
      createdAt: FieldValue.serverTimestamp()
    });
    response = { stateVersion: nextVersion, diceValue: dice, tokenIndex,
      pieces: result.pieces, winnerUid: result.winnerUid, bonusRoll: result.bonusRoll };
  });
  return response!;
});

/** Joins a waiting private room; the server starts the match atomically. */
export const joinRoom = onCall(async (request) => {
  const uid = requireUid(request);
  const roomId = roomIdFrom(request.data);
  const ref = db.collection("rooms").doc(roomId);
  let stateVersion = 0;
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (!snap.exists) throw new HttpsError("not-found", "Room not found.");
    const room = snap.data()!;
    const players = Array.isArray(room.playerUids) ? room.playerUids as string[] : [];
    if (players.includes(uid)) {
      stateVersion = Number(room.stateVersion ?? 0);
      return;
    }
    if (room.status !== "waiting") {
      throw new HttpsError("failed-precondition", "This room is not waiting for another player.");
    }
    if (players.length !== 1) {
      throw new HttpsError("failed-precondition", "This room is full or invalid.");
    }
    const nextPlayers = [...players, uid];
    const oldPieces = (room.gameState?.pieces ?? {}) as Pieces;
    const nextPieces: Pieces = { ...oldPieces, [uid]: [-1, -1, -1, -1] };
    stateVersion = Number(room.stateVersion ?? 0) + 1;
    tx.update(ref, {
      status: "active",
      playerUids: nextPlayers,
      currentTurnIndex: 0,
      currentTurnUid: nextPlayers[0],
      gameState: { ...room.gameState, pieces: nextPieces, winnerUid: null },
      stateVersion,
      updatedAt: FieldValue.serverTimestamp()
    });
    tx.create(ref.collection("events").doc(), {
      type: "player_joined", uid, stateVersion,
      createdAt: FieldValue.serverTimestamp()
    });
  });
  return { roomId, stateVersion, status: "active" };
});

export const rollDice = onCall(async (request) => {
  const uid = requireUid(request);
  const roomId = roomIdFrom(request.data);
  const expectedVersion = checkVersion(request.data?.stateVersion);
  const ref = db.collection("rooms").doc(roomId);
  let result = 0;
  let nextVersion = 0;
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (!snap.exists) throw new HttpsError("not-found", "Room not found.");
    const room = snap.data()!;
    if (room.status !== "active") throw new HttpsError("failed-precondition", "The game is not active.");
    if (!(room.playerUids as string[]).includes(uid)) throw new HttpsError("permission-denied", "You are not in this room.");
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

export const moveToken = onCall(async (request) => {
  const uid = requireUid(request);
  const roomId = roomIdFrom(request.data);
  const expectedVersion = checkVersion(request.data?.stateVersion);
  const tokenIndex = Number(request.data?.tokenIndex);
  const ref = db.collection("rooms").doc(roomId);
  let response: { stateVersion: number; pieces: Pieces; bonusRoll: boolean; winnerUid: string | null } | null = null;

  await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (!snap.exists) throw new HttpsError("not-found", "Room not found.");
    const room = snap.data()!;
    const players = room.playerUids as string[];
    if (room.status !== "active" || !players.includes(uid)) throw new HttpsError("failed-precondition", "The game or membership is invalid.");
    if (room.currentTurnUid !== uid) throw new HttpsError("permission-denied", "It is not your turn.");
    if (room.stateVersion !== expectedVersion) throw new HttpsError("aborted", "Game state changed. Refresh and retry.");
    const dice = Number(room.diceValue);
    try {
      const result = applyMove(players, (room.gameState?.pieces ?? {}) as Pieces, uid, tokenIndex, dice);
      const bonusRoll = result.bonusRoll;
      const nextIndex = bonusRoll ? Number(room.currentTurnIndex) : nextTurn(players, Number(room.currentTurnIndex));
      const nextUid = bonusRoll ? uid : players[nextIndex];
      const nextVersion = expectedVersion + 1;
      const status = result.winnerUid ? "completed" : "active";
      tx.update(ref, {
        gameState: { ...(room.gameState ?? {}), pieces: result.pieces, winnerUid: result.winnerUid },
        diceValue: null,
        currentTurnIndex: nextIndex,
        currentTurnUid: nextUid,
        status,
        winnerUid: result.winnerUid,
        stateVersion: nextVersion,
        lastActionUid: uid,
        updatedAt: FieldValue.serverTimestamp()
      });
      tx.create(ref.collection("events").doc(), {
        type: "token_moved", uid, tokenIndex, dice,
        capturedUids: result.capturedUids,
        winnerUid: result.winnerUid,
        bonusRoll,
        stateVersion: nextVersion,
        createdAt: FieldValue.serverTimestamp()
      });
      response = { stateVersion: nextVersion, pieces: result.pieces, bonusRoll, winnerUid: result.winnerUid };
    } catch (error) {
      if (error instanceof HttpsError) throw error;
      throw new HttpsError("failed-precondition", error instanceof Error ? error.message : "Illegal move.");
    }
  });
  return response!;
});

export const passTurn = onCall(async (request) => {
  const uid = requireUid(request);
  const roomId = roomIdFrom(request.data);
  const expectedVersion = checkVersion(request.data?.stateVersion);
  const ref = db.collection("rooms").doc(roomId);
  let nextVersion = 0;
  let nextUid = "";
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (!snap.exists) throw new HttpsError("not-found", "Room not found.");
    const room = snap.data()!;
    const players = room.playerUids as string[];
    if (room.status !== "active" || !players.includes(uid) || room.currentTurnUid !== uid) {
      throw new HttpsError("permission-denied", "You cannot pass this turn.");
    }
    if (room.stateVersion !== expectedVersion) throw new HttpsError("aborted", "Game state changed. Refresh and retry.");
    const dice = Number(room.diceValue);
    if (!Number.isInteger(dice) || dice < 1 || dice > 6) throw new HttpsError("failed-precondition", "Roll the dice first.");
    const tokens = ((room.gameState?.pieces ?? {}) as Pieces)[uid] ?? [-1, -1, -1, -1];
    if (legalTokenIndices(tokens, dice).length !== 0) throw new HttpsError("failed-precondition", "A legal move is available.");
    const nextIndex = nextTurn(players, Number(room.currentTurnIndex));
    nextUid = players[nextIndex];
    nextVersion = expectedVersion + 1;
    tx.update(ref, {
      diceValue: null,
      currentTurnIndex: nextIndex,
      currentTurnUid: nextUid,
      stateVersion: nextVersion,
      lastActionUid: uid,
      updatedAt: FieldValue.serverTimestamp()
    });
    tx.create(ref.collection("events").doc(), {
      type: "turn_passed", uid, dice, stateVersion: nextVersion,
      createdAt: FieldValue.serverTimestamp()
    });
  });
  return { stateVersion: nextVersion, currentTurnUid: nextUid };
});
