import React from "react";
import './subjectcard.css'
import { Button, ButtonGroup, Icon} from '@blueprintjs/core';
import { Classes, Popover2 } from "@blueprintjs/popover2";
import { PSubject } from "../../../api";

export default class SubjectCard extends React.Component {
    subject: PSubject;

    constructor(props: any) {
        super(props);
        this.subject = props.subject ? props.subject : null;
        this.state = {open: false};
    }

    handleClick = () => {  
        this.setState({open: !this.state.open});
        if(this.props.onClick)
            this.props.onClick(this.subject);
    };

    render() {
        const sub = this.subject;
        const open = this.state.open;

        // const items = sub.labelingsets.map((set: any) => <li key={set.id}>
        //     <div className="lset-title"><Icon icon="edit"/> {set.name} - {(100*set.completed).toLocaleString(undefined, {maximumFractionDigits:0})}%</div>
        //     <div className="progress-bar" style={{width: 100*set.completed + "%"}}></div>
        //     </li>);
        return ( 
            <div>
                <div className="subject-card" onClick={this.handleClick}>
                    {/* <h5>{sub.database.name}</h5> */}
                    <p>{sub.name}</p>
                </div> 

                { open &&
                    <div className="subject-popover">
                        {/* <ul className="labelingsets">{items}</ul> */}
                        {/* <ButtonGroup>
                            <Button text="Left" icon="add" small={true}/>
                            <Button text="Right" rightIcon="add" small={true} />
                        </ButtonGroup> */}
                    </div>
                }
            </div>
        );
    }
}
