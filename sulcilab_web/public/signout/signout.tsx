import React from "react";
import { appTokenStorage } from "../../helper/tokenstorage";


export default class SignOut extends React.Component {

    constructor(props: any) {
        super(props);
        if(appTokenStorage.user) {
            appTokenStorage.reset();
            window.location = "/";
        }
    }

    render() { return (
        <div></div>
    );}
}