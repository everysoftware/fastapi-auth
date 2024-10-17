import {backendUrl} from './config.js';
import {AuthClient} from './auth_client.js';

export const authClient = new AuthClient(backendUrl);
