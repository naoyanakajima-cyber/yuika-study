// Test-only deterministic PRNG. Application/production randomness is unchanged.
(() => {
  let state = 20261110;
  Math.random = () => {
    state = (Math.imul(1664525, state) + 1013904223) >>> 0;
    return state / 4294967296;
  };
})();
