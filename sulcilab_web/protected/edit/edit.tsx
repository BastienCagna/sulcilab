import React from "react";
// import './view.css';

import { Link  } from "react-router-dom";
import { Button, Callout, ControlGroup, InputGroup, MenuItem, Spinner } from "@blueprintjs/core"
import ProtectedComponent from "../protectedcomponent";
import withNavigateHook from "../../helper/navigation";
import EditorComponent from "../../components/editor";



class View extends ProtectedComponent {
    constructor(props: any) {
        super(props);

        this.reset();

    }

    reset() {
        // this.state = {
        // };
    }

    componentDidMount() {
        const lsets = this.props.lsets ? this.props.lsets : this.props.navigation.getParam('lsets', []);
        if(lsets) {
            const n = lsets.length;
            
            const width = window.innerWidth;
            const height = 0.9*window.innerHeight;
            const c = Math.ceil(Math.sqrt(n));
            const r = Math.floor(n / c);
            this.setState({
                lsets: lsets,
                rows: r,
                cols: c
            })
        }
    }

    render() { 
        return (
        <div className="App">
            <Button className='back-btn'><Link to="/">{'< retour'}</Link></Button>
            { (this.state && this.state.lsets) &&
                <EditorComponent rows={this.state.rows} cols={this.state.cols} lsets={this.state.lsets} width={window.innerWidth} height={0.9*window.innerHeight}></EditorComponent>
    }
        </div>
    );}
}

export default withNavigateHook(View);