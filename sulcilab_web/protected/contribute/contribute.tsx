import React, { RefObject } from "react";
import './contribute.css';

import { Link, useNavigate } from "react-router-dom";
import { Button, Callout, ControlGroup, InputGroup, MenuItem, Overlay, Spinner } from "@blueprintjs/core"
import { Select2, ICreateNewItem, ItemPredicate } from "@blueprintjs/select";

import { DatabasesService, LabelingSetsService, PDatabase, PGraph, PLabelingSet, PLabelingSetWithoutLabelings, PSubject } from "../../api";
import ProtectedComponent from "../protectedcomponent";
import SubjectList from './components/subjectlist';
import SubjectView from './components/subjectview';
import ViewerComponent from "../../components/viewer";
import withNavigationHook from "../../helper/navigation";


const DatabaseSelect = Select2.ofType<PDatabase>();
const SubjectSelect = Select2.ofType<PSubject>();


function filterDatabase(query: string, database: PDatabase, _index:any, exactMatch:any):  boolean {
    const normalizedTitle = database.name.toLowerCase();
    const normalizedQuery = query.toLowerCase();

    if (exactMatch) {
        return normalizedTitle === normalizedQuery;
    } else {
        return `${normalizedTitle}`.indexOf(normalizedQuery) >= 0;
    }
};

function filterSubject(query: string, subject: PSubject, _index:any, exactMatch:any) {
    let subjectStr = `${subject.name}`.toLowerCase();
    let normalizedQuery = query.toLowerCase();

    if (exactMatch) {
        return subjectStr === normalizedQuery;
    } else {
        return `${subjectStr}`.indexOf(normalizedQuery) >= 0;
    }
}

class Contribute extends ProtectedComponent {
    subjectView = null; //:RefObject<SubjectView> = React.createRef();

    constructor(props: any) {
        super(props);
        this.reset();
        this.subjectView = React.createRef();
    }

    reset() {
        this.state = {
            isLoadingDatabases: false,
            databases: [],
            selectedDatabase: null,
            subjects: [],
            selectedSubjects: [],
            query: '',
            currentSubject: null,
            selectedLabelingSets: [],
            previewLSet: null,
            isProcessingSubject: false
        };
    }

    async loadDatabases() {
        this.setState({isLoadingDatabases: true});
        const databases = await DatabasesService.databasesRead();
        this.setState({databases: databases});
        if(!this.selectedDatabase && databases.length > 0) {
            this.changeDatabase(databases[0], false);
        }
        this.setState({isLoadingDatabases: false});
    }

    // async setSelectedDatabase(db: PDatabase) {
    //     this.setState({selectedDatabase: db});
    //     this.filterSubjects();
    // }

    componentDidMount() {
        this.loadDatabases();
    }

    filterSubjects = (database:PDatabase|null = null) => {
        const db = database ? database : this.state.selectedDatabase;
        //console.log('query:', db.subjects);
        if(db) {
            this.setState({
                subjects: db.subjects,/*.filter((subject) => {
                    return filterSubject(this.state.query, subject, db)
                })*/
                currentSubject: db.subjects[0]
            })
        }
    };

    async changeDatabase(db: PDatabase | null) {
        this.setState({selectedDatabase: db, currentSubject: null});
        this.filterSubjects(db as PDatabase);
    };

    queryChanged = (event: any) => {
        this.setState({query: event.target.value});
        this.filterSubjects();
    }

    handleSelectSubject = (subject: PSubject) => {
        this.setState({currentSubject: subject});
    }

    handleSelectLabelingSet(lset: PLabelingSetWithoutLabelings) {
        const selecteds = this.state.selectedLabelingSets;
        const idx = selecteds.indexOf(lset);
        if(idx==-1) {
            selecteds.push(lset);
            this.setState({selectedLabelingSets: selecteds})
        }
    }

    handleOnPreview(lset: PLabelingSetWithoutLabelings) {
        this.setState({previewLSet: lset});
    }

    handleDuplicateLabelingSet(lset: PLabelingSetWithoutLabelings) {
        // Duplicate Labeling Set
        this.setState({isProcessingSubject: true});
        LabelingSetsService.labelingSetsDuplicate(lset.id).then(
            newLSet => {
                this.setState({isProcessingSubject: false});
                this.subjectView.current.reload();
            }
        )
    }

    handleNewLabelingSet(graph: PGraph) {
        this.setState({isProcessingSubject: true});
        LabelingSetsService.labelingSetsNew(graph.id).then(
            newLSet => {
                this.setState({isProcessingSubject: false});
                this.subjectView.current.reload();
            }
        );
    }

    handleEditLabelingSet(lset: PLabelingSetWithoutLabelings) {
        // Duplicate Labeling Set
    }

    handleDeleteLabelingSet(lset: PLabelingSetWithoutLabelings) {
        if(window.confirm(`Do you really want to delete labeling set #${lset.id}`) == false)
            return
        this.setState({isProcessingSubject: true});
        LabelingSetsService.labelingSetsDeleteLabelingset(lset.id).then(
            newLSet => {
                this.setState({isProcessingSubject: false});
                this.subjectView.current.reload();
            }
        );
    }

    handleShareLabelingSet(lset: PLabelingSetWithoutLabelings) {

    }

    openInViewer() {
        // const navigate = useNavigate();
        //console.log(this.props.navigation, this.props.navigation.navigate);
        this.props.navigation('/view', { state : {lsets: this.state.selectedLabelingSets }});
    }

    openInEditor() {
        // const navigate = useNavigate();
        //console.log(this.props.navigation, this.props.navigation.navigate);
        this.props.navigation('/edit', { state : {lsets: this.state.selectedLabelingSets }});
    }

    unSelect(lset: PLabelingSet) {
        const sel = this.state.selectedLabelingSets;
        sel.splice(sel.indexOf(lset), 1);
        this.setState({
            selectedLabelingSets: sel
        })
    }

    // async autoselect() {
    //     const sel = [];
    //     if(this.state.subjects) {
    //         const nsubs = 24;//this.state.subjects.length;
    //         let sub;
    //         for(let s=0; s<nsubs; s++) {
    //             sub = this.state.subjects[s];
    //             let lsets: PLabelingSet[] = await LabelingSetsService.labelingSetsGetLabelingsetsOfUserForASubject(this.user.id, sub.id);
    //             sel.push(lsets[0])
    //         }
    //         this.setState({selectedLabelingSets: sel})
    //     }
    // }

    render() { 
        const nSubs = this.state.subjects.length;
        const selectedLSets = this.state.selectedLabelingSets.map(lset => {
                return <li key={lset.id}>{lset.graph.subject.name} / {lset.graph.hemisphere} <Button icon="cross" lset-id={lset.id} onClick={() =>{ this.unSelect(lset);}}/> </li>    
            })
        return (
        <div className="App">
            <Button className='back-btn'><Link to="/">{'< retour'}</Link></Button>
            <header className="App-header">
                <h1>Sulci Lab</h1>
                <p>Select one or several labeling sets and open them in the editor.</p>
            </header>

            <div className="app-row page">
                <Overlay>
                    <h1>Sharing</h1>
                    
                </Overlay>
                <section className="app-col-large">
                    <div>
                        <form className="sl-box labelingset-search-bar">
                            { !this.state.isLoadingDatabases &&
                                <DatabaseSelect
                                    items={this.state.databases}
                                    itemPredicate={filterDatabase}
                                    itemRenderer={(item: PDatabase, {handleClick, handleFocus}) => {return (<MenuItem key={item.id} text={item.name} onClick={handleClick} onFocus={handleFocus} />)} }
                                    noResults={<MenuItem disabled={true} text="No results." />}
                                    onItemSelect={this.changeDatabase.bind(this)}
                                    //query={this.state.selectedDatabase ? this.state.selectedDatabase.name : ""}
                                    //onActiveItemChange={this.changeDatabase}
                                >
                                    { this.state.databases &&
                                        <Button text={this.state.selectedDatabase ? this.state.selectedDatabase.name: ""} rightIcon="double-caret-vertical" icon="database"/>
                                    }
                                </DatabaseSelect>
                            }
                            {/* <InputGroup placeholder="Search..." leftIcon="search" value={this.state.query} onChange={this.queryChanged}/> */}
                            <SubjectSelect
                                    items={this.state.subjects}
                                    itemPredicate={filterSubject}
                                    itemRenderer={(item: PSubject, {handleClick, handleFocus}) => {return (<MenuItem key={item.id} text={item.name} onClick={handleClick} onFocus={handleFocus} />)} }
                                    noResults={<MenuItem disabled={true} text="No results." />}
                                    onItemSelect={this.handleSelectSubject.bind(this)}
                                    //query={this.state.selectedDatabase ? this.state.selectedDatabase.name : ""}
                                    //onActiveItemChange={this.changeDatabase}
                                >
                                    { this.state.subjects &&
                                        <Button text={this.state.currentSubject ? this.state.currentSubject.name: ""} rightIcon="double-caret-vertical" icon="person"/>
                                    }
                                </SubjectSelect>

                            {/* <Button text="Auto selection" intent="warning" onClick={this.autoselect.bind(this)}/> */}
                            <p style={{textAlign: "right"}}>{nSubs > 1 ? nSubs + ' subjects' : (nSubs === 1 ? '1 subject' : 'No subjects')} </p>
                        </form>                    
                        { this.state.isLoadingDatabases && <Spinner></Spinner> }
                    </div>


                    { this.state.isProcessingSubject && <Spinner></Spinner> }
                    <SubjectView ref={this.subjectView} user={this.user} subject={this.state.currentSubject} 
                        onPreview={this.handleOnPreview.bind(this)}
                        onSelect={this.handleSelectLabelingSet.bind(this)}
                        onCreateNew={this.handleNewLabelingSet.bind(this)}
                        onDuplicate={this.handleDuplicateLabelingSet.bind(this)}
                        onShare={this.handleShareLabelingSet.bind(this)}
                        onEdit={this.handleEditLabelingSet.bind(this)}
                        onDelete={this.handleDeleteLabelingSet.bind(this)}
                    ></SubjectView>
                </section>

                <section className="app-col-medium" style={{'minWidth': 490}}>
                    <ViewerComponent title="Preview" width={480} height={320} lset={this.state.previewLSet}></ViewerComponent>
                    <Callout>
                        <div>
                            <h3>Selection</h3>
                            <ul>
                                {selectedLSets}
                            </ul>
                            <Button text="Open in the viewer" intent="primary" onClick={this.openInViewer.bind(this)}></Button>
                            <Button text="Open in the editor" intent="success" onClick={this.openInEditor.bind(this)}></Button>
                        </div>
                    </Callout>
                </section>
            </div>
        </div>
    );}
}


export default withNavigationHook(Contribute);