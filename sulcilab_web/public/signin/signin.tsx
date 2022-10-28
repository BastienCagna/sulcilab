import React, {useEffect} from "react";
import './signin.css';
import { Link} from "react-router-dom";
import { Button} from "@blueprintjs/core";
import { UsersService } from "../../api/";
import { appTokenStorage } from "../../helper/tokenstorage";


export default class SignIn extends React.Component {

    constructor(props: any) {
        super(props);
        if(appTokenStorage.user) {
            window.location = '/';
        }
        this.reset();
    }
  
    reset() {
        this.state = {
            username: '',
            password: '',
            isLoggedIn: false
        };
    }

    async signin() {
        let response = await UsersService.usersLogin({
            email: this.state.username,
            password: this.state.password
        });
        if(response.token) {
            await appTokenStorage.setToken(response.token);
            window.location = '/';
        }
    }

    render() { return (
        <form className="login-form">
            <h2>Sign in</h2>
            <div className="form-item">
                <label>Username:</label><input value={this.state.username} onChange={evt => this.updateStateValue(evt, 'username')} type="text" name="login" id="login" />
            </div>
            <div className="form-item">
                <label>Password:</label><input value={this.state.password} onChange={evt => this.updateStateValue(evt, 'password')} type="password" name="password" id="password" />
            </div>
            <div className="form-item">
                <label></label>
                <Button className="submit" onClick={evt => this.signin()}>Sign in</Button>
                <a href="">Create a new account</a>
            </div>
        </form>
    );}

    updateStateValue(evt: any, key:string) {
        const val = evt.target.value; 
        this.setState({ [key]: val });
    }
}