



export default function Home() {
    useEffect(() => {
      fetch("/api").then(resp => resp.json()).then(resp => console.log(resp))
    }, [])
    return <h2>Home</h2>;
  }
  