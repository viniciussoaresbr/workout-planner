/** Limites alinhados às validações da API (schemas de auth e coluna `usuarios.email`). */
export const AUTH_LIMITS = {
  nameMin: 3,
  nameMax: 120,
  emailMax: 255,
  passwordMin: 8,
  passwordMax: 128,
} as const;
