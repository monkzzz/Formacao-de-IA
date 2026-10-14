#!/usr/bin/env node
/**
 * Gera nove imagens PNG (128x128), cada uma com um digito manuscrito (1-9)
 * sobre um fundo de cor diferente. Sem dependencias externas.
 *
 * Uso (na raiz do repositorio):
 *   node Dia2/Desafio/gerar_digitos.js
 *
 * Os arquivos digito_1.png ... digito_9.png sao gerados na mesma pasta.
 * O algoritmo reproduz as imagens originalmente adicionadas ao desafio.
 */
"use strict";

const fs = require("node:fs");
const path = require("node:path");

const N = 128;
const SCALE = N / 224;

// Trajetorias de caligrafia definidas com curvas de Bezier (M, L, Q, C).
const patterns = [
  "M 80 83 Q 105 68 122 47 Q 125 95 121 182 M 92 184 Q 123 182 151 184",
  "M 72 78 C 75 43 133 31 157 59 C 181 87 150 114 118 138 C 91 156 77 171 74 183 Q 119 180 162 183",
  "M 77 56 C 108 35 149 43 157 68 C 165 93 132 108 111 112 C 149 104 171 129 159 158 C 147 189 105 193 80 171",
  "M 145 183 Q 147 100 145 46 M 144 46 C 121 79 92 112 75 140 C 101 143 137 141 165 139",
  "M 158 53 C 123 54 105 57 88 58 Q 83 91 82 112 C 105 98 136 106 153 127 C 168 148 155 171 135 181 Q 106 194 77 169",
  "M 148 53 C 113 63 85 92 81 123 C 75 154 89 184 119 182 C 147 183 163 161 154 140 C 147 119 113 115 92 132 C 80 143 83 162 92 174",
  "M 73 57 C 105 55 136 56 165 53 C 143 98 116 146 105 184 M 89 111 Q 118 117 146 108",
  "M 118 112 C 78 93 81 63 104 50 C 129 38 158 57 155 82 C 153 105 123 112 115 115 C 83 128 70 152 85 172 C 103 194 149 187 159 165 C 169 143 144 123 118 112",
  "M 148 107 C 154 78 143 54 123 49 C 95 43 76 63 80 89 C 84 114 110 125 130 113 C 146 103 149 91 147 77 C 158 125 136 165 104 185"
];
const backgrounds = [
  "#FDE68A", "#BFDBFE", "#FBCFE8", "#BBF7D0", "#DDD6FE",
  "#FED7AA", "#A5F3FC", "#FECACA", "#D9F99D"
];
const inks = [
  "#5B21B6", "#7C2D12", "#1E3A8A", "#7C2D12", "#14532D",
  "#1E40AF", "#831843", "#164E63", "#713F12"
];
const rotations = [-5, 4, -3, 3, -4, 4, -2, 2, -3];

function parsePath(s) {
  const tokens = s.match(/[A-Za-z]|-?\d+(?:\.\d+)?/g);
  let i = 0, cmd = "", p = [0, 0], strokes = [], line = null;
  function val() { return Number(tokens[i++]); }

  while (i < tokens.length) {
    if (/[A-Za-z]/.test(tokens[i])) cmd = tokens[i++];

    if (cmd === "M") {
      p = [val(), val()];
      line = [p];
      strokes.push(line);
      cmd = "L";
      continue;
    }

    const start = p.slice();
    if (cmd === "L") {
      const q = [val(), val()];
      line.push(q);
      p = q;
      continue;
    }
    if (cmd === "Q") {
      const a = [val(), val()], q = [val(), val()];
      for (let j = 1; j <= 75; j++) {
        const t = j / 75, u = 1 - t;
        line.push([
          u*u*start[0] + 2*u*t*a[0] + t*t*q[0],
          u*u*start[1] + 2*u*t*a[1] + t*t*q[1]
        ]);
      }
      p = q;
      continue;
    }
    if (cmd === "C") {
      const a = [val(), val()], b = [val(), val()], q = [val(), val()];
      for (let j = 1; j <= 90; j++) {
        const t = j / 90, u = 1 - t;
        line.push([
          u*u*u*start[0] + 3*u*u*t*a[0] + 3*u*t*t*b[0] + t*t*t*q[0],
          u*u*u*start[1] + 3*u*u*t*a[1] + 3*u*t*t*b[1] + t*t*t*q[1]
        ]);
      }
      p = q;
      continue;
    }
    throw new Error("Comando de caminho inesperado: " + cmd);
  }
  return strokes;
}

function hex(s) {
  return [1, 3, 5].map(i => parseInt(s.slice(i, i + 2), 16));
}

// Rasterizacao deterministica, com anti-aliasing, leve ruido e traco variavel.
function raster(digit) {
  const back = hex(backgrounds[digit - 1]);
  const ink = hex(inks[digit - 1]);
  const mask = new Float32Array(N * N);
  const angle = rotations[digit - 1] * Math.PI / 180;
  const cs = Math.cos(angle), sn = Math.sin(angle);
  const strokes = parsePath(patterns[digit - 1]);

  for (let k = 0; k < strokes.length; k++) {
    const stroke = strokes[k];
    for (let j = 0; j < stroke.length; j++) {
      const [ux, uy] = stroke[j], dx = ux - 112, dy = uy - 112;
      const cx = (112 + cs*dx - sn*dy) * SCALE;
      const cy = (112 + sn*dx + cs*dy) * SCALE;
      const radius = (7.5 + 0.65*Math.sin((j/stroke.length)*Math.PI*2 + digit + k)) * SCALE;

      for (let y = Math.max(0, Math.floor(cy-radius-1)); y <= Math.min(N-1, Math.ceil(cy+radius+1)); y++) {
        for (let x = Math.max(0, Math.floor(cx-radius-1)); x <= Math.min(N-1, Math.ceil(cx+radius+1)); x++) {
          const dist = Math.hypot(x+0.5-cx, y+0.5-cy);
          const cov = Math.max(0, Math.min(1, radius+0.5-dist));
          const pos = y*N+x;
          if (cov > mask[pos]) mask[pos] = cov;
        }
      }
    }
  }

  const bytes = [];
  for (let y = 0; y < N; y++) {
    bytes.push(0); // Filtro PNG 0: sem predicao por linha.
    for (let x = 0; x < N; x++) {
      const cov = mask[y*N+x];
      const noise = ((x*17 + y*29 + digit*13) % 9) - 4;
      for (let c = 0; c < 3; c++) {
        const v = Math.round((back[c] + noise*0.27)*(1-cov) + ink[c]*cov);
        bytes.push(Math.max(0, Math.min(255, v)));
      }
    }
  }
  return new Uint8Array(bytes);
}

// Gravador PNG/DEFLATE sem pacotes de terceiros.
function u32(num) {
  return [(num >>> 24)&255, (num >>> 16)&255, (num >>> 8)&255, num&255];
}

const crcTable = new Uint32Array(256);
for (let n = 0; n < 256; n++) {
  let c = n;
  for (let k = 0; k < 8; k++) {
    c = (c & 1) ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
  }
  crcTable[n] = c >>> 0;
}

function chunk(type, body) {
  const typeBytes = Array.from(type).map(c => c.charCodeAt(0));
  const data = [...typeBytes, ...body];
  let crc = 0xFFFFFFFF;
  for (const b of data) crc = crcTable[(crc ^ b)&255] ^ (crc >>> 8);
  return [...u32(body.length), ...data, ...u32((crc ^ 0xFFFFFFFF) >>> 0)];
}

function zlibStored(raw) {
  const out = [0x78, 0x01];
  for (let offset = 0; offset < raw.length;) {
    const size = Math.min(65535, raw.length - offset);
    const last = offset + size === raw.length;
    out.push(last ? 1 : 0, size&255, (size >>> 8)&255, (~size)&255, ((~size) >>> 8)&255);
    for (let k = 0; k < size; k++) out.push(raw[offset+k]);
    offset += size;
  }
  let a = 1, b = 0;
  for (const x of raw) {
    a = (a + x) % 65521;
    b = (b + a) % 65521;
  }
  return [...out, ...u32(((b << 16) | a) >>> 0)];
}

function png(raw) {
  return new Uint8Array([
    137, 80, 78, 71, 13, 10, 26, 10,
    ...chunk("IHDR", [...u32(N), ...u32(N), 8, 2, 0, 0, 0]),
    ...chunk("IDAT", zlibStored(raw)),
    ...chunk("IEND", [])
  ]);
}

function gerar() {
  for (let digit = 1; digit <= 9; digit++) {
    const nome = "digito_" + digit + ".png";
    const destino = path.join(__dirname, nome);
    fs.writeFileSync(destino, Buffer.from(png(raster(digit))));
    console.log("Gerado: " + destino);
  }
}

if (require.main === module) gerar();
module.exports = { gerar };
