import { Button, Callout, Card, MenuItem, Overlay, Tag } from "@blueprintjs/core";
import { MultiSelect2, Select2 } from "@blueprintjs/select";
import React from "react";
import { LabelingSetsService, PLabelingSet, PLabelingSetWithoutLabelings, PUser, UsersService } from "../../../api";
import './subjectview.css';

const UserSelect = MultiSelect2.ofType<PUser>();



function filterUser(query: string, user: PUser, _index:any, exactMatch:any) {
    let subjectStr = `${user.username} ${user.email}`.toLowerCase();
    let normalizedQuery = query.toLowerCase();

    // TODO: add this
    // if(!user.is_active) {
    //     return false
    // }
    if (exactMatch) {
        return subjectStr === normalizedQuery;
    } else {
        return `${subjectStr}`.indexOf(normalizedQuery) >= 0;
    }
}
/*
    Props
    =====
    lset:
*/
class SharingOverlay extends React.Component {

    constructor(props: any) {
        super(props);
        //this.subjects = props.subjects ? props.subjects : [];
        this.reset();
    }
    reset() {
        this.state = {
            isLoading: false,
            isOpen: false,
            users: [],
            selectedUsers: []
        }
    }

    componentDidMount() {
        UsersService.usersListAll().then(
            users => {
                this.setState({users: users})
            }
        )
    }

    toggleOverlay() {
        this.setState({isOpen: !this.state.isOpen})
    }

    selectUser(user: PUser) {
        const users = this.state.selectedUsers;
        users.push(user);
        this.setState({selectedUsers: users})
    }

    render() {
        return <div>
            <Button icon="share" intent="primary" onClick={() => {this.toggleOverlay()}} />
            <Overlay isOpen={this.state.isOpen} onClose={this.toggleOverlay}>
                <Card interactive={true} className="sharing-overlay">
                    <h3>I'm an Overlay!</h3>
                    <p>
                        This is a simple container with some inline styles to position it on the screen. Its CSS
                        transitions are customized for this example only to demonstrate how easily custom
                        transitions can be implemented.
                    </p>
                    <p>
                        Click the "Focus button" below to transfer focus to the "Show overlay" trigger button
                        outside of this overlay. If persistent focus is enabled, focus will be constrained to the
                        overlay. Use the key to move to the next focusable element to illustrate
                        this effect.
                    </p>
                    <p>
                        Click the "Make me scroll" button below to make this overlay's content really tall, which
                        will make the overlay's container (but not the page) scrollable
                    </p>
                    <br />
                    <form>
                        <UserSelect
                            items={this.state.users}
                            selectedItems={this.state.selectedUsers}
                            itemPredicate={filterUser}
                            itemRenderer={(item: PUser, {handleClick, handleFocus}) => {
                                return (<MenuItem key={item.id} text={item.username} onClick={handleClick} onFocus={handleFocus} />)} 
                            }
                            tagRenderer={(item: PUser) => {
                                return (<MenuItem key={item.id} text={item.username} />)} 
                            }
                            noResults={<MenuItem disabled={true} text="No results." />}
                            onItemSelect={this.selectUser.bind(this)}
                            //query={this.state.selectedDatabase ? this.state.selectedDatabase.name : ""}
                            //onActiveItemChange={this.changeDatabase}
                        >
                            <Button text="Select users..." rightIcon="mugshot" icon="search"/>
                        </UserSelect>
                    </form>
                    <div>
                        <Button intent="danger" onClick={() => {this.toggleOverlay(); }}>
                            Close
                        </Button>
                    </div>
                </Card>
            </Overlay>
        </div>
    }
}


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
                <Tag>Author ID: {lset.author_id}</Tag>
                <Tag>Creation: {lset.created_at}</Tag>
                { lset.updated_at && 
                    <Tag>Last update: {lset.updated_at}</Tag>
                }
                { lset.parent_id && 
                    <Tag>Fork of: #{lset.parent_id}</Tag>
                }
                <span>{lset.comment}</span>
                <div className="controls">
                    <Button icon="edit" intent="primary" onClick={() => { if(props.onEdit) props.onEdit(lset);} }/>
                    {/* <Button icon="share" intent="primary" onClick={() => { if(props.onShare) props.onShare(lset);} }/> */}
                    <SharingOverlay lset={lset}></SharingOverlay>
                    <Button icon="duplicate" intent="primary" onClick={() => { if(props.onDuplicate) props.onDuplicate(lset);} }/>
                    <Button icon="trash" intent="danger" onClick={() => { if(props.onDelete) props.onDelete(lset);} }/>
                    <Button icon="eye-open" intent="success" onClick={() => { if(props.onPreview) props.onPreview(lset);} }/>
                    <Button icon="add-to-artifact" intent="success" onClick={() => { if(props.onSelect) props.onSelect(lset);} }/>
                    {/* <Button icon="duplicate" text="Duplicate" onClick={() => { if(props.onPreview) props.onDuplicate(lset);} }/>
                    <Button icon="eye-open" text="Preview" onClick={() => { if(props.onPreview) props.onPreview(lset);} }/>
                    <Button icon="add-to-artifact" text="Select" onClick={() => { if(props.onSelect) props.onSelect(lset);} }/> */}
                </div>
            </li>
        )});
    }

    return (
        <li>
            <div className="item-header"> 
                <div className="controls">
                    <Button text="New" icon="add" onClick={() => { if(props.onCreateNew) props.onCreateNew(graph);} }></Button>
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
                    <li key={graph.id}><LabelingSetListItem graph={graph} lsets={lsets} 
                                onPreview={this.props.onPreview} 
                                onSelect={this.props.onSelect} 
                                onCreateNew={this.props.onCreateNew}
                                onEdit={this.props.onEdit} 
                                onDuplicate={this.props.onDuplicate} 
                                onShare={this.props.onShare} 
                                onDelete={this.props.onDelete}
                        ></LabelingSetListItem></li>
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
