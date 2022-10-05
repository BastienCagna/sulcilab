import React from "react";
import './signin.css';


export default class SignIn extends React.Component {
    render() { return (
        <form>
            <label>Username</label><input type="text" name="login" id="login" />
            <label>Password</label><input type="password" name="password" id="password" />
            <input type="submit" value="Sign in" />
            <a href="">Create a new account</a>
        </form>
    );}
}