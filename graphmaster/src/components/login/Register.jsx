import { useForm } from "react-hook-form";

export default function Register() {

    const { register, handleSubmit } = useForm();
    const onSubmit = (data) => {
    console.log(data)
    const requestOptions = {
        method: 'POST',
        body: JSON.stringify(data)
    };
    fetch('/api/register', requestOptions)
        .then(response => response.json())

    }

    return (
        <div className="register" id="register">

            <form onSubmit={handleSubmit(onSubmit)}>
                <input {...register("username", { required: true })} placeholder="Username" />

                <input {...register("password", { required: true, minLength: 6 })} placeholder="Password" />

                <input {...register("email", { required: true, minLength: 2 })} placeholder="Email" />

                <input type="submit" value="Submit" />
            </form>

        </div>
    )
}

