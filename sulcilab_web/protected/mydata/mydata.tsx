import { Button, MenuItem } from "@blueprintjs/core";
import { Select2 } from "@blueprintjs/select";
import { DatabasesService, PDatabase } from "../../api";
import { formatDate } from "../../utils";
import ProtectedComponent from "../protectedcomponent";
import './mydata.css'


const DatabaseSelect = Select2.ofType<PDatabase>();

export default class MyData extends ProtectedComponent {

    
    constructor(props: any) {
        super(props);
        this.reset();
    }

    reset() {
        this.state = {
            isLoadingDatabases: false,
            databases: [],
            selectedDatabase: null
        };
    }


    async loadDatabases() {
        this.setState({isLoadingDatabases: true});
        const databases = await DatabasesService.databasesIndex(0, 100, true);
        this.setState({databases: databases});
        if(!this.state.selectedDatabase && databases.length > 0) {
            this.changeDatabase(databases[0]);
        }
        this.setState({isLoadingDatabases: false});
    }

    async changeDatabase(db: PDatabase | null) {
        this.setState({selectedDatabase: db, currentSubject: null});
        // this.filterSubjects(db as PDatabase);
    };

    componentDidMount() {
        this.loadDatabases();
    }

    render() {
        const rows = this.state.selectedDatabase ? this.state.selectedDatabase.subjects.map(sub => {return (
            <tr>
                <td><input type="checkbox" /></td>
                <td>{sub.name}</td>
                <td>Imported {formatDate(sub.created_at)} </td>
                <td>0</td>
                <td><Button icon="export" intent="primary"/><Button icon="trash" intent="danger"/></td>
            </tr>
        )}) : [];

        return <div>
            <div className="app-row page">
                <section className="app-col-large">
                    <Button icon="chevron-left" text="Back" onClick={() => { window.location = "./contribute" }} /> 
                    <h2>Your data</h2>

                    { !this.state.isLoadingDatabases &&
                        <DatabaseSelect
                            items={this.state.databases}
                            // itemPredicate={filterDatabase}
                            itemRenderer={(item: PDatabase, {handleClick, handleFocus}) => {return (<MenuItem key={item.id} text={item.name} onClick={handleClick} onFocus={handleFocus}></MenuItem>)} }
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

                    { this.state.selectedDatabase && (
                        <div>
                            <Button icon="plus" text="Add a subject" />
                            <Button icon="export" text="Export..." />
                            <table>
                                <tbody>
                                    <th>Public:</th>
                                    <td>{this.state.selectedDatabase.is_public ? "Yes" : "No"}</td>
                                </tbody>
                            </table>
                            <table>
                                <thead>
                                    <tr>
                                        <th></th>
                                        <th>Name</th>
                                        <th>State</th>
                                        <th>Labeling sessions</th>
                                        <th></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rows}
                                </tbody>
                            </table>
                        </div>
                    )}
                </section>
            </div>
        </div>
    }
}