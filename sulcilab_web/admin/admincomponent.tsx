import { PUser } from "../api";
import { appTokenStorage } from "../helper/tokenstorage";
import ProtectedComponent from "../protected/protectedcomponent";


export default class AdminComponent extends ProtectedComponent {
    user: PUser | null = null;

    constructor(props: any) {
        super(props);
        this.user = appTokenStorage.user ? appTokenStorage.user : null;
        if(!this.user || !this.user.is_admin) {
            window.location = '/';            
        } 
    }
}