import React from 'react';
import logo from './logo.svg';

import { Button, InputGroup } from "@blueprintjs/core";

class LoginForm extends React.Component {
    render() {
        return (
            <div className="userform">
                <h4>Login</h4>
                <form>
                    <InputGroup id="text-input" placeholder="E-mail" />
                    <InputGroup id="text-input" type="password" placeholder="Password" />
                    <Button>Sign in</Button>
                    <Button>Sign up</Button>
                </form>
            </div>
        );
    }
}

export default LoginForm;
