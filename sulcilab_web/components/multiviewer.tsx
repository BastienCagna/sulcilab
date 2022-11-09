import React from "react";
import './viewer.css';
import {v4 as uuidv4} from 'uuid';
import * as THREE from 'https://cdn.skypack.dev/three@v0.135.0';

import { Viewer } from "../assets/lib/brainviewer/viewer";
import { LabelingSetsService, PLabel, PLabeling } from '../api';
import { Icon, Slider, Spinner } from "@blueprintjs/core";
import ViewerComponent from "./viewer";

import { getLabel } from './viewer_utils';

/*
    Props
    =====
    width:
    height:
    cols:
    rows:
    lsets:
*/
export default class MultiViewerComponent extends React.Component {
    id: string;
    nRows: number;
    nCols: number
    width: number;
    height: number;
    viewers: Viewer[] = [];
    viewersIds: string[] = [];
    length: number;
    showToolbar: boolean;

    constructor(props: any) {
        super(props);

        this.id = uuidv4();
        this.width = props.width ? props.width : 800;
        this.height = props.height ? props.height : 600;
        this.nRows = props.rows ? props.rows : 1;
        this.nCols = props.cols ? props.cols : 1;
        this.length = this.nRows * this.nCols;        
        this.showToolbar = props.toolbar != undefined ? props.toolbar : true;
        
        for(let v=0; v < this.length; v++) {
            this.viewersIds.push(this.id + "_" + v.toString());
            this.viewers.push(null);
        }

        document.addEventListener('keyup', this.onKeyUp.bind(this));
        this.init();
    }

    init() {
        // Check that all the nomenclature are the same
        let nomId = null;
        if(this.props.lsets) {
            for(let lset of this.props.lsets) {
                if(nomId == null) {
                    nomId = lset.nomenclature_id;
                } else {
                    if(nomId != lset.nomenclature_id) {
                        throw 'The labeling sets use different nomenclatures';
                    }
                }
            }
        }

        this.state = {
            currentNomenclature: null,
            currentLabel: null,
            meshOpacity: 100
        };
    }

    // FIXME: labelise is oin viewer component not on the js class
    labelize() {
        if(this.state.currentLabel) {
            for(let viewer of this.viewers) {
                viewer.labelise(this.state.currentLabel)
            }
        }
    }
    resetSelection() {
        for(let viewer of this.viewers) {
            viewer.resetSelection();
        }
    }
    onKeyUp(event: any) {
        switch (event.key) {
            case "l": this.labelize(); break;
            case "k": this.resetSelection(); break;
        }
    }

    allViewersRegisteredHandler() {
        // For now only the first viewer can be master
        for(let v=1; v < this.length; v++) this.viewers[0].addSlave(this.viewers[v]);
    }

    onCurrentLabelChangedHandler(label: PLabel) {
        if(this.state.currentNomenclature) {
            // TODO: Verify that the label is in the nomenclature ?
            this.setState({currentLabel: label});
        } else {
            this.setState({currentLabel: null});
        }
    }

    nomenclatureChangedHandler(nomenclature: any) {
        if(!this.state.nomenclature) {
            this.setState({
                currentNomenclature: nomenclature
            })
        }
    }

    updateMeshOpacity(val: number) {
        // if(this.state.brainMesh)
        //     this.state.brainMesh.material.opacity = val / 100;
        this.setState({"meshOpacity": val});
    }


    render() {
        const vWidth = Math.ceil((this.width) / this.nCols); 
        const vHeight = this.height / this.nRows; 
        const rows = [];
        let cols, v=0;
        for(let r=0; r < this.nRows; r++) {
            cols = [];
            for(let c=0; c < this.nCols; c++) {
                cols.push(<td key={v}><ViewerComponent  key={v}
                                id={this.viewersIds[v]} 
                                width={vWidth} height={vHeight} 
                                lset={this.props.lsets[v]} 
                                onViewerInit={this.registerViewer.bind(this)}
                                onNomenclatureChanged={this.nomenclatureChangedHandler.bind(this)}
                                onCurrentLabelChanged={this.onCurrentLabelChangedHandler.bind(this)}
                                toolbar={false}
                            ></ViewerComponent></td>);
                v++;
            }
            rows.push(<tr key={r}>{cols}</tr>)
        }
        return (
            <div style={{width: this.width}}>
                <table className="bw-grid">
                    <tbody>
                        {rows}
                    </tbody>
                </table>
                { this.showToolbar && 
                    <div className="bw-toolbar">
                        <div className="bw-infos">
                            <span className="bw-brand">Web Brain Viewer</span>
                            { this.state.currentNomenclature &&
                                <span><Icon icon="label" ></Icon>{this.state.currentNomenclature.name}
                                </span>
                            }
                            { this.state.currentNomenclature && (
                                <div>
                                    { this.state.currentLabel &&
                                        <span>
                                            <Icon icon="tag"></Icon>
                                            {this.state.currentLabel.shortname} - {this.state.currentLabel.fr_name}
                                        </span>
                                    }
                                </div>
                            )}
                        </div>
                        
                        <div className="bw-controls">
                            <Icon icon="predictive-analysis" />
                            <div className="bw-control" >
                                <select>
                                    <option value="white">White</option>
                                    <option value="hemi">Hemi</option>
                                </select>
                            </div>
                            <div className="bw-control" >
                                <input type="range" min="0" max="100" step="5" 
                                    value={this.state.meshOpacity}
                                    onChange={this.meshOpacityChangeHandler.bind(this)}/>
                            </div>
                        </div>
                    </div>
                }
            </div>
        );
    }

    private registerViewer(viewerId: string, viewer: Viewer){
        const idx = this.viewersIds.indexOf(viewerId);
        this.viewers[idx] = viewer;
        
        for(let v=0; v < this.length; v++) {
            if(!this.viewers[v]) {
                return;
            }
        }
        this.allViewersRegisteredHandler();
    }

    private meshOpacityChangeHandler(event: any) {
        this.updateMeshOpacity(event.target.value);
    }
}