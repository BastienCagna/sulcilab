import React from "react";
import { LabelingSetsService, PLabelingSet } from "../../../api";
//import './subjectlist.css';
import ViewerComponent from "../../../components/viewer";

function LabelingSetListItem(props: any) {
    return (
        <li className="" key={props.lset.id}>
            <p>{props.lset.graph.hemisphere}</p>
            <p>{props.lset.comment}</p>
        </li> 
    )
}

export default class SubjectView extends React.Component {

    constructor(props: any) {
        super(props);
        //this.subjects = props.subjects ? props.subjects : [];
        this.reset();
    }
    reset() {
        this.state = {
            lsets: []
        }
    }

    componentDidUpdate(prevProps: any) {
        const sub = this.props.subject;
        const user = this.props.user;
        if(prevProps.subject != sub || prevProps.user != user) {
            if(sub && user) {
                LabelingSetsService.labelingSetsGetLabelingsetsOfUserForASubject(user.id, sub.id).then((lsets: PLabelingSet[]) => {
                    this.setState({lsets: lsets})
                });
            }
        }
    }

    render() {
        const lsets = this.state.lsets;
        const listItems = lsets ? lsets.map((lset: PLabelingSet) => <LabelingSetListItem lset={lset}></LabelingSetListItem>) : [];  
        const sub = this.props.subject;
        return (
        sub ? (
            <div>
                <h1>{sub.name}</h1>
                <ul className="subject-list">{listItems}</ul> 
                { lsets.length > 0 &&
                    <ViewerComponent lset={this.state.lsets[0]}></ViewerComponent>
                }
            </div>
        ) : (
            <div>
                <p>Select a subject</p>
            </div>
        )
    );}
}
