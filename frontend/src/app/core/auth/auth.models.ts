export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  name: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface CurrentUser {
  id: string;
  nome: string;
  name: string;
  email: string;
}
