import React from "react";
// import './view.css';

import { Link  } from "react-router-dom";
import { Button, Callout, ControlGroup, InputGroup, MenuItem, Spinner } from "@blueprintjs/core";
import AdminComponent from "./admincomponent";
import { UsersService } from "../api";
import { User } from "@blueprintjs/icons/lib/esm/generated/16px/paths";
import { isNullOrUndefined } from "util";


function UsersTable(props) {
    const rows = []
    for(let user of props.users) {
        rows.push(<tr>
            <td>{user.username}</td>
            <td>{user.email}</td>
            <td>{user.is_admin ? 'Yes' : "No"}</td>
            <td>{user.is_active ? 'Yes' : "No"}</td>
            <td><Button></Button></td>
        </tr>);
    }
    return <table>
        <thead>
            <tr>
                <th>Username</th>
                <th>E-mail</th>
                <th>Admin</th>
                <th>Active</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
}

class UserForm extends React.Component {
    constructor(props: any) {
        super(props);

        this.reset();
    }

    reset() {
        this.state = {
            username: "",
            email: "",
            password: "",
            is_active: true,
            is_admin: false
        }
    }
    
    submit() {
        console.log(this.state)
        UsersService.usersCreate({
            username: this.state.username,
            email: this.state.email,
            password: this.state.password,
            is_active: this.state.is_active,
            is_admin: this.state.is_admin,
        })
    }

    handleChange(key, event) { console.log(key, event.target.value); this.setState({key: event.target.value});}

    render() { 
        return <form>
            <h3>New user:</h3>
            <table>
                <tbody>
                    <tr>
                        <td><label>Username:</label></td>
                        <td><input type="text" value={this.state.username} onChange={e => this.handleChange('username', e)} /></td>
                    </tr>
                    <tr>
                        <td><label>E-mail:</label></td>
                        <td><input type="email" value={this.state.email} onChange={e => this.handleChange('email', e)} /></td>
                    </tr>
                    <tr>
                        <td><label>Password:</label></td>
                        <td><input type="password" value={this.state.password} onChange={e => this.handleChange('password', e)} /></td>
                    </tr>
                    <tr>
                        <td><label>Active:</label></td>
                        <td><input type="checkbox" value={this.state.is_active} onChange={e => this.handleChange('is_active', e)} /></td>
                    </tr>
                    <tr>
                        <td><label>Admin:</label></td>
                        <td><input type="checkbox" value={this.state.is_admin} onChange={e => this.handleChange('is_admin', e)} /></td>
                    </tr>
                </tbody>
            </table>
            <Button type="submit" text="Send" intent="success" onClick={this.submit.bind(this)}/>
            <Button type="reset" text="Cancel" intent="warning" onClick={this.reset()} />
        </form>
    }
}


class AdminHome extends AdminComponent {
    constructor(props: any) {
        super(props);

        this.reset();
    }

    reset() {
        this.state = {
            users: []
        }
    }

    componentDidMount() {
        UsersService.usersListAll().then(users => { this.setState({users: users})});
    }

    render() { 
        return (
        <div className="App">
            <Button className='back-btn'><Link to="/">{'< retour'}</Link></Button>
            <header className="App-header">
                <h1>Sulci Lab</h1>
                <p>Select one or several labeling sets and open them in the editor.</p>
            </header>

            <div className="app-row page">
                <h1>Admin</h1>
                <section>
                    <h2>Users</h2>
                    <UsersTable users={this.state.users}></UsersTable>
                    <UserForm></UserForm>
                </section>
            </div>
        </div>
    );}
}

export default AdminHome;