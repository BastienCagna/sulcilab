import {PointOfView, Viewer} from './viewer.js';
import {LogMessageType, Logger, DEFAULT_LOG_MESSAGE_TIMEOUT, Loggable} from './logger.js';
import { randNInt } from './utils.js';
import * as THREE from 'three';


const DEFAULT_MESH_COLOR = 0xffaaaa;
const BRAIN_MESH_COLOR = '#c9c9c9';


// Import of RxJS is performed by the html page
// <script src="https://cdnjs.cloudflare.com/ajax/libs/rxjs/6.5.2/rxjs.umd.js"></script>
//import * as rxjs from './rxjs.js';

function checkBackgrounColor(hexcolor, darkColor, lightColor){
    var r = parseInt(hexcolor.substr(1,2),16);
    var g = parseInt(hexcolor.substr(3,2),16);
    var b = parseInt(hexcolor.substr(4,2),16);
    var yiq = ((r*299)+(g*587)+(b*114))/1000;
    // Return new color if to dark, else return the original
    return (yiq < 40) ? lightColor : darkColor;
}

function computeOffset(vertices) {
    var sum = [0, 0, 0];
    for (var v = 0; v < vertices.length; v++) {
        sum[0] += vertices[v][0];
        sum[1] += vertices[v][1];
        sum[2] += vertices[v][2];
    }
    var n_points = vertices.length / 3;
    return [sum[0] / n_points, sum[1] / n_points, sum[2] / n_points];
}


class MyHttpClient extends Loggable {
    csrftoken = null;

    constructor(logger=null) {
        super(logger);
        this.csrftoken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    }

    get(url, callback, errorCallback=null) {
        return this._send("GET", url, callback,  null, errorCallback);
    }

    post(url, data, callback, errorCallback=null) {
        return this._send("POST", url, callback, data, errorCallback);
    }

    _send(method, url, callback, data=null, errorCallback=null) {
        var xhttp = new XMLHttpRequest()
        if (callback)
            xhttp.onload = function () { callback(JSON.parse(xhttp.response)); };
        /*xhttp.onerror = (e) => { console.log("ajax error:", e); this.log("Cannot load data from " + url, LogMessageType.SYSTEM_ERROR); if(errorCallback) errorCallback(e); };*/
        xhttp.open(method, url, true);
        xhttp.onreadystatechange = () => {
            // if(callback && xhttp.status >= 200 && xhttp.status < 300) {
            //     callback(JSON.parse(xhttp.response));
            // }
            if(xhttp.status >= 400 && errorCallback) {
                this.log("Cannot load data from " + url, LogMessageType.SYSTEM_ERROR);
                errorCallback(xhttp.response);
            }
        };
        xhttp.setRequestHeader('X-CSRFToken', this.csrftoken);
        xhttp.send(JSON.stringify(data));
    }
}

class APIInterface {
    constructor(apiUrl, logger=null) {
        this.baseUrl = apiUrl;
        this.client = new MyHttpClient(logger);
        this.logger = logger;
    }

    getNomenclature(nomenclatureId, hemi, callback) {
        return this.client.get(this.baseUrl + "/nomenclature/" + nomenclatureId + "/" + hemi, callback);
    }

    getGraphMesh(graphId, callback, mesh_type=null) {
        return this.client.get(this.baseUrl + "/graph/" + graphId + "/mesh" + (mesh_type ? "/" + mesh_type : ""), callback);
    }

    getGraphLabelings(labelingSetId, callback) {
        return this.client.get(this.baseUrl + "/labelingset/" + labelingSetId + '/labelings', callback);
    }
    setGraphLabelings(labelingSetId, labelings, callback) {
        return this.client.post(this.baseUrl + "/labelingset/" + labelingSetId + '/labelings/save', labelings, callback);
    }

    getLabelingSet(labelingSetId, callback) {
        return this.client.get(this.baseUrl + "/labelingset/" + labelingSetId, callback);
    }

    getLabelingSetExampleIds(labelId, nSamples, callback) {
        return this.client.get(this.baseUrl + "/labelingset/" + labelId + '/examples/' + nSamples, callback);
    }
}


class GraphViewer extends Loggable {
    id;
    domElement;
    api;
    selectedMeshId;
    spinnerDOMElement;
    viewer;
    nomenclature;
    brainMesh;
    selectable;
    controllable;
    slaves;
    loadingLevel;
    width;
    height;
    onLoadingCompleted = null;
    onClickCallback = null;
    onDoubleClickCallback = null;

    constructor(domElementId, width, height, api_url, logger=null) {
        super(logger);
        this.id = domElementId;
        this.domElement = document.getElementById(domElementId);
        this.api = new APIInterface(api_url, logger);
        this.spinnerDOMElement = document.getElementById(this.id + '-spinner');
        this.selectable = true;
        this.controllable = true;
        this.slaves = [];
        this.width = width;
        this.height = height;
        this.reset();
    }

    reset() {
        // Setup the viewer
        this.viewer = new Viewer(this, this.id, this.width, this.height);
        this.viewer.onClickCallBack = this.onClickHandler.bind(this);
        this.viewer.onDoubleClickCallBack = this.onDoubleClickHandler.bind(this);
        this.nomenclature = null;
        this.brainMesh = null;
        this.selectedMeshId = null;
	    this.axialClippingPlane = new THREE.Plane(new THREE.Vector3( -1, 0, 0 ), 100 );
	    this.coronalClippingPlane = new THREE.Plane(new THREE.Vector3( 0, -1, 0 ), 60 );
	    this.sagitalClippingPlane = new THREE.Plane(new THREE.Vector3( 0, 0, -1 ), 50 );
        this.viewer.renderer.clippingPlanes = [this.axialClippingPlane, this.coronalClippingPlane, this.sagitalClippingPlane];
        this.resetLoadingLevel();
    }

    onClickHandler(obj) {
        if(this.onClickCallBack) {
            this.onClickCallBack(obj);
        }
    }

    onDoubleClickHandler(obj) {
        if(this.onDoubleClickCallBack) {
            this.onDoubleClickCallBack(obj);
        }
    }

    addSlave(slave) {
        this.slaves.push(slave);
        this.viewer.addSlave(slave.viewer);
        slave.onDoubleClickCallBack = this.onDoubleClickHandler.bind(this);
    }

    addLabelledSulci(sulci){
        var lab = null;
        var meta = null;
        for (var s = 0; s < sulci.length; s++) {
            lab = sulci[s];
            if(lab.label) {
                meta = {
                    'fold': lab.fold,
                    'label': lab.label,
                    //'nomenclature': lab.label.nomenclature.name
                }
            }
            else {
                meta = {
                    'fold': lab.fold,
                    'label': null,
                    //'nomenclature': null
                }
            }
            this.viewer.addMesh(
                lab.mesh.vertices, 
                lab.mesh.triangles, 
                meta, 
                lab.label ? lab.label.color : DEFAULT_MESH_COLOR, 
                true,   // Sulci are selectable
                false   // But not transparent
            );
        }
    }

    loadGraphMesh(graphId) {
        this.api.getGraphMesh(
            graphId,
            mesh => {
                var offset = computeOffset(mesh.vertices);
                this.viewer.setOffset(offset[0], offset[1], offset[2]);
                this.brainMesh = this.viewer.addMesh(
                    mesh.vertices, 
                    mesh.triangles, 
                    mesh.metadata, 
                    BRAIN_MESH_COLOR, 
                    false, // Not selectable
                    true   // Transparente
                );
                this.decreaseLoadingLevel();
            }
        );
    }

    loadNomenclature(nomenclatureId, hemi) {
        this.api.getNomenclature(
            nomenclatureId,
            hemi,
            data => { this.nomenclature = data; this.decreaseLoadingLevel(); }
        );
    }

    loadExamples(labelingSetId) {
        this.api.getLabelingSetExampleIds(
            labelingSetId, this.slaves.length,
            data => {
                // Set subviewer graphs
                for(let s=0; s < this.slaves.length; s++) {
                    if(data.ids[s]) {
                        this.slaves[s].loadLabelingSet(data.ids[s]);
                    } else {
                        this.slaves[s].reset();
                    }
                }
            }
        );     
    }

    loadLabelingSet(labelistSetId) {
        this.increaseLoadingLevel(3);
        this.labelingSet = null;

        // Request LabelingSet (brain mesh, nomenclature and labelingset id)
        this.api.getLabelingSet(
            labelistSetId,
            labelingSet => {
                // Request Labelings: list of association between graph's vertices and nomenclature)
                this.labelingSet = labelingSet;
                this.api.getGraphLabelings(
                    labelingSet.id,
                    data => {
                        this.addLabelledSulci(data.labelings);
                        this.decreaseLoadingLevel();
                    }
                );

                // Update point of view depending of the hemisphere
                this.viewer.setCameraPointOfView(labelingSet.hemisphere == "L" ? PointOfView['LeftToRight'] : PointOfView['RightToLeft']);

                this.loadGraphMesh(labelingSet.graph_id);
                this.loadNomenclature(labelingSet.nomenclature_id, labelingSet.hemisphere);
                this.viewer.setLegend(labelingSet.subject_name + ' / ' + labelingSet.hemisphere);
                if(this.slaves.length > 0) {
                    this.loadExamples(labelingSet.id);
                }                
            }
        );
    }

    setLabel(meshId, label, nomenclature) {
        var obj = this.viewer.getObjectById(meshId);
        obj.userData.label = label;
        obj.userData.nomenclature =nomenclature.name;
        obj.material.color.setStyle(label.color);
        return obj.userData;
    }

    setBrainMeshOpacity(alpha) {
        if(this.brainMesh) {
            this.brainMesh.material.opacity = alpha;
        }
        for(let slave of this.slaves) {
            slave.setBrainMeshOpacity(alpha);
        }
    }

    setAxialClipping(v) { 
        this.axialClippingPlane.constant = v;
        for(let slave of this.slaves) slave.setAxialClipping(v);
    }
    setCoronalClipping(v) { 
        this.coronalClippingPlane.constant = v;
        for(let slave of this.slaves) slave.setCoronalClipping(v);
    }
    setSagitalClipping(v) { 
        this.sagitalClippingPlane.constant = v;
        for(let slave of this.slaves) slave.setSagitalClipping(v);
    }

    resetLoadingLevel() {
        this.loadingLevel = 0;
        this._checkLoadingLevel();
    }
    increaseLoadingLevel(l=1) {
        this.loadingLevel += l;
        this._checkLoadingLevel();
    }
    decreaseLoadingLevel(l=1) {
        this.loadingLevel -= l;
        this._checkLoadingLevel();
    }
    _checkLoadingLevel() {
        if(this.spinnerDOMElement) this.spinnerDOMElement.hidden = this.loadingLevel > 0;
        if(this.onLoadingCompleted && this.loadingLevel == 0) this.onLoadingCompleted();
    }
}

class Editor extends Loggable {
    id;
    api;
    viewer;
    currentNomenclature;
    currentLabel;
    domElement;
    nomenclatureDOMElement;
    labelDOMElement;
    selectedMeshId;
    brainMesh;
    mouseIsOver;
    msgDOMElement;
    titleDOMElement;
    nomenclatureButtonDOMElement;

    constructor(domElementId, width, height) {
        super(null);
        this.id = domElementId;//'viewer-' + randNInt(1, 100000).toString();
        this.domElement = document.getElementById(domElementId);
        this.mouseIsOver = false; 
        this.domElement.onmouseover = function(){ this.mouseIsOver = true; }.bind(this);
        this.domElement.onmouseout = function(){ this.mouseIsOver = false; }.bind(this);

        this.currentNomenclature = null;
        this.selectedMeshId = null;

        const nbrSubViewers = 2;
        const subHeight = height / nbrSubViewers - 2 * nbrSubViewers;

        var html = ' \
            <div class="graph-editor"> \
                <div id="' + this.id +'-spinner" class="spinner-border text-dark ge-spinner"></div> \
                <div class="ge-tb"> \
                    <h1 id="' + this.id + '-title"></h1> \
                    <div>\
                        <label>Mesh:</label>\
                        <select>\
                            <option>Grey matter</option>\
                            <option>White matter</option>\
                            <option>Nothing</option>\
                        </select>\
                        <input type="range" id="' + this.id + '-mesh-opacity" size="1" min="0" max="1" step="0.05" value="1">\
                        <label for="' + this.id + '-clip-ax"><i class="icon brain-axial-clip"></i></label>\
                        <input type="range" id="' + this.id + '-clip-ax" size="1" min="-90" max="100" step="1" value="100">\
                        <label for="' + this.id + '-clip-cor"><i class="icon brain-coronal-clip"></i></label>\
                        <input type="range" id="' + this.id + '-clip-cor" size="1" min="-60" max="60" step="1" value="60">\
                        <label for="' + this.id + '-clip-sag"><i class="icon brain-sagital-clip"></i></label>\
                        <input type="range" id="' + this.id + '-clip-sag" size="1" min="-30" max="40" step="1" value="50">\
                        <button class="btn ge-btn btn-light" id="' + this.id + '-cancel">Cancel</button> \
                        <button class="btn ge-btn btn-success" id="' + this.id + '-save">Save</button> \
                        <div class="tooltip">Help ?\
                            <div class="tooltip-content">\
                                <div class="ge-control"><i class="icon left-click"></i> Rotate</div>\
                                <div class="ge-control"><i class="icon right-click"></i> Move</div>\
                                <div class="ge-control"><i class="icon wheel-click"></i> Zoom</div>\
                            </div>\
                        </div>\
                    </div>\
                </div>\
                <div class="ge-graph-editor">\
                    <div id="' + this.id +'-scene" class="ge-scene"></div> \
                    <div id="' + this.id +'-subviewers" class="ge-subviewers">';
                        for(var sv = 0; sv < nbrSubViewers; sv++) {
                            html += '<div class="ge-subviewer" id="' + this.id + '-sv-' + sv + '"></div>';
                        }
                        html += ' \
                    </div>\
                </div> \
                    </div> \
                </div> \
                <div class="ge-footer">\
                    <div class="ge-tb"> \
                        <div class="ge-nomenclature-controls">\
                            <button class="btn ge-btn" id="' + this.id + '-nomenclature-btn" >Nomenclature</button> \
                            <input type="text" id="' + this.id + '-labelSearch" value="" placeholder="Search label..." /> \
                            <button class="btn ge-btn" id="' + this.id + '-set-label" disabled>Apply</button>\
                        </div>\
                        <div class="ge-label-details" id="' + this.id + '-currentLabel"></div>\
                    </div> \
                    <div class="ge-logs">\
                        <div id="' + this.id + '-log" class="ge-log"> </div>\
                    </div>\
                    <ul class="ge-nomenclature" id="' + this.id + '-currentNomenclature" style="display: none">\
                    </ul><div style="clear:both"></div>\
                </div> \
            </div> \
        ';
        this.domElement.innerHTML = html;

        this.nomenclatureDOMElement =  document.getElementById(this.id + '-currentNomenclature');
        this.labelDOMElement = document.getElementById(this.id + '-currentLabel');
        this.setButtonDOMElement = document.getElementById(this.id + '-set-label');
        this.spinnerDOMElement = document.getElementById(this.id + '-spinner');
        this.logDOMElement = document.getElementById(this.id + '-log');
        this.titleDOMElement = document.getElementById(this.id + '-title');
        this.nomenclatureButtonDOMElement = document.getElementById(this.id + '-nomenclature-btn');

        // Setup log
        this.logger = new Logger(this.logDOMElement.id);

        this.api = new APIInterface(this.domElement.getAttribute('data-link'));
        
        // Setup the viewer
        this.viewer = new GraphViewer(this.id + '-scene', width, height, this.api.baseUrl);
        this.viewer.onClickCallBack = this.onClickHandler.bind(this);
        this.viewer.onDoubleClickCallBack = this.onDoubleClickHandler.bind(this);
        this.viewer.onLoadingCompleted = () => {
            this.setCurrentNomenclature(this.viewer.nomenclature); 
            this.setLoadingMode(false);
        }
        this.subViewers = [];
        const w = document.getElementById(this.id +'-subviewers').clientWidth; // / nbrSubViewers;
        var subV;
        for(var sv = 0; sv < nbrSubViewers; sv++) {
            subV = new GraphViewer(this.id + '-sv-' + sv, w, subHeight, this.api.baseUrl);
            subV.onDoubleClickHandler = this.onDoubleClickHandler.bind(this);
            this.subViewers.push(subV);
            this.viewer.addSlave(subV);
        }

        // Setup controls
        var that = this;
        $(document).on('click', '#' + this.id + '-set-label', function () { that.labelize(); });
        $(document).on('click', '#' + this.id + '-save', function () { that.saveLabelings(); });
        $(document).on('click', '#' + this.id + '-cancel', function () { that.cancel(); });
        $(document).on('click', '#' + this.id + '-mesh-opacity', function () { that.viewer.setBrainMeshOpacity($(this)[0].value); });
        $(document).on('click', '#' + this.id + '-clip-ax', function () { that.viewer.setAxialClipping($(this)[0].value); });
        $(document).on('click', '#' + this.id + '-clip-cor', function () { that.viewer.setCoronalClipping($(this)[0].value); });
        $(document).on('click', '#' + this.id + '-clip-sag', function () { that.viewer.setSagitalClipping($(this)[0].value); });
        $(document).on('click', '#' + this.id + '-nomenclature-btn', function () { that.toggleNomenclature(); })
        $(document).on('click', '.ge-btn', function () { if($(this).attr('selected') !== "selected") $(this).setAttr('selected', 'selected'); else $(this).setAttr('selected', ''); })
        document.addEventListener('keydown', this.keydownEvent.bind(this));
    }

    keydownEvent(evt) {
        if(this.mouseIsOver && evt.key == 'l') {
            this.labelize();
        }
    }

    setLoadingMode(val) {
        this.spinnerDOMElement.hidden = !val;
    }

    loadLabelingSet(labelistSetId) {
        this.viewer.loadLabelingSet(labelistSetId);
    }

    saveLabelings() {
        this.setLoadingMode(true);

        var labelings = []
        for(const mesh of this.viewer.viewer.allObjects()) {
            if(mesh.userData.fold) {
                labelings.push(mesh.userData);
            }
        }

        this.api.setGraphLabelings(
            this.viewer.labelingSet.id,
            {
                'labelings': labelings
            },
            labelingSet => {
                this.setLoadingMode(false);
                this.log("The graph has been saved.", LogMessageType.SUCCESS);
            }
        );
    }

    onDoubleClickHandler(objectData) {
        if(objectData.userData.label !== undefined) {
            this.selectedMeshId = objectData.id;
            const data = objectData.userData;
            if (data.label) {
                for(const l of this.currentNomenclature.labels) {
                    if(data.label.id == l.id) {
                        this.setCurrentLabel(l);
                        return;
                    }
                }
            }
        } else {
            this.selectedMeshId = null;
        }
    }
    onClickHandler(objectData) {
        if(objectData.userData.label !== undefined) {
            this.selectedMeshId = objectData.id;
        } else {
            this.selectedMeshId = null;
        }
    }

    setCurrentNomenclature(nomenclature) {
        this.currentNomenclature = nomenclature;
        this.setCurrentLabel(null);

        if(!this.nomenclatureDOMElement)
            return;
        
        if(nomenclature) {
            // Update the nomenclature panel
            var html = '';
            var id;
            for(const label of nomenclature.labels) {
                id = this.id + "-labelselector-" + label.id.toString();
                html += '<li id="' + id + '" style="background-color:' + label.color + '; color:' + checkBackgrounColor(label.color,'black', 'white')+ '"><span class="sulcus-sname">' + label.shortname + '</span>' + (label.fr_name? ' - ' + label.fr_name : '') + '</li>';
            }
            this.nomenclatureDOMElement.innerHTML = html;

            var labelElement;
            for(const label of nomenclature.labels) {
                id = this.id + "-labelselector-" + label.id.toString();
                labelElement = document.getElementById(id);
                labelElement.label = label;
                labelElement.addEventListener("click", function(evt) { this.setCurrentLabel(evt.currentTarget.label); }.bind(this));
            }
            document.getElementById(this.id + '-labelSearch').addEventListener("keyup", function(evt) { this.filterLabels(evt.currentTarget.value); }.bind(this));
        } else {
            this.nomenclatureDOMElement.innerHTML = '<p class="default">No nomenclature</p>';
        }
    }

    setCurrentLabel(label) {
        this.currentLabel = label;

        if(!this.labelDOMElement)
            return;
        if(label) {
            var html = '<div style="background-color:' + label.color + '; color:' + checkBackgrounColor(label.color,'black', 'white') + '">' ;
            /*if(label.parent) {
                var parent = null;
                for(const p of this.currentNomenclature.labels) {
                    if(p.id == label.parent) {
                        parent = p;
                        break;
                    }
                }
                if(parent) {
                    var parent_id = this.id + "-parentLabel-" + label.id.toString();
                    html += '<p>Parent:<a id="' + parent_id + '">Parent:' + parent.shortname + '</a></p>';
                }
            }
            else {
                html += '<p></p>';
            }*/
            html += '<p><span style="font-weight: bold;">' + label.fr_name + '</span> ' + label.shortname + '</p>';
            html += '<p>' + label.en_description + '</p>';
            html += '</div>';
            this.labelDOMElement.innerHTML = html;
            //this.setButtonDOMElement.setAttribute('style', 'background-color: ' + label.color);
            this.setButtonDOMElement.setAttribute('class', 'btn blinking');

            if(parent) {
                var parentElement = document.getElementById(parent_id);
                parentElement.label = parent;
                parentElement.addEventListener("click", function(evt) { this.setCurrentLabel(evt.currentTarget.label); }.bind(this));
            }
        } else {
            this.labelDOMElement.innerHTML = '<p class="default">No selected label</p>';
            this.setButtonDOMElement.setAttribute('class', 'btn');
            this.setButtonDOMElement.setAttribute('disabled', 'disabled');
        }
    }

    toggleNomenclature() {
        console.log("Toggle nomenclature", window.getComputedStyle(this.nomenclatureDOMElement).display);
        if( window.getComputedStyle(this.nomenclatureDOMElement).display == 'none' ) {
            this.showNomenclature();
        } else {
            this.hideNomenclature();
        }
    }
    showNomenclature() {
        this.nomenclatureDOMElement.setAttribute("style", "display: block");
    }
    hideNomenclature() {
        this.nomenclatureDOMElement.setAttribute("style", "display: none");   
    }

    filterLabels(search) {
        this.showNomenclature();
        if(!search || search.length < 1) {
            for(const label of this.currentNomenclature.labels) {
                document.getElementById(this.id + "-labelselector-" + label.id.toString()).style.visibility = "visible";
                document.getElementById(this.id + "-labelselector-" + label.id.toString()).style.display = "block";
            }
        } else {
            for(const label of this.currentNomenclature.labels) {
                if((label.name && label.name.includes(search)) || (label.shortname && (label.shortname.includes(search) || label.shortname.replace('.', '').includes(search))) || (label.description && label.description.includes(search))) {
                    document.getElementById(this.id + "-labelselector-" + label.id.toString()).style.visibility = "visible";
                    document.getElementById(this.id + "-labelselector-" + label.id.toString()).style.display = "block";
                }
                else {
                    document.getElementById(this.id + "-labelselector-" + label.id.toString()).style.visibility  = "collapse";
                    document.getElementById(this.id + "-labelselector-" + label.id.toString()).style.display = "none";
                }
            }
        }
    }

    labelize() {
        if(this.viewer && this.currentLabel && this.selectedMeshId >= 0) {
            const metadata = this.viewer.setLabel(this.selectedMeshId, this.currentLabel, this.currentNomenclature)
            this.log("Fold #" + metadata.fold.id + " has been labelized  with " + metadata.label.shortname);
        } else {
            if(!this.currentLabel) this.log("No active label. Select one before labeling.", LogMessageType.ERROR);
            if(!this.selectedMeshId) this.log("No selected mesh. Select the one you want to labelize.", LogMessageType.ERROR);
        }
    }

    cancel() {
        alert("Not implemented action");
    }

    // log(msg, type=LogMessageType.DEFAULT) {
    //     const timeElapsed = Date.now();
    //     const today = new Date(timeElapsed);
    //     var new_msg = '<div class="ge-message '+ type.className + '">' + today.toUTCString() + ': ' + msg + '</div>';
    //     this.msgDOMElement.innerHTML = new_msg + this.msgDOMElement.innerHTML
    // }

    setTitle(html) {
        this.titleDOMElement.innerHTML = html;
    }
}

export { Editor, APIInterface }