// Fixed bottleneck blocks for residual64-16-32-128. All maps are real activations.
export const RESIDUAL_SHAPES = Object.fromEntries([16, 32].flatMap((channels, i) => {
  const prefix = `block${i + 1}`, narrow = channels / 2;
  return [[`${prefix}.reduce.weight`, [narrow, channels, 1, 1]],
    [`${prefix}.reduce.bias`, [narrow]],
    [`${prefix}.spatial.weight`, [narrow, narrow, 3, 3]],
    [`${prefix}.spatial.bias`, [narrow]],
    [`${prefix}.expand.weight`, [channels, narrow, 1, 1]],
    [`${prefix}.expand.bias`, [channels]]];
}));

function pointwise(input, side, channels, count, weight, bias, relu) {
  const area = side * side, output = new Float32Array(area * count);
  for (let o = 0; o < count; o++) for (let p = 0; p < area; p++) {
    let sum = bias[o];
    for (let c = 0; c < channels; c++) sum += input[c * area + p] * weight[o * channels + c];
    output[o * area + p] = relu ? Math.max(0, sum) : sum;
  }
  return output;
}

export function residualBlock(input, side, channels, weights, prefix, convRelu) {
  const narrow = channels / 2;
  const reduced = pointwise(input, side, channels, narrow,
    weights[`${prefix}.reduce.weight`], weights[`${prefix}.reduce.bias`], true);
  const spatial = convRelu(reduced, side, narrow, narrow,
    weights[`${prefix}.spatial.weight`], weights[`${prefix}.spatial.bias`]);
  const expanded = pointwise(spatial, side, narrow, channels,
    weights[`${prefix}.expand.weight`], weights[`${prefix}.expand.bias`], false);
  for (let i = 0; i < expanded.length; i++) expanded[i] = Math.max(0, input[i] + expanded[i]);
  return expanded;
}
