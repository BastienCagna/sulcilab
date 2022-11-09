import { ThDisconnect, ThumbsUp } from "@blueprintjs/icons/lib/esm/generated/16px/paths";
import { UsersService, PUser } from "../api/";


function parseJwt (token: string) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
}

export class TokenStorage {
    expiration: number | undefined = undefined;
    token: string | undefined = undefined;
    user: PUser|undefined = undefined;

    constructor() {
        let token = sessionStorage.getItem("token");
        let user = sessionStorage.getItem("user");
        if(token && user && user != "undefined") {
            this.token = token;
            this.user = JSON.parse(user);
            this.expiration = parseJwt(token)['expiration'] * 1000;
            this.checkExpiration();
        }
    }

    async setToken(token: string) {
        sessionStorage.setItem("token", token);
        this.user = await UsersService.usersGetCurrentUser();
        sessionStorage.setItem("user", JSON.stringify(this.user));
    }

    checkExpiration() {
        if(this.expiration && this.expiration < Date.now()) {
            this.reset();
        }
    }
    isAuthenticated() {
        this.checkExpiration();
        return this.user != undefined;
    }

    reset() {
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user');
        this.user = undefined;
        this.token = undefined;
    }
}

export const appTokenStorage = new TokenStorage();