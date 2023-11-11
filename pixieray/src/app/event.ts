export interface Afe {
  i: [number, number, number, number];
  m: [
    [number, number, number, number, number, number],
    []
  ],
  t: 'L' | 'R';
}

interface Raw {
  afe: [Afe, Afe];
}

export interface SSEData {
  raw: Raw;
}
