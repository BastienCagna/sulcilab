import React, {useEffect} from "react";
import './signin.css';
import { Link } from "react-router-dom";
import { Button} from "@blueprintjs/core";
import { ColorsService } from "../../api";


export default class SignIn extends React.Component {
    constructor(props: any) {
        super(props);
        this.reset();
    }
  
    reset() {
        this.state = {
            username: '',
            password: '',
            isLoggedIn: false
        };
    }


    async componentDidMount() {
        // const response = fetch("http://127.0.0.1:8000/color/all");
        // console.log(response);
        let response = await ColorsService.colorsRead();
        console.log(response);
    }  

    signin() {
        console.log("coucou ", this.state.username);
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
                <Button className='back-btn'><Link to="/">{'< Back'}</Link></Button>
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