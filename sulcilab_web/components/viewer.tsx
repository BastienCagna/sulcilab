import React from "react";
import './viewer.css';
import {v4 as uuidv4} from 'uuid';
import * as THREE from 'https://cdn.skypack.dev/three@v0.135.0';

import { Viewer } from "../assets/lib/brainviewer/viewer";
import { LabelingSetsService, PLabel, PLabeling, PNomenclature } from '../api';
import { Button, Icon, Slider, Spinner } from "@blueprintjs/core";

import { computeOffset, getLabel } from './viewer_utils';

/*
    Props
    ======
    lset:
    id:
    width:
    height:    
    onViewerInit:
    onNomenclatrueChanged:
    onCurrentLabelChanged:
    toolbar: boolean (default: true)
*/
export default class ViewerComponent extends React.Component {
    viewer: Viewer | null = null;
    id: string;
    indexedLabelings = [];
    width: number;
    height: number;
    showToolbar: boolean;
    onCurrentLabelChanged: any;

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
            currentLabel: null,
            selectedObject: null,
            currentNomenclature: null,
            editable: this.props.editable != undefined ? this.props.editable : true, //false
            hasChanged: false
        };
    }

    /*
        Load the brain mesh, the folds meshes, the nomenclature and the labelings
    */
    setLabelingSet() {
        this.setState({isLoading: true, loadingMessage: 'Loading subject ' + this.props.lset.graph.subject.name});
        LabelingSetsService.labelingSetsGetLabelingsetData(this.props.lset.id).then(
            (data: any)=> {
                if(this.viewer) {
                    this.setState({
                        currentNomenclature: data.nomenclature,
                        loadingMessage: 'Adding meshes...'
                    });

                    // Compute the registration offset
                    const offset = computeOffset(data.mesh.vertices);
                    this.viewer.setOffset(offset[0], offset[1], offset[2]);

                    // Add the brain mesh
                    const bmesh = this.viewer.addMesh(
                        data.mesh.vertices, data.mesh.triangles, {meshType: "white"},
                        new THREE.Color(1,1, 1)
                    )

                    // Add the folds meshes
                    const default_color = new THREE.Color(0xffe0f1);
                    for(let f=0; f < data.folds_meshes.length; f++) {
                        this.viewer.addMesh(
                            data.folds_meshes[f].vertices, data.folds_meshes[f].triangles, {meshIndex: f+1},
                            default_color
                        )
                    }

                    const folds = data.folds;

                    // Apply labelings
                    this.setState({isLoading: true, loadingMessage: 'Applying labeling...'});
                    const sceneObjects = this.viewer.allObjects();
                    let mesh, label, color, meshIndex;
                    data.labelings.forEach(labeling => {
                        // Found the corresponding mesh index
                        meshIndex = null;
                        for(let f=0; f < folds.length; f++) {
                            if(labeling.fold_id == folds[f].id) {
                                meshIndex = folds[f].mesh_index;
                                break;
                            }
                        }
                        for(let o=0; o < sceneObjects.length; o++) {
                            mesh = sceneObjects[o];
                            if(mesh.userData && mesh.userData.meshIndex != undefined && mesh.userData.meshIndex == meshIndex) {
                                this.indexedLabelings[meshIndex] = labeling
                                label = getLabel(data.nomenclature, labeling.label_id); //labeling.label.color;
                                if(label) {
                                    color = label.color;
                                    mesh.material.color = new THREE.Color(color.red/255.0, color.green/255.0, color.blue/255.0);    
                                }
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

                    if(this.props.onNomenclatureChanged) this.props.onNomenclatureChanged(data.nomenclature);
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
        let label : PLabel | null = null;

        if(object.userData.meshIndex)
            label = getLabel(this.state.currentNomenclature, this.indexedLabelings[object.userData.meshIndex].label_id);
        
        this.setState({currentLabel: label, selectedObject: object});
        if(this.props.onCurrentLabelChanged) {
            this.props.onCurrentLabelChanged(label);
        }
    }

    labelize(label: PLabel) {
        const object = this.state.selectedObject;
        if(object) {
            // TODO: verify if the label is different from the original
            this.indexedLabelings[object.userData.meshIndex].label = label;
            object.material.color = new THREE.Color(255, 255, 255);
            this.setState({hasChanged: true})
        }
    }

    componentDidMount() {
        this.viewer = new Viewer(this, this.id, this.width, this.height);
        // this.viewer.onClickCallBack = this.setCurrentLabel.bind(this);
        this.viewer.onDoubleClickCallBack = this.setCurrentLabel.bind(this);
        // this.viewer.onPositionChange = this.props.onCameraChange
        if(this.props.onViewerInit) this.props.onViewerInit(this.id, this.viewer);

        if(this.props.lset) {
            this.setLabelingSet();
        }
    }

    componentDidUpdate(prevProps: any) {
        if(this.props.lset != prevProps.lset) {
            // if(this.props.lset) {
                this.setLabelingSet();
            // }            
        } else if(this.props.editable != prevProps.editable) {
            this.setState({
                editable: this.props.editable
            })
        }
    }

    render() {   
        return (
        <div className="bw-viewer" style={{width: this.width}}>
            {this.state.hasChanged &&
                <div style={{position: "absolute"}}>
                    <div className="wb-edit-controls" style={{position: "relative", left: this.width - 120, top: 5}} >
                        <Button icon="reset"></Button>
                        <Button icon="floppy-disk" intent="danger"></Button>
                    </div>
                </div>
            }
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
                        { this.state.currentNomenclature && (
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
                                <Icon icon="predictive-analysis" />
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