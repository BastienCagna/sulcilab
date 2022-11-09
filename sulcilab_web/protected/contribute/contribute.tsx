import React from "react";
import './contribute.css';

import { Link, useNavigate } from "react-router-dom";
import { Button, Callout, ControlGroup, InputGroup, MenuItem, Spinner } from "@blueprintjs/core"
import { Select2, ICreateNewItem, ItemPredicate } from "@blueprintjs/select";

import { DatabasesService, PDatabase, PLabelingSet, PLabelingSetWithoutLabelings, PSubject } from "../../api";
import ProtectedComponent from "../protectedcomponent";
import SubjectList from './components/subjectlist';
import SubjectView from './components/subjectview';
import ViewerComponent from "../../components/viewer";
import withNavigationHook from "../../helper/navigation";

const DatabaseSelect = Select2.ofType<PDatabase>();

function filterDatabase(query: string, database: PDatabase, _index:any, exactMatch:any):  boolean {
    const normalizedTitle = database.name.toLowerCase();
    const normalizedQuery = query.toLowerCase();

    if (exactMatch) {
        return normalizedTitle === normalizedQuery;
    } else {
        return `${normalizedTitle}`.indexOf(normalizedQuery) >= 0;
    }
};

function filterSubject(query: string, subject: PSubject, database: PDatabase|null) {
    /*if(database && database.id && subject.database_id !== database.id) {
        return false;
    }*/
    
    let subjectStr = `${subject.name} ${database ? database.name: ''}`.toLowerCase();
    // subject.labelingsets.forEach(set => {
    //     subjectStr += ` ${set.name} ${set.hemisphere}`
    // });

    return `${subjectStr}`.indexOf(query.toLowerCase()) >= 0;
}

class Contribute extends ProtectedComponent {
    
    constructor(props: any) {
        super(props);
        this.reset();
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
            previewLSet: null
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
                subjects: db.subjects/*.filter((subject) => {
                    return filterSubject(this.state.query, subject, db)
                })*/
            })
        }
    };

    async changeDatabase(db: PDatabase | ICreateNewItem | null, isCreateNewItem: boolean) {
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
                <section className="app-col-small">
                    <form className="sl-box">
                        { !this.state.isLoadingDatabases &&
                            <DatabaseSelect
                                items={this.state.databases}
                                itemPredicate={filterDatabase}
                                itemRenderer={(item: Database, {handleClick, handleFocus}) => {return (<MenuItem key={item.id} text={item.name} onClick={handleClick} onFocus={handleFocus} />)} }
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
                        <InputGroup placeholder="Search..." leftIcon="search" value={this.state.query} onChange={this.queryChanged}/>
                    </form>
                    <p style={{textAlign: "right"}}>{nSubs > 1 ? nSubs + ' subjects' : (nSubs === 1 ? '1 subject' : 'No subjects')} </p>
                
                    { this.state.isLoadingDatabases ? (
                        <Spinner></Spinner>
                    ) : (
                        <div>
                            { this.state.selectedDatabase ? (
                                <ul>
                                    <SubjectList subjects={this.state.subjects.length > 0 ? this.state.subjects : this.state.selectedDatabase.subjects} onSelectSubject={this.handleSelectSubject}/>
                                </ul>
                            ) : (
                                <p>No subjects.</p>
                            )}
                        </div>
                    )}
                </section>


                <section className="app-col-large">
                    <SubjectView user={this.user} subject={this.state.currentSubject} 
                        onPreview={this.handleOnPreview.bind(this)}
                        onSelect={this.handleSelectLabelingSet.bind(this)}></SubjectView>
                </section>

                <section className="app-col-medium" style={{'min-width': 490}}>
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