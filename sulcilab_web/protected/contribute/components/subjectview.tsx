import { Button, Callout, Card, Icon, MenuItem, Overlay, PortalProvider, Tag } from "@blueprintjs/core";
import { MultiSelect2, Select2 } from "@blueprintjs/select";
import React from "react";
import { LabelingSetsService, PLabelingSet, PUser, SharedLabelingSetsService, UsersService } from "../../../api";
import './subjectview.css';
import { formatDate } from "../../../utils";


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
    disabled: bool
    intent:
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
            sharingUsers: [],
            allUsers: [],
            notSharedUsers: null,
            originalSharing: null,
            hasChanged: false
        }
    }

    setUserLists() {
        SharedLabelingSetsService.sharedLabelingSetsSharingRecipient(this.props.lset.id).then(
            users => {
                // TODO: do this on server side
                const notsharing_users = [];
                let found;
                for(let user of this.state.allUsers) {
                    found = users.some(u => { return u.id == user.id });
                    if(!found) {
                        notsharing_users.push(user);
                    }
                }
                
                this.setState({
                    sharingUsers: users,
                    originalSharing: [...users],
                    hasChanged: false,
                    notSharedUsers: notsharing_users
                })
            }
        )
    }

    componentDidMount() {
        UsersService.usersListAll().then(
            users => {
                this.setState({allUsers: users})
            }
        )
    }

    componentDidUpdate(prevProps: Readonly<{}>): void {
        if(prevProps.lset != this.props.lset || !this.state.notSharedUsers) {
            this.setUserLists();
        }
    }

    toggleOverlay() {
        this.setState({isOpen: !this.state.isOpen})
    }

    selectUser(user: PUser) {
        const users = this.state.sharingUsers;
        const nusers = this.state.notSharedUsers;
        users.push(user);
        nusers.splice(nusers.indexOf(user));
        this.setState({sharingUsers: users, notSharedUsers: nusers, hasChanged: this.hasChanged()})
    }
    unselectUser(user: PUser) {   
        const users = this.state.sharingUsers;
        const nusers = this.state.notSharedUsers;
        users.splice(users.indexOf(user));
        nusers.push(user);
        this.setState({sharingUsers: users, notSharedUsers: nusers, hasChanged: this.hasChanged()})
    }

    hasChanged() {
        let all_found;
        if(this.state.sharingUsers) {
            all_found = this.state.originalSharing.every(u => {
                return this.state.sharingUsers.indexOf(u) >= 0;
            });
            // If all original users are in the current and the original and the current have same length
            // Then there is no change
            return !(all_found && this.state.originalSharing.length == this.state.sharingUsers.length);
        }
        return false;
    }

    save() {
        if(this.hasChanged()) {
            const uids = [];
            for(let user of this.state.sharingUsers) {
                uids.push(user.id)
            }
            SharedLabelingSetsService.sharedLabelingSetsUpdateSharings(
                this.props.lset.id,
                uids
            ).then(nothing => {
                this.setUserLists();
            })
        }
        // else, nothing to do
    }

    render() {
        const lset = this.props.lset;
        return <div>
            <Button icon="share" intent={this.props.intent ? this.props.intent : 'none'} onClick={() => {this.toggleOverlay()}} disabled={this.props.disabled}/>
            <Overlay isOpen={this.state.isOpen} onClose={() => {this.toggleOverlay()}}>
                <Card interactive={true} className="sharing-overlay">
                    <h3>Sharing #{lset.id}</h3>
                    <p>
                        This graph is shared to:
                    </p>
                    <br />
                    <form>
                        <UserSelect
                            items={this.state.notSharedUsers}
                            selectedItems={this.state.sharingUsers}
                            itemPredicate={filterUser}
                            itemRenderer={(item: PUser, {handleClick, handleFocus}) => {
                                return (<MenuItem key={item.id} text={item.username + ' (' + item.email + ')'} onClick={handleClick} onFocus={handleFocus} />)} 
                            }
                            tagRenderer={(item: PUser) => {
                                return (<MenuItem key={item.id} text={item.username + ' (' + item.email + ')'} />)} 
                            }
                            noResults={<MenuItem disabled={true} text="No results." />}
                            onItemSelect={this.selectUser.bind(this)}
                            onRemove={this.unselectUser.bind(this)}
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
                        { this.state.hasChanged && 
                            <Button intent="success" onClick={() => {this.save(); }}>
                                Save
                            </Button>
                        }
                    </div>
                </Card>
            </Overlay>
        </div>
    }
}


function LabelingSetItem(props: any) {
    const lset = props.lset;
    const allowEdit = props.user.is_admin || props.user.id == lset.author_id;
    return <li key={lset.id}>
        <Tag>#{lset.id}</Tag>
        <Tag>{lset.author.username}</Tag>
        { lset.updated_at && lset.updated_at != lset.created_a ?
            <Tag><Icon icon="updated" size={12} /> {formatDate(lset.updated_at)}</Tag>
        :
            <Tag><Icon icon="add" size={12} /> {formatDate(lset.created_at)}</Tag>
        }
        { lset.parent_id && 
            <Tag aria-label={"Fork from #" + lset.parent_id}><Icon icon="git-new-branch" size={14}/> #{lset.parent_id}</Tag>
        }
        <Tag>{lset.nomenclature.name}</Tag>
        <span>{lset.comment}</span>
        <div className="controls">
            {/* <Button icon="edit" intent="primary" onClick={() => { if(props.onEdit) props.onEdit(lset);} } disabled={!allowEdit}/> */}
            {/* <Button icon="share" intent="primary" onClick={() => { if(props.onShare) props.onShare(lset);} }/> */}
            <Button icon="duplicate" intent="primary" onClick={() => { if(props.onDuplicate) props.onDuplicate(lset);} }/>
            <SharingOverlay lset={lset} disabled={!allowEdit} intent={lset.sharings.length > 0 ? 'success' : 'primary'}></SharingOverlay>
            <Button icon="trash" intent="danger" onClick={() => { if(props.onDelete) props.onDelete(lset);} } disabled={!allowEdit}/>
            <Button icon="eye-open" intent="success" onClick={() => { if(props.onPreview) props.onPreview(lset);} }/>
            <Button icon="add-to-artifact" intent="success" onClick={() => { if(props.onSelect) props.onSelect(lset);} }/>
            {/* <Button icon="duplicate" text="Duplicate" onClick={() => { if(props.onPreview) props.onDuplicate(lset);} }/>
            <Button icon="eye-open" text="Preview" onClick={() => { if(props.onPreview) props.onPreview(lset);} }/>
            <Button icon="add-to-artifact" text="Select" onClick={() => { if(props.onSelect) props.onSelect(lset);} }/> */}
        </div>
    </li>
}

/*
    Props
    =====
    graph:
    lsets:
    user:
*/
function LabelingSetListItem(props: any) {
    let rows;
    const graph = props.graph;
    if(!props.lsets || props.lsets.length == 0) {
        rows = []
    }
    else {
        rows = props.lsets.filter(lset => {return lset.graph.id == graph.id}).map(lset => {
            return (
                <LabelingSetItem user={props.user} lset={lset}
                    onPreview={props.onPreview} 
                    onSelect={props.onSelect} 
                    onCreateNew={props.onCreateNew}
                    onEdit={props.onEdit} 
                    onDuplicate={props.onDuplicate} 
                    onShare={props.onShare} 
                    onDelete={props.onDelete}
                ></LabelingSetItem>
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
                { rows.length > 0 ?
                    rows
                :
                    <p>No labeling for this graph. <a onClick={() => { if(props.onCreateNew) props.onCreateNew(graph);}}>Clic here</a> to create one.</p>
                }
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
    user:
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

    reload() {
        const sub = this.props.subject;
        const user = this.props.user;
        if(sub && user) {
            this.setState({isLoading: true, lsets: []});
            LabelingSetsService.labelingSetsGetLabelingsetsOfUserForASubject(user.id, sub.id).then((lsets: PLabelingSet[]) => {
                this.setState({lsets: lsets, isLoading: false})
            });
        } else {
            this.setState({lsets: []});
        }
    }

    componentDidUpdate(prevProps: any) {
        const sub = this.props.subject;
        const user = this.props.user;
        if(prevProps.subject != sub || prevProps.user != user) {
            this.reload();
        }
    }

    render() {
        const lsets = this.state.lsets;
        const sub = this.props.subject;

        const rows = [];
        if(this.props.subject) {
            for(let graph of this.props.subject.graphs) {
                rows.push(
                    <li key={graph.id}><LabelingSetListItem graph={graph} lsets={lsets} user={this.props.user}
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
