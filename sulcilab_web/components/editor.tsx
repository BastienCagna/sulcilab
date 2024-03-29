import React from "react";
import './editor.css';

import { LabelingSetsService, PColor, PLabel, PLabeling, PLabelingSet,} from '../api';
import { Button, Icon, Slider, Spinner, Tab, TabId, Tabs } from "@blueprintjs/core";
import MultiViewerComponent from "./multiviewer";
import { checkBackgrounColor, strColor, threeJsColor } from './viewer_utils'
import { Select2 } from "@blueprintjs/select";


const LSetSelect = Select2.ofType<PLabelingSet>();


class LabelView extends React.Component {
    onClick() {
        if(this.props.onClick) this.props.onClick(this.props.label);
    }
    render(){
        const label: PLabel = this.props.label;
        if(!label) {
            return <li>No label</li>
        }
        return <li key={label.id} 
                   style={{backgroundColor: strColor(label.color), color: checkBackgrounColor(label.color, "black", "white")}} 
                   onClick={this.onClick.bind(this)}>{label.shortname}</li>
    }
}

function HelpPanel(props: any) {
    return (<div className="editor-help-panel">
            <h4>Controls</h4>
            <ul>
                <li>Left click: select + change current label</li>
                <li>Right click: just select</li>
                <li>"l": apply current label</li>
                <li>"k": clear selection</li>
            </ul>
        </div>)
}

class InfosPanel extends React.Component {
    constructor(props: any) {
        super(props);

        this.state = {
            // lsets: props.lsets ? props.lsets : []
            lset: null
        }
    }

    render() {
        return <div className="editor-help-panel">
            <h4>Infos</h4>
            <LSetSelect 
                items={this.props.lsets}
                
            ></LSetSelect>
        </div>
    }
}

class LabelDetailedView extends React.Component {
    render(){
        const label: PLabel = this.props.label;
        if(!label) {
            return <p>No label</p>
        }
        return <div style={{backgroundColor: strColor(label.color), color: checkBackgrounColor(label.color, "black", "white")}}>
            <h3>{label.shortname}</h3>
            <p>ID: #{label.id} </p>
            <h4>{label.fr_name}</h4>
            <p>{label.fr_description}</p>
        </div>
    }
}


/*
*   Props
*   =====
*   label:
*/
class NomenclatureView extends React.Component {
    constructor(props: any) {
        super(props);

        this.state = {
            label: null
        }
    }

    clearLabel() {
        this.setState({
            label: null
        })
    }
    onSelectLabel(label: PLabel) {
        if(this.props.onClickOnLabel) {
            this.props.onClickOnLabel(label);
        }
    }

    componentDidUpdate(prevProps: any) {
        if((prevProps.label || this.props.label) && prevProps.label !== this.props.label) {
            this.setState({label: this.props.label})
        }
    }
    render() {
        const nom = this.props.nomenclature;
        if(!nom) {
            return <p>No data</p>
        }
        const labels = nom.labels.map(label => { return <LabelView key={label.id} label={label} onClick={() => {this.onSelectLabel(label);}}></LabelView>});
        return (
            <div>
                <h3>{nom.name}</h3>
                {this.state.label ? (
                    <div>
                        <Button icon="chevron-left" onClick={this.clearLabel.bind(this)}>Nomenclature</Button>
                        <LabelDetailedView label={this.state.label}></LabelDetailedView>
                    </div>
                ) : (
                    <ul className="editor-labels">
                        {labels}
                    </ul>
                )}
            </div>
        )
    }
}

/*
    Props
    =====
    width:
    height:
    cols:
    rows:
    lsets:
*/
export default class EditorComponent extends MultiViewerComponent {

    constructor(props: any) {
        super(props);
        this.width = this.width > 600 ? 0.8 * this.width : 600;
        document.addEventListener('keyup', this.onKeyUp.bind(this));
    }
    init() {
        super.init({
            selectedTabId:"nomenclature",
            showPanel:true,
            currentObjects: []
        });
    }
    
    selectTab(newTabId:TabId) {
        this.setState({
            selectedTabId: newTabId
        })
    }

    // onCurrentLabelChangedHandler(label: PLabel) {
    //     super.onCurrentLabelChangedHandler(label);
    //     const objects = [];
    //     let sel;
    //     for(let viewer of this.viewers) {
    //         sel = viewer.getSelection();
    //         if(sel.length > 0) {
    //             objects.push(sel[0]);
    //             console.log("selected", sel[0]);
    //         }
    //     }
    //     this.setState({currentObjects: objects})
    // }

    /*
    * Cast labeling order to each viewer
    */
    labelize(label: PLabel) {
        for(let viewerRef of this.viewerComponents) {
            console.log("labelize", label);
            viewerRef.current.labelize(label);
        }
    }

    onKeyUp(event: any) {
        switch (event.key) {
            case "l": this.labelize(this.state.currentLabel); break;
            case "k": this.resetSelection(); break;
        }
    }


    // showPanel() {
    //     this.setState({showPanel: true});
    // }
    // hidePanel() {
    //     this.setState({showPanel: false});
    // }
    render() {
        const viewer = super.render();
        //const oViews = this.state.currentObjects.map(obj => {return <li key={obj.id}><ObjectView object={obj}></ObjectView></li>})
        return (
            <div className="app-row">
                {/* <div className="editor-open-panel">
                    <Button icon="open" onClick={this.showPanel.bind(this)}/>
                </div> */}
                <div className="editor-viewer-col">
                    {viewer}
                </div>
                { this.state.showPanel &&
                    <div className="editor-side-col">
                        <Tabs onChange={this.selectTab.bind(this)} selectedTabId={this.state.selectedTabId} defaultSelectedTabId="nomenclature">
                            {/* <Tab id="graph" title="Graph"
                                panel={<ul>{oViews}</ul>}>
                            </Tab>  */}
                            <Tab id="nomenclature" title="Nomenclature" 
                                panel={<NomenclatureView 
                                        nomenclature={this.state.currentNomenclature} 
                                        onClickOnLabel={this.onCurrentLabelChangedHandler.bind(this)}
                                        label={this.state.currentLabel}>
                                    </NomenclatureView>
                                }>
                            </Tab> 
                            <Tab id="helps" title="Helps" 
                                panel={<HelpPanel />
                                }>
                            </Tab> 
                            {/* <Tab id="fold" title="Fold"
                                panel={<p>Hello</p>}>                            
                            </Tab>      */}
                            <Tabs.Expander />
                            {/* <Button icon="cross" onClick={this.hidePanel.bind(this)}/> */}
                        </Tabs>
                        
                    </div>
                }
            </div>
        )
    }
}