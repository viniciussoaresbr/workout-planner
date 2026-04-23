import { HttpContextToken } from '@angular/common/http';

export const BYPASS_GLOBAL_ERROR_HANDLER = new HttpContextToken<boolean>(
  () => false,
);
