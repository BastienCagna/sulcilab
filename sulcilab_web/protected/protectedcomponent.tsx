import React from "react";
import { PUser } from "../api";
import { appTokenStorage } from "../helper/tokenstorage";


export default class ProtectedComponent extends React.Component {
    user: PUser | null = null;

    constructor(props: any) {
        super(props);
        if(!appTokenStorage.isAuthenticated()) {
            window.location = '/';            
        } 
        this.user = appTokenStorage.user ? appTokenStorage.user : null;
    }
}