import React from "react";
import './edit.css';

import { Link } from "react-router-dom";
import { Button, InputGroup } from "@blueprintjs/core";

import Editor from "../../components/editor";

export default class Edit extends React.Component {
    constructor(props: any) {
        super(props)
        this.state = {
            subject: {id: "0", name: "Subject 1"}
        }
    }

    render() { return (
        <div className="App">
            <header className="App-header">
                <h1>Sulci Lab</h1>
            </header>
            <Editor ></Editor>
        </div>
    );}
}