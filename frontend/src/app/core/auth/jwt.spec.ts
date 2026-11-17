import { fakeJwt } from '../../../testing/jwt';
import { decodeJwtPayload, isTokenValid } from './jwt';

describe('jwt', () => {
  it('decodifica o payload base64url', () => {
    const payload = decodeJwtPayload(fakeJwt(60, { nome: 'Ação ✓' }));

    expect(payload?.sub).toBe('user-1');
    expect(typeof payload?.exp).toBe('number');
  });

  it.each(['', 'invalido', 'a.b', 'a.@@@.c', `x.${btoa('"texto"')}.y`])(
    'retorna null para token malformado: %s',
    token => expect(decodeJwtPayload(token)).toBeNull(),
  );

  it('considera válido apenas token com exp no futuro', () => {
    expect(isTokenValid(fakeJwt(3600))).toBe(true);
    expect(isTokenValid(fakeJwt(-10))).toBe(false);
    expect(isTokenValid(fakeJwt(2))).toBe(false); // dentro da margem de segurança
    expect(isTokenValid(null)).toBe(false);
    expect(isTokenValid('lixo')).toBe(false);
  });
});
