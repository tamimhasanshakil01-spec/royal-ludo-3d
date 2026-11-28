# Real-Money Betting Readiness

## Status

DESIGN ONLY — real-money wagering, deposits, withdrawals, and cash settlement are disabled. This document does not authorize or implement gambling or payment processing.

## Product direction

Royal Ludo 3D remains a single-player game against a server-authoritative bot. A future, separately reviewed wagering mode may be considered only where the operator has confirmed that the activity is lawful and has obtained all required licences, regulator approvals, and payment-provider authorization for each target market.

## Required launch gates

Do not enable any real-money feature until all gates are independently verified:

1. Written advice from qualified local counsel confirming the exact game/wager model is lawful in every launch jurisdiction.
2. All required operator, gaming, and other regulatory licences or approvals are obtained.
3. A payment provider has expressly approved the business model and the exact deposit, payout, and withdrawal flows.
4. KYC/age verification, AML/sanctions screening, fraud controls, transaction monitoring, and responsible-play controls are implemented as required.
5. Terms, privacy disclosures, dispute handling, refunds, tax/accounting, data retention, and customer support processes are ready.
6. Independent security review and end-to-end testing of server-side balance and settlement logic are complete.
7. A documented admin audit trail, reconciliation process, limits, self-exclusion, and emergency kill switch are operational.

## Safe development scope while gates are pending

- Keep the wagering UI and payment integration behind a server-controlled feature flag that defaults to OFF.
- Do not collect deposits, accept stakes, promise cash prizes, convert coins to currency, or process withdrawals.
- If a demo wallet is needed, use clearly labelled non-redeemable test coins with no cash value and no transfer or cash-out path.
- Never trust client-submitted dice, game results, wallet balances, or settlement amounts.
- Record immutable server-side ledger events and use idempotency keys if a lawful payment integration is later approved.
- Keep payment-provider credentials in server-side secret storage; never embed them in the Android app or repository.

## Architecture requirements for any future approved implementation

- Server-authoritative match creation, stake validation, game result verification, and settlement.
- Atomic balance reservation and settlement transactions to prevent double spending and race conditions.
- Separate ledger entries for deposits, reservations, releases, winnings, fees, refunds, and withdrawals.
- Per-user and per-market limits, velocity checks, suspicious-activity review, and auditable admin actions.
- Fail closed: if jurisdiction, identity, provider, or compliance checks cannot be verified, wagering remains unavailable.

## Current project limitations

The existing project status must be re-checked before implementation. Anonymous Firebase sign-in is not a substitute for verified user identity or KYC. A successful debug build or a connected payment gateway alone does not establish legal or production readiness.
