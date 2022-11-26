import React from "react";
import './viewer.css';
import {v4 as uuidv4} from 'uuid';
import * as THREE from 'three';

import { Viewer } from "../assets/lib/brainviewer/viewer";
import { LabelingSetsService, PLabel, PLabeling, PNomenclature } from '../api';
import { Button, Icon, Slider, Spinner } from "@blueprintjs/core";

import { computeOffset, getLabel, threeJsColor} from './viewer_utils';

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
                        // Set the mesh color and add the labeling to mesh user data
                        for(let o=0; o < sceneObjects.length; o++) {
                            mesh = sceneObjects[o];
                            // If the object has a mesh index
                            if(mesh.userData && mesh.userData.meshIndex != undefined && mesh.userData.meshIndex == meshIndex) {
                                label = getLabel(data.nomenclature, labeling.label_id); //labeling.label.color;
                                if(label) {
                                    color = label.color;
                                    mesh.material.color = threeJsColor(color);
                                    mesh.userData['labeling'] = labeling;
                                    mesh.userData['originalLabeling'] = {...labeling}; // deep copy
                                    mesh.userData['originalColor'] = {...color}; // deep copy
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

        if(object && object.userData.meshIndex && object.userData.labeling)
            label = getLabel(this.state.currentNomenclature, object.userData.labeling.label_id);
        
        this.setState({currentLabel: label});
        if(this.props.onCurrentLabelChanged) {
            this.props.onCurrentLabelChanged(label);
        }
    }

    checkHasChanged() {
        if(!this.viewer) return;
        const objects = this.viewer.allObjects()
        for(let object of objects) {
            if(object.userData && object.userData.labeling && object.userData.originalLabeling && object.userData.originalLabeling.label_id !== object.userData.labeling.label_id) {
                this.setState({hasChanged: true});
                return;
            }
        }
        this.setState({hasChanged: false});
    }

    labelize(label: PLabel) {
        let selectedObjects;
        if(!label || !this.viewer || !this.state.editable) {
            return
        }
        selectedObjects = this.viewer.getSelection();
        selectedObjects.forEach(object => {
            if(object.userData.labeling && object.userData.labeling.label_id !== label.id) {
                // Update object color
                object.material.color = threeJsColor(label.color);
                // Update object label id
                object.userData.labeling.label_id = label.id;
                // Check if at least one labeling has changed
                if(object.userData.originalLabeling.label_id != label.id) {
                    this.setState({hasChanged: true});
                } else {
                    this.checkHasChanged();
                }
            }
        });
    }

    revertChanges() {
        this.viewer?.allObjects().forEach(object => {
            if(object.userData && object.userData.labeling && object.userData.originalLabeling && object.userData.originalLabeling.label_id !== object.userData.labeling.label_id) {
                // Reset object color
                object.material.color = threeJsColor(object.userData.originalColor);
                // Reset object label id
                object.userData.labeling.label_id = object.userData.originalLabeling.label_id;
            }
        })
        this.checkHasChanged();
    }

    save() {
        if(!this.viewer || !this.state.editable) return;

        const labelings: PLabeling[] = [];
        const updatedObjects: any[] = [];
        const objects = this.viewer.allObjects();

        for(let object of objects) {
            if(object.userData && object.userData.labeling && object.userData.originalLabeling && object.userData.originalLabeling.label_id !== object.userData.labeling.label_id) {
                labelings.push(object.userData.labeling);
                updatedObjects.push(object);
            }
        }

        this.setState({
            isLoading: true, 
            loadingMessage: `Saving updates (${labelings.length} labelings have changed)...`,
            editable: false
        });
        LabelingSetsService.labelingSetsSaveLabelings(this.props.lset.id, labelings).then(
            data => {
                // Update originalLabeling of each saved objects
                updatedObjects.forEach(object => {
                    object.userData.originalLabeling = {...object.userData.labeling};
                })
                // Clear loading message and haschanged and set editable back to true
                this.setState({
                    isLoading: false, 
                    loadingMessage: null, 
                    hasChanged: false,
                    editable: true
                });
            }
        );
    }

    componentDidMount() {
        this.viewer = new Viewer(this, this.id, this.width, this.height);
        // this.viewer.onClickCallBack = this.setCurrentLabel.bind(this);
        this.viewer.onLeftClickCallBack = this.setCurrentLabel.bind(this);
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
                        <Button icon="reset" onClick={this.revertChanges.bind(this)}></Button>
                        <Button icon="floppy-disk" intent="danger" onClick={this.save.bind(this)}></Button>
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