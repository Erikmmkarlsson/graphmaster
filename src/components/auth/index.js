import {createAuthProvider} from 'react-token-auth';
/*
This creates an auth provider which stores in local storage.
Not the best. Vulnerable to XSS attacks.
*/
export const [useAuth, authFetch, login, logout] =
    createAuthProvider({
        accessTokenKey: 'access_token',
        onUpdateToken: (token) => fetch('/api/refresh', {
            method: 'POST',
            body: token.access_token
        })
        .then(r => r.json())
    });