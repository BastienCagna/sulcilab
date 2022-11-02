import React from "react";
import './viewer.css';
import {v4 as uuidv4} from 'uuid';
import * as THREE from 'https://cdn.skypack.dev/three@v0.135.0';

import { Viewer } from "../assets/lib/brainviewer/viewer";
import { GraphsService, PMeshData } from '../api';

export default class ViewerComponent extends React.Component {
    viewer: Viewer = null;
    id: string;
    // axialClippingPlane;
    // coronalClippingPlane;
    // sagitalClippingPlane;

    constructor(props: any) {
        super(props)
        this.id = uuidv4();
        this.state = {
            // triangles: null
        }
        if(this.props.lset) {
            this.setGraph();
        }

        // this.axialClippingPlane = new THREE.Plane(new THREE.Vector3( -1, 0, 0 ), 100 );
	    // this.coronalClippingPlane = new THREE.Plane(new THREE.Vector3( 0, -1, 0 ), 60 );
	    // this.sagitalClippingPlane = new THREE.Plane(new THREE.Vector3( 0, 0, -1 ), 50 );
        // this.viewer.renderer.clippingPlanes = [this.axialClippingPlane, this.coronalClippingPlane, this.sagitalClippingPlane];
    }

    setGraph() {
        console.log("set graph")
        GraphsService.graphsGetMeshData(this.props.lset.graph.id).then(
            (meshData: PMeshData)=> {
                this.setState({meshdata: meshData});
                console.log("add mesh");
                if(this.viewer) {
                    this.viewer.addMesh(
                        meshData.vertices, meshData.triangles
                    )
                }
            }
        )
    }
    componentDidMount() {
        this.viewer = new Viewer(this, this.id, 800, 600);
    }

    componentDidUpdate(prevProps: any) {
        if(prevProps.lset != prevProps.lset) {
            if(this.props.lset) {
                this.setGraph();
            }            
        }
    }

    render() { return (
        <div className="bw-viewer" id={this.id}>
        </div>
    );}
}