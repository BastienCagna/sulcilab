import React from "react";
import './contribute.css';

import { Link } from "react-router-dom";
import { Button, Callout, ControlGroup, InputGroup, MenuItem, Spinner } from "@blueprintjs/core"
import { Select2, ICreateNewItem, ItemPredicate } from "@blueprintjs/select";

import { DatabasesService, PDatabase, PLabelingSetWithoutLabelings, PSubject } from "../../api";
import ProtectedComponent from "../protectedcomponent";
import SubjectList from './components/subjectlist';
import SubjectView from './components/subjectview';
import ViewerComponent from "../../components/viewer";



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


export default class Contribute extends ProtectedComponent {
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


    filterSubjects = () => {
        // console.log("database:", this.state.selectedDatabase);
        // console.log('query:', this.state.query);
        if(this.state.selectedDatabase) {
            this.setState({
                subjects: this.state.selectedDatabase.subjects.filter((subject) => {
                    return filterSubject(this.state.query, subject, this.state.selectedDatabase)
                })
            })
        }
    };

    async changeDatabase(db: PDatabase | ICreateNewItem | null, isCreateNewItem: boolean) {
        this.setState({selectedDatabase: db});
        this.filterSubjects();
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

    render() { 
        const nSubs = this.state.subjects.length;
        const selectedLSets = this.state.selectedLabelingSets.map(lset => {
                return <li>{lset.graph.subject.name} / {lset.graph.hemisphere} <Button icon="cross"/> </li>    
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
                                onItemSelect={this.changeDatabase}
                                query={this.state.selectedDatabase ? this.state.selectedDatabase.name : ""}
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
                            <Button text="Open in the viewer" intent="primary"></Button>
                            <Button text="Open in the editor" intent="success"></Button>
                        </div>
                    </Callout>
                </section>
            </div>
        </div>
    );}
}