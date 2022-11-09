import { Button, Callout, Tag } from "@blueprintjs/core";
import React from "react";
import { LabelingSetsService, PLabelingSet, PLabelingSetWithoutLabelings } from "../../../api";
import './subjectview.css';

/*
    Props
    =====
    graph:
    lsets:
*/
function LabelingSetListItem(props: any) {
    let rows;

    const graph = props.graph;
    if(!props.lsets || props.lsets.length == 0) {
        rows = []
    }
    else {
        rows = props.lsets.filter(lset => {return lset.graph.id == graph.id}).map(lset => {return (
            <li key={lset.id}>
                <Tag>#{lset.id}</Tag>
                <span>{lset.comment}</span>
                <div className="controls">
                    <Button text="Preview" onClick={() => { if(props.onPreview) props.onPreview(lset);} }/>
                    <Button text="Select" onClick={() => { if(props.onSelect) props.onSelect(lset);} }/>
                </div>
            </li>
        )});
    }

    return (
        <li>
            <div className="item-header"> 
                <div className="controls">
                    <Button text="New" icon="add"></Button>
                </div>
                <h4>{graph.acquisition} / {graph.analysis} / {graph.version} / {graph.hemisphere}</h4>
            </div>
           <ul className="sview-lsetlist">
                {rows}
            </ul>
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
        const sub = this.props.subject;

        const rows = [];
        if(this.props.subject) {
            for(let graph of this.props.subject.graphs) {
                rows.push(
                    <li key={graph.id}><LabelingSetListItem graph={graph} lsets={lsets} onPreview={this.props.onPreview} onSelect={this.props.onSelect}></LabelingSetListItem></li>
                )
            }
        }
        return (
        sub ? (
            <Callout className="bp4-dark">
                <h1>{sub.name}</h1>
                <ul className="sview-graphlist">
                    {rows}
                </ul>
            </Callout>
        ) : (
            <Callout className="bp4-dark" icon="info-sign" intent="primary">
                <p>Select a subject</p>
            </Callout>
        )
    );}
}
