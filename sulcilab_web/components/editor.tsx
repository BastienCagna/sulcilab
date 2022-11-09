import React from "react";
import './editor.css';
import {v4 as uuidv4} from 'uuid';
import * as THREE from 'https://cdn.skypack.dev/three@v0.135.0';

import { Viewer } from "../assets/lib/brainviewer/viewer";
import { LabelingSetsService, PColor, PLabel, PLabeling,} from '../api';
import { Button, Icon, Slider, Spinner, Tab, TabId, Tabs } from "@blueprintjs/core";
import MultiViewerComponent from "./multiviewer";
import { render } from "@testing-library/react";
import { strColor } from './viewer_utils'


class LabelView extends React.Component {
    onClick() {
        if(this.props.onClick) this.props.onClick(this.props.label);
    }
    render(){
        const label: PLabel = this.props.label;
        if(!label) {
            <li>No label</li>
        }
        return <li key={label.id} style={{backgroundColor: strColor(label.color)}} onClick={this.onClick.bind(this)}>{label.shortname}</li>
    }
}

class NomenclatureView extends React.Component {
    constructor(props: any) {
        super(props);
    }

    onSelectLabel(label: PLabel) {
        console.log("click on ", label.shortname)
        if(this.props.onClickOnLabel) {
            this.props.onClickOnLabel(label);
        }
    }
    render() {
        const nom = this.props.nomenclature;
        if(!nom) {
            return <p>No data</p>
        }
        const labels = nom.labels.map(label => { return <LabelView label={label} onClick={() => {console.log("coucou"); this.onSelectLabel(label);}}></LabelView>});
        return (
            <div>
                <h3>{nom.name}</h3>
                <ul className="editor-labels">
                    {labels}
                </ul>
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
    }
    init() {
        super.init();
        this.setState({
            selectedTabId:"nomenclature"
        })
    }
    
    selectTab(newTabId:TabId) {
        this.setState({
            selectedTabId: newTabId
        })
    }

    render() {
        const viewer = super.render();

        return (
            <div className="app-row">
                <div className="editor-viewer-col">
                    {viewer}
                </div>
                <div className="editor-side-col">
                    <Tabs onChange={this.selectTab.bind(this)} selectedTabId={this.state.selectedTabId} defaultSelectedTabId="nomenclature">
                        <Tab id="graph" title="Graph"
                            panel={<p>Hello</p>}>                            
                        </Tab> 
                        <Tab id="nomenclature" title="Nomenclature" 
                            panel={<NomenclatureView nomenclature={this.state.currentNomenclature} onClickOnLabel={this.onCurrentLabelChangedHandler.bind(this)}></NomenclatureView>}>
                        </Tab> 
                        <Tab id="fold" title="Fold"
                            panel={<p>Hello</p>}>                            
                        </Tab>     
                        <Tabs.Expander />
                        <Button icon="cross"/>
                    </Tabs>
                </div>
            </div>
        )
    }
}