import React from "react";
import './viewer.css';
import {v4 as uuidv4} from 'uuid';
import * as THREE from 'https://cdn.skypack.dev/three@v0.135.0';

import { Viewer } from "../assets/lib/brainviewer/viewer";
import { LabelingSetsService, PLabeling } from '../api';
import { Icon, Slider, Spinner } from "@blueprintjs/core";


function computeOffset(vertices: any) {
    var sum = [0, 0, 0];
    for (var v = 0; v < vertices.length; v++) {
        sum[0] += vertices[v][0];
        sum[1] += vertices[v][1];
        sum[2] += vertices[v][2];
    }
    var n_points = vertices.length / 3;
    return [sum[0] / n_points, sum[1] / n_points, sum[2] / n_points];
}

/*
    Props
    ======
    lset:
    id:
    width:
    height:    
    onViewerInit:
    toolbar: boolean (default: true)
*/
export default class ViewerComponent extends React.Component {
    viewer: Viewer | null = null;
    id: string;
    indexedLabelings = [];
    width: number;
    height: number;
    showToolbar: boolean;

    constructor(props: any) {
        super(props);
        
        this.id = props.id ? props.id : uuidv4();
        this.width = props.width ? props.width : 800;
        this.height = props.height ? props.height : 600;
        this.showToolbar = props.toolbar != undefined ? props.toolbar : true;
        
        this.state = {
            title: props.title ? props.title : null,
            isLoading: false,
            loadingMessage: null,
            brainMesh: null,
            meshOpacity: 100,
            currentLabel: null
        };
        if(this.props.lset) {
            this.setLabelingSet();
        }
    }

    /*
        Load the brain mesh, the folds meshes, the nomenclature and the labelings
    */
    setLabelingSet() {
        this.setState({isLoading: true, loadingMessage: 'Loading subject ' + this.props.lset.graph.subject.name});
        LabelingSetsService.labelingSetsGetLabelingsetData(this.props.lset.id).then(
            (data: any)=> {
                if(this.viewer) {
                    this.setState({isLoading: true, loadingMessage: 'Adding meshes...'});

                    // Compute the registration offset
                    const offset = computeOffset(data.mesh.vertices);
                    this.viewer.setOffset(offset[0], offset[1], offset[2]);

                    // Add the brain mesh
                    const bmesh = this.viewer.addMesh(
                        data.mesh.vertices, data.mesh.triangles, {meshType: "white"},
                        new THREE.Color()
                    )

                    // Add the folds meshes
                    const default_color = new THREE.Color(0xffe0f1);
                    for(let f=0; f < data.folds_meshes.length; f++) {
                        this.viewer.addMesh(
                            data.folds_meshes[f].vertices, data.folds_meshes[f].triangles, {foldId: f+1},
                            default_color
                        )
                    }

                    // Apply labelings
                    this.setState({isLoading: true, loadingMessage: 'Applying labeling...'});
                    const sceneObjects = this.viewer.allObjects();
                    let mesh, color, foldId;
                    data.labelings.forEach(labeling => {
                        foldId = labeling.fold.vertex;
                        for(let o=0; o < sceneObjects.length; o++) {
                            mesh = sceneObjects[o];
                            if(mesh.userData && mesh.userData.foldId != undefined && mesh.userData.foldId == foldId) {
                                this.indexedLabelings[foldId] = labeling
                                color = labeling.label.color;
                                mesh.material.color = new THREE.Color(color.red/255.0, color.green/255.0, color.blue/255.0);    
                                break;
                            }
                        }
                    });

                    this.setState({
                        title: "Subject " + data.subject.name, 
                        isLoading: false,
                        loadingMessage: "",
                        brainMesh: bmesh
                    });
                }
            }
        )
        if(this.viewer)
            this.viewer.reset();
    }

    updateMeshOpacity(val: number) {
        if(this.state.brainMesh)
            this.state.brainMesh.material.opacity = val / 100;
        this.setState({"meshOpacity": val});
    }

    setCurrentLabel(object: THREE.Object3D) {
        if(object.userData.foldId) {
            const labeling:PLabeling = this.indexedLabelings[object.userData.foldId];
            this.setState({currentLabel: labeling.label});
        } else {
            this.setState({currentLabel: null});
        }
    }

    componentDidMount() {
        this.viewer = new Viewer(this, this.id, this.width, this.height);
        this.viewer.onClickCallBack = this.setCurrentLabel.bind(this);
        // this.viewer.onPositionChange = this.props.onCameraChange
        if(this.props.onViewerInit) this.props.onViewerInit(this.id, this.viewer);
    }

    componentDidUpdate(prevProps: any) {
        if(this.props.lset != prevProps.lset) {
            // if(this.props.lset) {
                this.setLabelingSet();
            // }            
        }
    }

    render() {   
        return (
        <div className="bw-viewer" style={{width: this.width}}>
            {this.state.title &&
                <div className="wb-title">{this.state.title}</div>
            }
            { this.state.isLoading && (
                <div style={{position: "absolute"}}>
                    <div  style={{position: "relative", left: (this.width/2) - 70, top: (this.height/2) - 50, width: '160px'}} >
                        <Spinner className="wb-spinner" size="40"></Spinner>
                        <p style={{color: '#5c5a5a', margin: "5px", background:"#141414", opacity:0.8}}>{this.state.loadingMessage}</p>
                    </div>
                </div>
            )}

            <div className="bw-viewerport" id={this.id}></div>

            { this.showToolbar && 
                <div className="bw-toolbar">
                    <div className="bw-infos">
                        <span className="bw-brand">Web Brain Viewer</span>
                        { this.state.brainMesh && (
                            <div>
                                { this.state.currentLabel &&
                                    <span>
                                        {this.state.currentLabel.shortname} - {this.state.currentLabel.fr_name}
                                    </span>
                                }
                            </div>
                        )}
                    </div>
                    
                    { this.state.brainMesh && ( 
                        <div className="bw-controls">
                            <div className="bw-control" >
                                <Icon icon="eye-open" />
                                <input type="range" min="0" max="100" step="5" 
                                    value={this.state.meshOpacity}
                                    onChange={this.meshOpacityChangeHandler.bind(this)}/>
                            </div>
                        </div>
                    )}
                </div>
            }
        </div>
    );}

    private meshOpacityChangeHandler(event) {
        this.updateMeshOpacity(event.target.value);
    }

    private getChangeHandler(key: string) {
        return (value: number) => this.setState({ [key]: value });
    }

    private renderPercentage(val: number) {
        return `${Math.round(val * 100)}%`;
    }
}