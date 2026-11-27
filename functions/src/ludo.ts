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
