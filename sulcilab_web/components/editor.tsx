import React from "react";
import './editor.css';

import { LabelingSetsService, PColor, PLabel, PLabeling,} from '../api';
import { Button, Icon, Slider, Spinner, Tab, TabId, Tabs } from "@blueprintjs/core";
import MultiViewerComponent from "./multiviewer";
import { checkBackgrounColor, strColor, threeJsColor } from './viewer_utils'


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

class LabelDetailedView extends React.Component {
    render(){
        const label: PLabel = this.props.label;
        if(!label) {
            return <p>No label</p>
        }
        return <div style={{backgroundColor: strColor(label.color), color: checkBackgrounColor(label.color, "black", "white")}}>
            <h3>{label.shortname}</h3>
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
            showPanel:true
        });
    }
    
    selectTab(newTabId:TabId) {
        this.setState({
            selectedTabId: newTabId
        })
    }

    /*
    * Cast labeling order to each viewer
    */
    labelize(label: PLabel) {
        console.log("labelize with", label);
        for(let viewerRef of this.viewerComponents) {
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
                            <Tab id="graph" title="Graph"
                                panel={<p>Hello</p>}>                            
                            </Tab> 
                            <Tab id="nomenclature" title="Nomenclature" 
                                panel={<NomenclatureView 
                                        nomenclature={this.state.currentNomenclature} 
                                        onClickOnLabel={this.onCurrentLabelChangedHandler.bind(this)}
                                        label={this.state.currentLabel}>
                                    </NomenclatureView>
                                }>
                            </Tab> 
                            <Tab id="fold" title="Fold"
                                panel={<p>Hello</p>}>                            
                            </Tab>     
                            <Tabs.Expander />
                            {/* <Button icon="cross" onClick={this.hidePanel.bind(this)}/> */}
                        </Tabs>
                    </div>
                }
            </div>
        )
    }
}