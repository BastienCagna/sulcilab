import React from "react";
import './viewer.css';
import {v4 as uuidv4} from 'uuid';
import * as THREE from 'https://cdn.skypack.dev/three@v0.135.0';

import { Viewer } from "../assets/lib/brainviewer/viewer";
import { LabelingSetsService, PLabeling } from '../api';
import { Icon, Slider, Spinner } from "@blueprintjs/core";
import ViewerComponent from "./viewer";

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
    }

    init() {
        this.state = {
        };
    }

    allViewersRegisteredHandler() {
        // For now only the first viewer can be master
        for(let v=1; v < this.length; v++) this.viewers[0].addSlave(this.viewers[v]);
    }

    render() {   
        const vWidth = Math.ceil((this.width) / this.nCols); 
        const vHeight = this.height / this.nCols; 
        const rows = [];
        let cols, v=0;
        for(let r=0; r < this.nRows; r++) {
            cols = [];
            for(let c=0; c < this.nCols; c++) {
                cols.push(<td><ViewerComponent 
                                id={this.viewersIds[v]} 
                                width={vWidth} height={vHeight} 
                                lset={this.props.lsets[v]} 
                                onViewerInit={this.registerViewer.bind(this)}
                                toolbar={false}
                            ></ViewerComponent></td>);
                v++;
            }
            rows.push(<tr>{cols}</tr>)
        }
        return (
            <div style={{width: this.width}}>
                <table className="bw-grid">
                    {rows}
                </table>
                { this.showToolbar && 
                    <div className="bw-toolbar">
                        <div className="bw-infos">
                            <span className="bw-brand">Web Brain Viewer</span>
                        </div>
                        
                        {/* { this.state.brainMesh && ( 
                            <div className="bw-controls">
                                <div className="bw-control" >
                                    <Icon icon="eye-open" />
                                    <input type="range" min="0" max="100" step="5" 
                                        value={this.state.meshOpacity}
                                        onChange={this.meshOpacityChangeHandler.bind(this)}/>
                                </div>
                            </div>
                        )} */}
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

}