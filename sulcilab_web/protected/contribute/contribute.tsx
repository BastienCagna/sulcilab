import React from "react";
import './contribute.css';

import SubjectList from './components/subjectlist';
import { count } from "console";
import { Link } from "react-router-dom";
import { Button, ControlGroup, InputGroup, MenuItem, Spinner } from "@blueprintjs/core"
import { Select2, ICreateNewItem, ItemPredicate } from "@blueprintjs/select";

import { DatabasesService, PDatabase, PSubject } from "../../api";
import ProtectedComponent from "../protectedcomponent";


const databases = [
    {id: null, name: "All", path: null},
    {id: '0', name: "Human", path: "/path/to/human/database"},
    {id: '1', name: "Macaque", path: "/path/to/macapype/database"},
    {id: '2', name: "Chimps", path: "/path/to/chimps/database"}
]
const subjects = [
    {id: 0, name: "Aldo", database: databases[0], labelingsets: [{id: "0", name:'Left', hemisphere: "left", completed: 0.8}, {id: "1", name:'Right', hemisphere: "right", completed: 0.75}, {id: "2", name:'Left 2', hemisphere: "left", completed: 0.86}]},
    {id: 1, name: "Frédéric", database: databases[0], labelingsets: [{id: "3", name:'Left', hemisphere: "left", completed: 0.56}, {id: "4", name:'Right', hemisphere: "right", completed: 0.}]},
    {id: 2, name: "Alphonse", database: databases[1], labelingsets: [{id: "5", name:'Left', hemisphere: "left", completed: 0.56}]},
]

interface Database {
    id: string | null;
    name: string;
    path: string | null;
}
interface Subject {
    id: string,
    name: string,
    database: Database,
    labelingsets: []
}

const DatabaseSelect = Select2.ofType<PDatabase>();

function filterDatabase(query: string, database: Database, _index:any, exactMatch:any):  boolean {
    const normalizedTitle = database.name.toLowerCase();
    const normalizedQuery = query.toLowerCase();

    if (exactMatch) {
        return normalizedTitle === normalizedQuery;
    } else {
        return `${normalizedTitle}`.indexOf(normalizedQuery) >= 0;
    }
};

function filterSubject(query: string, subject: PSubject, database: Database|null) {
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
            query: ''
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
        this.setState({
            subjects: this.state.selectedDatabase.subjects.filter((subject) => {
                return filterSubject(this.state.query, subject, this.state.selectedDatabase)
            })
        })
    };

    async changeDatabase(db: PDatabase | ICreateNewItem | null, isCreateNewItem: boolean) {
        this.setState({selectedDatabase: db});
        this.filterSubjects();
    };

    queryChanged = (event: any) => {
        this.setState({query: event.target.value});
        this.filterSubjects();
    }

    render() { 
        const nSubs = this.state.subjects.length;

        return (
        <div className="App">
            <Button className='back-btn'><Link to="/">{'< retour'}</Link></Button>
            <header className="App-header">
                <h1>Sulci Lab</h1>
                <h2>Subjects</h2>
            </header>
            <div className="sl-box list-control">
                <form>
                    <ControlGroup>
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
                    </ControlGroup>
                </form>
                <p style={{textAlign: "right"}}>{nSubs > 1 ? nSubs + ' subjects' : (nSubs === 1 ? '1 subject' : 'No subjects')} </p>
            </div>

            { this.state.isLoadingDatabases ? (
                <Spinner></Spinner>
            ) : (
                <div className="row">
                    <div className="contribute-left-column">
                        { this.state.selectedDatabase ? (
                            <ul>
                                <SubjectList subjects={this.state.subjects.length > 0 ? this.state.subjects : this.state.selectedDatabase.subjects} />
                            </ul>
                        ) : (
                            <p>No subjects.</p>
                        )}
                    </div>
                    <div className="contribute-right-column">
                        <h1>yoyo</h1>
                        <p>Select a subject</p>
                    </div>
                </div>
            )}
        </div>
    );}
}