export type EyePosition = [number, number, number, number, number, number]

export type TimestampInMicroseconds = number;

export interface Afe {
  i: [number, TimestampInMicroseconds, number, number];
  m: [
    EyePosition,
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
