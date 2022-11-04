import React from "react";
import logo from '../../assets/images/logo_sillons.png';
import './home.css';

import { Link } from "react-router-dom";
import { Button, InputGroup } from "@blueprintjs/core";
import LoginForm from './components/loginform';
import { appTokenStorage } from "../../helper/tokenstorage";
import SignIn from "../signin/signin";
import ViewerComponent from '../../components/viewer';
import MultiViewerComponent from '../../components/multiviewer';
import { LabelingSetsService } from "../../api";
import { PLabelingSetWithoutLabelings } from "../../api/models/PLabelingSetWithoutLabelings";

export default class Home extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            demo_lset: null
        }
    }

    componentDidMount() {
        // Once the page is loaded, get the demo labelingset infos and send it to the demo viewer
        LabelingSetsService.labelingSetsGetDemoLabelingset().then(
            (lset: PLabelingSetWithoutLabelings) => {
                this.setState({demo_lset: lset})
            }
        )
    }

    render() {
        const user = appTokenStorage.user;
        const lsets = [this.state.demo_lset, this.state.demo_lset, this.state.demo_lset,  this.state.demo_lset, this.state.demo_lset, this.state.demo_lset, this.state.demo_lset,  this.state.demo_lset, this.state.demo_lset, this.state.demo_lset, this.state.demo_lset,  this.state.demo_lset]
        return (
        <div className="App">
            <header className="App-header">
                <h1>Sulci Lab</h1>
                <img src={logo} className="App-logo" alt="logo" />
            </header>
            <div className="page">
                <section>
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
                </section>
                {/* <section>
                    {/* <ViewerComponent lset={lsets[0]}></ViewerComponent> */}
                    {/* <MultiViewerComponent rows={3} cols={4} width={2400} height={1200} lsets={lsets}></MultiViewerComponent> */}
               {/* </section> */}
            </div>
        </div>
    );}
}