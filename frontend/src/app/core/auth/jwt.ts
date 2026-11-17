export interface JwtPayload {
  sub?: string;
  exp?: number;
  iat?: number;
}

/** Decodifica o payload de um JWT (base64url) sem validar a assinatura. */
export function decodeJwtPayload(token: string): JwtPayload | null {
  const [, payload] = token.split('.');
  if (!payload) {
    return null;
  }
  try {
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=');
    const bytes = Uint8Array.from(atob(padded), char => char.charCodeAt(0));
    const parsed: unknown = JSON.parse(new TextDecoder().decode(bytes));
    return typeof parsed === 'object' && parsed !== null ? (parsed as JwtPayload) : null;
  } catch {
    return null;
  }
}

/** Verdadeiro quando o token tem `exp` no futuro (com uma margem de segurança). */
export function isTokenValid(token: string | null, now = Date.now(), leewayMs = 5_000): boolean {
  if (!token) {
    return false;
  }
  const exp = decodeJwtPayload(token)?.exp;
  return typeof exp === 'number' && exp * 1000 > now + leewayMs;
}
