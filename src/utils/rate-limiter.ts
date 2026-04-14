/**
 * Per-hostname upstream rate limiter using a token bucket algorithm.
 *
 * One bucket per CKAN portal hostname. Cache hits bypass the limiter entirely —
 * only requests that reach the upstream consume tokens.
 */

export class RateLimitError extends Error {
  constructor(hostname: string, waitMs: number) {
    super(
      `Rate limit exceeded for ${hostname}: would need to wait ${Math.round(waitMs)}ms`
    );
    this.name = "RateLimitError";
  }
}

export interface RateLimitConfig {
  enabled: boolean;
  rps: number;
  burst: number;
  maxWaitMs: number;
}

interface Bucket {
  tokens: number;
  lastRefill: number;
}

const MAX_BUCKETS = 200;

function readEnv(name: string): string | undefined {
  if (typeof process === "undefined" || !process.env) return undefined;
  const v = process.env[name];
  return v === undefined || v === "" ? undefined : v;
}

export function getRateLimitConfig(): RateLimitConfig {
  const enabledRaw = readEnv("CKAN_RATE_LIMIT_ENABLED");
  const isTest = readEnv("VITEST") === "true";
  const enabled =
    enabledRaw !== undefined ? enabledRaw !== "false" : !isTest;
  return {
    enabled,
    rps: Number(readEnv("CKAN_RATE_LIMIT_RPS")) || 5,
    burst: Number(readEnv("CKAN_RATE_LIMIT_BURST")) || 10,
    maxWaitMs: Number(readEnv("CKAN_RATE_LIMIT_MAX_WAIT_MS")) || 5000,
  };
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export class UpstreamRateLimiter {
  private readonly buckets = new Map<string, Bucket>();

  constructor(private readonly config: RateLimitConfig) {}

  async acquire(hostname: string): Promise<void> {
    const { rps, burst, maxWaitMs } = this.config;

    if (!this.buckets.has(hostname)) {
      if (this.buckets.size >= MAX_BUCKETS) {
        const oldest = this.buckets.keys().next().value;
        if (oldest !== undefined) this.buckets.delete(oldest);
      }
      this.buckets.set(hostname, { tokens: burst, lastRefill: Date.now() });
    }

    let waited = 0;
    while (true) {
      const bucket = this.buckets.get(hostname)!;
      const now = Date.now();
      const elapsed = now - bucket.lastRefill;
      bucket.tokens = Math.min(burst, bucket.tokens + (elapsed / 1000) * rps);
      bucket.lastRefill = now;

      if (bucket.tokens >= 1) {
        bucket.tokens -= 1;
        return;
      }

      const waitNeeded = ((1 - bucket.tokens) / rps) * 1000;
      if (waited + waitNeeded > maxWaitMs) {
        throw new RateLimitError(hostname, waited + waitNeeded);
      }

      await sleep(waitNeeded);
      waited += waitNeeded;
    }
  }

  clear(): void {
    this.buckets.clear();
  }
}

let sharedLimiter: UpstreamRateLimiter | null = null;

export function getRateLimiter(): UpstreamRateLimiter {
  if (!sharedLimiter) {
    sharedLimiter = new UpstreamRateLimiter(getRateLimitConfig());
  }
  return sharedLimiter;
}

export function __resetRateLimiterForTests(): void {
  sharedLimiter = null;
}
