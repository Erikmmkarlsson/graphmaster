
import Login from './Login.jsx'

export default function Finalize() {
/*
    Finalizes the registration of a new user by sending the parameter
    to the API.
*/
    //Extracts query param from URL
    const queryParams = new URLSearchParams(window.location.search);
    const token = queryParams.get('token');


        const requestOptions = {
            method: 'GET',
            headers: {'Authorization': 'Bearer ' + token}
        };
        fetch('/api/finalize', requestOptions)
            .then(response => response.json())

    return (
        <Login/>
        )
}