
import { Redirect } from "react-router-dom";

export default function Finalize() {
    /*
        Finalizes the registration of a new user by sending the parameter
        to the API.
    */
    console.log(send_token('api/finalize'));
    

    return (
        <>
            <Redirect to="/login" />
        </>
    )
}

async function send_token(url = '') {
    //Extracts query param from URL
    const queryParams = new URLSearchParams(window.location.search);
    const token = queryParams.get('token');

    const requestOptions = {
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + token }
    };

    const response = await fetch(url, requestOptions)

    return response.json();
}