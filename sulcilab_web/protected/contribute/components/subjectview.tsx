import { Button, Callout } from "@blueprintjs/core";
import React from "react";
import { LabelingSetsService, PLabelingSet, PLabelingSetWithoutLabelings } from "../../../api";
//import './subjectlist.css';

function LabelingSetListItem(props: any) {
    const graph = props.lset.graph;
    return (
        <li className="" key={props.lset.id}>
            <p>{graph.acquisition} / {graph.analysis} / {graph.version} / {graph.session}</p>
            <p>{props.lset.comment}</p>
        </li> 
    )
}

/*
    Props
    =====
    subject: should be remove and use lset.graph.subject
    lset:
    onSelect:
*/
export default class SubjectView extends React.Component {

    constructor(props: any) {
        super(props);
        //this.subjects = props.subjects ? props.subjects : [];
        this.reset();
    }
    reset() {
        this.state = {
            isLoading: false,
            lsets: []
        }
    }

    componentDidUpdate(prevProps: any) {
        const sub = this.props.subject;
        const user = this.props.user;
        if(prevProps.subject != sub || prevProps.user != user) {
            if(sub && user) {
                this.setState({isLoading: true, lsets: []});
                LabelingSetsService.labelingSetsGetLabelingsetsOfUserForASubject(user.id, sub.id).then((lsets: PLabelingSet[]) => {
                    this.setState({lsets: lsets, isLoading: false})
                });
            }
        }
    }

    render() {
        const lsets = this.state.lsets;
        // const leftLabelingSets = lsets ? lsets.filter(lset => { return lset.graph.hemisphere == "L"}).map((lset: PLabelingSet) => <LabelingSetListItem lset={lset}></LabelingSetListItem>) : [];  
        // const rightLabelingSets = lsets ? lsets.filter(lset => { return lset.graph.hemisphere == "R"}).map((lset: PLabelingSet) => <LabelingSetListItem lset={lset}></LabelingSetListItem>) : [];  
        const sub = this.props.subject;

        const rows = [];
        let lset:PLabelingSetWithoutLabelings;
        for(let l=0; l<lsets.length; l++) {
            lset = lsets[l];
            rows.push(
                <tr>
                    <td>{lset.graph.acquisition}</td>
                    <td>{lset.graph.analysis}</td>
                    <td>{lset.graph.version}</td>
                    <td>{lset.graph.session}</td>
                    <td>{lset.graph.hemisphere}</td>
                    <td>{lset.comment}</td>
                    <td>
                        <Button text="Preview" onClick={() => { if(this.props.onPreview) this.props.onPreview(lset);} }/>
                        <Button text="Select" onClick={() => { if(this.props.onSelect) this.props.onSelect(lset);} }/>
                    </td>
                </tr>
            )
        }
        return (
        sub ? (
            <Callout className="bp4-dark">
                <h1>{sub.name}</h1>
                <h2>Your labelings</h2>
                <table className="full-width">
                    <thead>
                        <tr>
                            <td>Acquisition</td>
                            <td>Analysis</td>
                            <td>Version</td>
                            <td>Session</td>
                            <td>Hemisphere</td>
                            <td>Comment</td>
                            <td>Actions</td>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </Callout>
        ) : (
            <Callout className="bp4-dark" icon="info-sign" intent="primary">
                <p>Select a subject</p>
            </Callout>
        )
    );}
}
