import { ThumbsUp } from "@blueprintjs/icons/lib/esm/generated/16px/paths";
import { UsersService, PUser } from "../api/";

export class TokenStorage {
    token: string | undefined = undefined;
    user: PUser|undefined = undefined;

    constructor() {
        let token = sessionStorage.getItem("token");
        let user = sessionStorage.getItem("user");
        if(token && user && user != "undefined") {
            this.token = token;
            this.user = JSON.parse(user);
        }
    }

    async setToken(token: string) {
        sessionStorage.setItem("token", token);
        this.user = await UsersService.usersGetCurrentUser();
        sessionStorage.setItem("user", JSON.stringify(this.user));
    }

    isAuthenticated() {
        // TODO: verify that token is valid
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