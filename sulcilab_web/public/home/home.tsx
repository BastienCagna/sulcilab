import React from "react";
import logo from '../../logo.svg';
import './home.css';

import { Link } from "react-router-dom";
import { Button, InputGroup } from "@blueprintjs/core";
import LoginForm from './components/loginform';
import { appTokenStorage } from "../../helper/tokenstorage";
import SignIn from "../signin/signin";


export default class Home extends React.Component {

    render() {
      const user = appTokenStorage.user;

      return (
        <div className="App">
        <header className="App-header">
          <h1>Sulci Lab</h1>
          <h2>Studying Sulci Together</h2>
          <img src={logo} className="App-logo" alt="logo" />
    
          <nav className="sl-nav">
            <Link to="/learn" className="learn">
                <h3>Learn about anatomy</h3>
            </Link>
            { !user && 
                <div className="signin">
                    <SignIn></SignIn>
                </div>
            }
            { user && 
              <Link to="contribute" className="contribute">
                <h3>Manual Labeling</h3>
            </Link>
            }
            { user && 
            <div className="userinfos">
                <p>Username: {user.username}</p>
                <Link to="signout">Log out</Link>
            </div>
            }
          </nav>
        </header>
      </div>
    );}
}