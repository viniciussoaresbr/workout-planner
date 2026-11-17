function base64Url(value: object): string {
  const bytes = new TextEncoder().encode(JSON.stringify(value));
  const binary = String.fromCharCode(...bytes);
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

/** Gera um JWT (não assinado) com expiração relativa a agora, em segundos. */
export function fakeJwt(expiresInSeconds = 3600, extra: Record<string, unknown> = {}): string {
  const exp = Math.floor(Date.now() / 1000) + expiresInSeconds;
  return `${base64Url({ alg: 'HS256', typ: 'JWT' })}.${base64Url({ sub: 'user-1', exp, ...extra })}.assinatura`;
}

export const TEST_API_URL = 'http://api.test/api/v1';
