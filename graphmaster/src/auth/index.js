import {createAuthProvider} from 'react-token-auth';
/*
This creates an auth provider which is interfaced by the exported consts
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