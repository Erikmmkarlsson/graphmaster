import { useEffect, useState } from "react";
import './App.scss';
import {
  BrowserRouter as Router, Switch, Route, Redirect, Link
} from "react-router-dom";
import { useAuth, authFetch } from "./components/auth";
import { Login, Register, Finalize } from "./components/login/";
import Home from "./components/home/Home";
import Graphs from "./components/graphs/Graphs"

export default function App() {
  return (
    <Router>
      <nav className="nav">
        <Link to="/"><div className="button">
          Home</div></Link>

        <Link to="/login"><div className="button">
          Login</div></Link>

        <Link to="/secret"><div className="button">
          Settings</div></Link>

        <Link to="/graphs"><div className="button">
          Graphs</div></Link>
      </nav>

      {/* A <Switch> looks through its children <Route>s and
            renders the first one that matches the current URL. */}
      <Switch>
        <Route path="/login">
          <Login />
        </Route>

        <Route path="/register">
          <Register />
        </Route>

        <Route path="/finalize/">
          finalize
          <Finalize />

        </Route>

        <PrivateRoute path="/secret" component={Secret} />
        <PrivateRoute path="/graphs" component={Graphs} />

        <Route path="/">
          <Home />
        </Route>
      </Switch>
    </Router>
  );
}


function Secret() {
  const [message, setMessage] = useState('')

  useEffect(() => {
    //Api checks whether someone is logged in or not
    authFetch("/api/protected").then(response => {
      if (response.status === 401) {
        setMessage("Sorry you aren't authorized!")
        return null
      }
      return response.json()
    }).then(response => {
      if (response && response.message) {
        setMessage(response.message)
      }
    })
  }, [])
  return (<div>
    <h2>{message}</h2>
    <p>The secret is that you are here now.</p>
  </div>
  )
}

//checks whether someone is logged in or not, if not then redirects to login page
const PrivateRoute = ({ component: Component, ...rest }) => {
  const [logged] = useAuth();

  return <Route {...rest} render={(props) => (
    logged
      ? <Component {...props} />
      : <Redirect to='/login' />
  )} />
}