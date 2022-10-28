import React from "react";
import { appTokenStorage } from "../helper/tokenstorage";


export default class ProtectedComponent extends React.Component {

    constructor(props: any) {
        super(props);
        if(!appTokenStorage.isAuthenticated()) {
            window.location = '/';            
        }
    }
}