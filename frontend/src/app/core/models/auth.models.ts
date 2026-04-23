export interface AuthCredentials {
  email: string;
  password: string;
}

export interface RegisterPayload extends AuthCredentials {
  name: string;
}

export interface AuthResponse {
  access_token?: string;
  token?: string;
  token_type?: string;
  user?: {
    id: number;
    name: string;
    email: string;
  };
}

export interface CurrentUserResponse {
  id: string;
  nome: string;
  name: string;
  email: string;
}
