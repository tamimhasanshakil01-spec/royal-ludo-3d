const test = require("node:test");
const assert = require("node:assert/strict");
const { HOME, GOAL, SAFE, legalTokenIndices, applyMove, nextTurn } = require("../lib/ludo.js");

test("a token leaves home only on a six", () => {
  assert.deepEqual(legalTokenIndices([HOME, 0, 55, GOAL], 5), []);
  assert.deepEqual(legalTokenIndices([HOME, 0, 55, GOAL], 6), [0, 1]);
});

test("a move must enter the goal exactly; overshooting is illegal", () => {
  assert.deepEqual(legalTokenIndices([55, 56], 2), []);
  assert.deepEqual(legalTokenIndices([55, 56], 1), [0]);
});

test("a move captures an opponent on an unprotected square", () => {
  const players = ["alice", "bob"];
  const result = applyMove(players, {
    alice: [0, HOME, HOME, HOME],
    bob: [40, HOME, HOME, HOME]
  }, "alice", 0, 1);
  assert.equal(result.pieces.alice[0], 1);
  assert.equal(result.pieces.bob[0], HOME);
  assert.deepEqual(result.capturedUids, ["bob"]);
  assert.equal(result.bonusRoll, true);
});

test("safe squares protect opponent tokens from capture", () => {
  const players = ["alice", "bob"];
  const result = applyMove(players, {
    alice: [HOME, HOME, HOME, HOME],
    bob: [39, HOME, HOME, HOME]
  }, "alice", 0, 6);
  assert.equal(result.pieces.alice[0], 0);
  assert.equal(result.pieces.bob[0], 39);
  assert.deepEqual(result.capturedUids, []);
  assert.equal(SAFE.has(0), true);
});

test("winning requires all four tokens to reach the goal", () => {
  const players = ["alice", "bob"];
  const result = applyMove(players, {
    alice: [55, GOAL, GOAL, GOAL],
    bob: [HOME, HOME, HOME, HOME]
  }, "alice", 0, 1);
  assert.equal(result.winnerUid, "alice");
  assert.equal(result.pieces.alice.every(p => p === GOAL), true);
});

test("turn order wraps around the seated players", () => {
  assert.equal(nextTurn(["a", "b", "c"], 2), 0);
});
