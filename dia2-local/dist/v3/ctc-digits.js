// Exact CTC alignment sums for the ten one-character targets. This scores
// hypotheses from logits; it never edits the unrestricted text transcription.
function logAdd(a, b) {
  if (a === -Infinity) return b;
  if (b === -Infinity) return a;
  const maximum = Math.max(a, b);
  return maximum + Math.log(Math.exp(a - maximum) + Math.exp(b - maximum));
}

export function singleDigitScores(data, dimensions, charset) {
  if (dimensions.length !== 3 || dimensions[2] !== charset.length ||
      !(dimensions[0] === 1 || dimensions[1] === 1)) throw new Error("Unexpected digit model output.");
  const indices = Array.from("0123456789", digit => charset.indexOf(digit));
  if (indices.some(index => index < 1)) throw new Error("Digit vocabulary does not match the model.");
  const classes = charset.length, steps = dimensions[0] === 1 ? dimensions[1] : dimensions[0];
  let before = 0, emitting = Array(10).fill(-Infinity), after = Array(10).fill(-Infinity);
  for (let t = 0; t < steps; t++) {
    const offset = t * classes, blank = data[offset];
    const values = indices.map(index => data[offset + index]);
    if (![blank, ...values].every(Number.isFinite)) throw new Error("Non-finite digit model output.");
    // The vocabulary-wide softmax denominator is common to every target and
    // cancels during the final conditional normalization. A common shift keeps
    // the dynamic program stable without changing the conditional scores.
    const shift = Math.max(blank, ...values);
    const nextEmitting = values.map((value, i) => logAdd(before, emitting[i]) + value - shift);
    const nextAfter = after.map((value, i) => logAdd(emitting[i], value) + blank - shift);
    before += blank - shift; emitting = nextEmitting; after = nextAfter;
  }
  const likelihoods = emitting.map((value, i) => logAdd(value, after[i]));
  const maximum = Math.max(...likelihoods), scores = likelihoods.map(value => Math.exp(value - maximum));
  const total = scores.reduce((a, b) => a + b, 0);
  return scores.map(value => value / total);
}
