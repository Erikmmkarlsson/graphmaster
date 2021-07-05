import { useEffect } from "react";




export default function Home() {
    useEffect(() => {
      fetch("/api").then(resp => resp.json()).then(resp => console.log(resp))
    }, []) //Prints hello world to the console log, from the api
    return <h2>Home</h2>;
  }
  