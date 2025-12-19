export class Pair {
  constructor(public first: number, public second: number) {}
}

export async function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function make2dArray<T>(size: number, fill: T): T[][] {
  const result: T[][] = [];
  for (let i = 0; i < size; i++) {
    result.push(new Array<T>(size).fill(fill));
  }
  return result;
}
