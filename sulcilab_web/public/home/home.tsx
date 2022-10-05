import React from "react";
import logo from '../../logo.svg';
import './home.css';

import { Link } from "react-router-dom";
import { Button, InputGroup } from "@blueprintjs/core";
import LoginForm from './components/loginform';

export default class Home extends React.Component {

    render() {   
    const is_logged = false;

      return (
        <div className="App">
        <header className="App-header">
          <h1>Sulci Lab</h1>
          <img src={logo} className="App-logo" alt="logo" />
    
          <nav className="sl-nav">
            <Link to="/learn" className="learn">
                <h3>Learn about anatomy</h3>
            </Link>
            { is_logged && 
              <Link to="contribute" className="contribute">
                <h3>Manual Labeling</h3>
            </Link>
            }
            { !is_logged && 
              <Link to="">
                <form>
                  <label>Login:</label><input type="text" name="login" id="login"></input><br />
                  <label>Password:</label><input type="text" name="login"></input><br />
                  <input type="button" value="Sign in"></input><input type="button" value="Sign up"></input>
                </form>
              </Link>
            }
          </nav>

          <p>
            Studying Sulci Together
          </p>
        </header>
      </div>
    );}
}