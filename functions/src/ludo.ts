export const HOME = -1;
export const GOAL = 56;
export const STARTS = [0, 13, 26, 39] as const;
export const SAFE = new Set([0, 8, 13, 21, 26, 34, 39, 47]);

export type Pieces = Record<string, number[]>;

export function validProgress(value: unknown): value is number {
  return Number.isInteger(value) && (value === HOME || (Number(value) >= 0 && Number(value) <= GOAL));
}

export function legalTokenIndices(tokens: number[], dice: number): number[] {
  if (!Number.isInteger(dice) || dice < 1 || dice > 6) return [];
  return tokens.flatMap((p, i) => {
    if (!validProgress(p) || p === GOAL) return [];
    if (p === HOME) return dice === 6 ? [i] : [];
    return p + dice <= GOAL ? [i] : [];
  });
}

function absoluteTrack(seat: number, progress: number): number | null {
  if (progress < 0 || progress > 50) return null;
  return (STARTS[seat] + progress) % 52;
}

export interface MoveResult {
  pieces: Pieces;
  capturedUids: string[];
  winnerUid: string | null;
  bonusRoll: boolean;
}

export function applyMove(
  playerUids: string[],
  piecesInput: Pieces,
  uid: string,
  tokenIndex: number,
  dice: number
): MoveResult {
  const seat = playerUids.indexOf(uid);
  if (seat < 0 || seat > 3) throw new Error("Player is not seated.");
  const pieces: Pieces = {};
  for (const player of playerUids) {
    const tokens = piecesInput[player] ?? [HOME, HOME, HOME, HOME];
    if (!Array.isArray(tokens) || tokens.length !== 4 || !tokens.every(validProgress)) {
      throw new Error("Stored token state is invalid.");
    }
    pieces[player] = [...tokens];
  }
  const tokens = pieces[uid];
  if (!Number.isInteger(tokenIndex) || tokenIndex < 0 || tokenIndex >= 4) {
    throw new Error("Token index must be between 0 and 3.");
  }
  if (!legalTokenIndices(tokens, dice).includes(tokenIndex)) {
    throw new Error("That token cannot move with the current dice.");
  }
  const oldProgress = tokens[tokenIndex];
  const nextProgress = oldProgress === HOME ? 0 : oldProgress + dice;
  tokens[tokenIndex] = nextProgress;

  const target = absoluteTrack(seat, nextProgress);
  const capturedUids: string[] = [];
  if (target !== null && !SAFE.has(target)) {
    playerUids.forEach((otherUid, otherSeat) => {
      if (otherUid === uid) return;
      const otherTokens = pieces[otherUid];
      let captured = false;
      otherTokens.forEach((progress, index) => {
        if (absoluteTrack(otherSeat, progress) === target) {
          otherTokens[index] = HOME;
          captured = true;
        }
      });
      if (captured) capturedUids.push(otherUid);
    });
  }
  const winnerUid = tokens.every(p => p === GOAL) ? uid : null;
  return {
    pieces,
    capturedUids,
    winnerUid,
    bonusRoll: winnerUid === null && (dice === 6 || capturedUids.length > 0 || nextProgress === GOAL)
  };
}

export function nextTurn(playerUids: string[], currentIndex: number): number {
  if (playerUids.length < 2 || playerUids.length > 4) throw new Error("Room must have 2–4 players.");
  return (currentIndex + 1) % playerUids.length;
}


/** Count opponent tokens that could capture this token on their next fair dice roll. */
function immediateThreats(playerUids: string[], pieces: Pieces, uid: string, progress: number): number {
  const seat = playerUids.indexOf(uid);
  const target = absoluteTrack(seat, progress);
  if (target === null || SAFE.has(target)) return 0;
  let threats = 0;
  playerUids.forEach((opponentUid, opponentSeat) => {
    if (opponentUid === uid) return;
    for (const opponentProgress of pieces[opponentUid] ?? []) {
      const from = absoluteTrack(opponentSeat, opponentProgress);
      if (from === null) continue;
      const distance = (target - from + 52) % 52;
      if (distance >= 1 && distance <= 6) threats++;
    }
  });
  return threats;
}

/** Strong server-side policy: win/capture first, protect exposed tokens, use safe squares,
 * advance toward goal, and break ties deterministically. Dice remain uniformly random. */
export function chooseBotTokenIndex(
  playerUids: string[],
  pieces: Pieces,
  uid: string,
  dice: number
): number | null {
  const legal = legalTokenIndices(pieces[uid] ?? [], dice);
  if (legal.length === 0) return null;
  const seat = playerUids.indexOf(uid);
  const scored = legal.map(index => {
    const result = applyMove(playerUids, pieces, uid, index, dice);
    const progress = result.pieces[uid][index];
    const absolute = absoluteTrack(seat, progress);
    const captured = result.capturedUids.length;
    const threatsBefore = immediateThreats(playerUids, pieces, uid, pieces[uid][index]);
    const threatsAfter = immediateThreats(playerUids, result.pieces, uid, progress);
    const escapedThreat = Math.max(0, threatsBefore - threatsAfter);
    const score =
      (result.winnerUid === uid ? 1000000 : 0) +
      captured * 20000 +
      (progress === GOAL ? 5000 : 0) +
      escapedThreat * 1800 -
      threatsAfter * 2400 +
      (absolute !== null && SAFE.has(absolute) ? 900 : 0) +
      (pieces[uid][index] === HOME ? 350 : 0) +
      progress * 12;
    return { index, score };
  });
  scored.sort((a, b) => b.score - a.score || a.index - b.index);
  return scored[0].index;
}
