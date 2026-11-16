# R1 Model Repair Plan

**Status: completed and verified.**

1. The model uses a 100% protected-liquidity inactive fallback and no return forecast.
2. It defines cash accounting, external-flow treatment and no automatic reinvestment so a later return study cannot count a receipt twice.
3. It treats delayed data, liquidity, price limits, margin, delivery and failed exits as modeled constraints rather than assumptions away.
4. It retains crypto as a separate q=0 packet with legal/access, custody/venue, mark, liquidity, funding, tax and red-team gates.
