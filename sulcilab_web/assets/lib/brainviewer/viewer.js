//import * as THREE from './threejs.js';
//import * as THREE from 'https://cdn.skypack.dev/pin/three@v0.135.0-pjGUcRG9Xt70OdXl97VF/mode=imports,min/optimized/three.js';
import * as THREE from 'https://cdn.skypack.dev/three@v0.135.0';
import { OrbitControls } from 'https://cdn.skypack.dev/three@v0.135.0/examples/jsm/controls/OrbitControls.js';
import { EffectComposer } from 'https://cdn.skypack.dev/three@v0.135.0/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'https://cdn.skypack.dev/three@v0.135.0/examples/jsm/postprocessing/RenderPass';
import { OutlinePass } from 'https://cdn.skypack.dev/three@v0.135.0/examples/jsm/postprocessing/OutlinePass';
import { ShaderPass } from 'https://cdn.skypack.dev/three@v0.135.0/examples/jsm/postprocessing/ShaderPass';
import { FXAAShader } from 'https://cdn.skypack.dev/three@v0.135.0/examples/jsm/shaders/FXAAShader';
// import { listChildren } from './utils.js';


export const PointOfView = { 
    "FrontToBack": [120, 40, 0],
    "LeftToRight": [10, 0, 60],
    "RightToLeft": [10, 0, -60]
};

export class Viewer {
    mouse = new THREE.Vector2();
    // Animation
    camRotationSpeed = 0.;
    angle = 0.;
    animate;
    objects = [];
    slaves = [];

    onClickCallBack = null;
    onDoubleClickCallBack = null;
    onFrameCallBack = null;

    clickDownX = null;
    clickDownY = null;

    /**
     * Init a 3D view.
     * Create a toolbar containing a 3DViewWidget and a 3DObjectWidget to manage the rendering of objects.
     * Then, create the ThreeJS scene with lights, camera, control, helper and renderer
     * @param parent
     * @param title
     * @param width
     * @param height
     */
    constructor(parent, domElementId, width, height) {
        this.parent = parent;
        this.type = "3D";
        this.width = width;
        this.height = height;
        this.domElement = document.getElementById(domElementId);
        this.domElement.classList.add("viewer");
        this.domElement.innerHTML = '<div id="' + domElementId + '-vlegend" class="viewer-legend"></div>';
        this.legendDomElement = document.getElementById(domElementId + '-vlegend');
        this.legendDomElement.hidden = true;

        // ThreeJS Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color("#141414");//"#333333");//0x48494a);// 0xf0f0f0 );
        this.camera = new THREE.PerspectiveCamera(75, this.width / this.height, 0.1, 1000);
        this.raycaster = new THREE.Raycaster();

        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(this.width, this.height);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.BasicShadowMap;
        this.renderer.physicallyCorrectLights = true;
        this.renderer.localClippingEnabled = true;

        // Generate HTML elements
        this.domElement.appendChild(this.renderer.domElement);

        this.offset = new THREE.Vector3(0, 0, 0);
        this.resetCamera();

        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.minDistance = 50;
        this.controls.maxDistance = 400;
        /*
                this.controls = new TrackballControls(this.camera, this.renderer.domElement);
                this.controls.rotateSpeed = 2.0;
                this.controls.addEventListener('change', this.cameraWidget.onCameraChange);
        */
        this.scene.add(new THREE.AmbientLight(0xffffff, 2));
        const sun = new THREE.DirectionalLight(0xffffff, 1,5);
        sun.position.set(0, 1000, 0);
        sun.castShadow = true;
        this.scene.add(sun);
        const moon = new THREE.DirectionalLight(0xffffff, 0.75);
        moon.position.set(0, -1000, 0);
        this.scene.add(moon);

        this.origin = new THREE.AxesHelper(1000);
        this.origin.name = "Origin";

        this.grid = new THREE.PolarGridHelper(200, 12, 8, 64, 0x808080);
        this.grid.name = "Grid";
        this.grid.position.y = - 100;
        this.grid.position.x = - 0;
        this.objects.push(this.grid);
        //this.scene.add(this.grid);

        // Edge highlighter
        // ref: https://github.com/mrdoob/three.js/blob/master/examples/webgl_postprocessing_outline.html
        this.composer = new EffectComposer(this.renderer);
        const renderPass = new RenderPass(this.scene, this.camera);
        this.composer.addPass(renderPass);
        const boundaries = new THREE.Vector2(this.width, this.height);
        this.outlinePass = new OutlinePass(boundaries, this.scene, this.camera);
        this.outlinePass.visibleEdgeColor.set(new THREE.Color(0xffffff));
        this.outlinePass.hiddenEdgeColor.set(new THREE.Color(0x404040));
        this.outlinePass.usePatternTexture = false;
        this.outlinePass.edgeThickness = 1;
        this.outlinePass.edgeGlow = 1;
        this.outlinePass.edgeStrength = 2;
        this.outlinePass.pulsePeriod = 4;
        this.composer.addPass(this.outlinePass);
        const effectFXAA = new ShaderPass(FXAAShader);
        effectFXAA.uniforms['resolution'].value.set(1 / this.width, 1 / this.height);
        this.composer.addPass(effectFXAA);

        const animate = function () {
            // Render with a fps of 60, and stop when changing browser tab
            if (this.camRotationSpeed != 0) {
                /*this.angle += this.camRotationSpeed * 0.01;
                this.camera.position.x = this.lastStaticCamPosition.x * Math.cos(this.angle);
                this.camera.position.z = this.lastStaticCamPosition.z * Math.sin(this.angle);*/
                const pos = this.camera.position;
                this.camera.position.x = pos.x * Math.cos(this.camRotationSpeed) + pos.z * Math.sin(this.camRotationSpeed);
                this.camera.position.z = pos.z * Math.cos(this.camRotationSpeed) - pos.x * Math.sin(this.camRotationSpeed);
                //this.camera.lookAt(0, 0, 0);
            }
            requestAnimationFrame(animate);
            this.controls.update();
            //this.renderer.render(this.scene, this.camera);
            this.composer.render();
            if (this.onFrameCallBack) { this.onFrameCallBack(); }
        }.bind(this);
        animate();
        this.animate = animate;

        //this.renderer.domElement.addEventListener(`click`, (evt) => this.onClickOnObject(evt));
        this.renderer.domElement.addEventListener('mousedown', (evt) => {this.clickDownX = evt.pageX; this.clickDownY = evt.pageY;});
        this.renderer.domElement.addEventListener('mouseup', (evt) => {
            //console.log("event", this.onDoubleClickCallBack);
            if(this.clickDownTime && Date.now() - this.clickDownTime < 400){
                if(this.onDoubleClickCallBack) this.onDoubleClickOnObject(evt);
                return
            } 
            this.clickDownTime = Date.now();
            const diffX = Math.abs(evt.pageX - this.clickDownX);
            const diffY = Math.abs(evt.pageY - this.clickDownY);
            if (diffX < 6 && diffY < 6) {
                this.onClickOnObject(evt);
            }
        });
        document.addEventListener('keydown', this.onKeyDown.bind(this));
        window.addEventListener( 'resize', this.onWindowResize.bind(this), false );
        this.controls.addEventListener('change', this.onPositionChange.bind(this));
    }

    addSlave(slave) {
        this.slaves.push(slave);
        // slave.controls = this.controls;
        // slave.camera = this.camera;
        // console.log("setting master controls and camera to slave")
    }

    addMesh(vertices, triangles, metadata = null, color = 0xaaaaaa, selectable = true, transparent = true) {
        var offset = this.offset.toArray();
        var flat_vertices = [];
        for (var v = 0; v < vertices.length; v++) {
            for (var i = 0; i < 3; i++) {
                flat_vertices.push(vertices[v][i] - (offset[i]/3));
            }
        }

        var flatTri = [];
        for (var v = 0; v < triangles.length; v++) {
            for (var i = 0; i < 3; i++) {
                flatTri.push(triangles[v][i]);
            }
        }
        vertices = new THREE.Float32BufferAttribute(flat_vertices, 3);
        const geometry = new THREE.BufferGeometry();
        geometry.setIndex(Array.from(flatTri));
        geometry.setAttribute('position', vertices);
        geometry.computeVertexNormals();
        // geometry.computeMorphNormals();
        // geometry.computeFaceNormals();
        geometry.computeBoundingSphere();

        //const material = new THREE.MeshLambertMaterial({
        const material = new THREE.MeshPhongMaterial({ 
        //const material = new THREE.MeshToonMaterial({ 
            opacity: 1,
            shininess: 30,
            transparent: transparent,
            color: color,
            side: THREE.DoubleSide,
            blending: THREE.NormalBlending,
            shadowSide: THREE.DoubleSide,
        });
        //const material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        if (metadata) {
            mesh.userData = metadata;
            if (metadata.name)
                mesh.name = metadata.name;
        }

        mesh.rotateZ(3.14 / 2);
        mesh.rotateY(-3.14 / 2);

        mesh.selectable = selectable;
        this.scene.add(mesh);
        return mesh;
    }

    setLegend(legend) {
        this.legendDomElement.innerHTML = legend;
        if(this.legendDomElement.innerHTML) {
            this.legendDomElement.hidden = false;
        } else {
            this.legendDomElement.hidden = true;
        }
    }

    // allObjects() {
    //     return listChildren(this.scene).slice(1);
    // }
    getObjectById(id) {
        return this.scene.getObjectById(id);
    }
    setOffset(x, y, z) {
        var oldOffset = this.offset;
        this.offset = new THREE.Vector3(x, y, z);
        var translation = this.offset.sub(oldOffset);
        var children = this.allObjects();
        for(var c=0; c<children.length; c++) {
            children[c].position.add(translation);
        }
    }
    resetCamera() {
        // this.setCameraPosition(120, 40, 0);
        this.setCameraPosition(10, 0, 60);
    }
    setCameraPosition(x, y, z) {
        this.camera.position.x = x;
        this.camera.position.y = y;
        this.camera.position.z = z;
        this.camera.lookAt(0, 0, 0);
    }
    setCameraPointOfView(ptw) {
        this.setCameraPosition(ptw[0], ptw[1], ptw[2]);
    }

    onWindowResize() {
        this.camera.aspect = this.width / this.height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.width, this.height);
        this.composer.setSize(this.width, this.height);
    }


    intersectingObjects(event) {
        var rect = this.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX-rect.left) / this.width) * 2 - 1;
        this.mouse.y = -((event.clientY-rect.top) / this.height) * 2 + 1;

        this.raycaster.setFromCamera(this.mouse, this.camera);
        let intersects = this.raycaster.intersectObjects(this.scene.children, true);

        if (intersects.length > 0) {
            for (let i = 0; i < intersects.length; i++) {
                if (intersects[i].object.visible && intersects[i].object.selectable !== undefined && intersects[i].object.selectable) {
                    const object = intersects[i].object;
                    this.outlinePass.selectedObjects = [object];
                    return object;
                }
            }
        }
    }
    /**
     * Manage click in the 3D scene.
     * @param event
     */
    onClickOnObject(event) {
        event.preventDefault();
        const obj = this.intersectingObjects(event);
        if (this.onClickCallBack) this.onClickCallBack(obj);
    }

    onDoubleClickOnObject(event) {
        event.preventDefault();
        const obj = this.intersectingObjects(event);
        if (this.onDoubleClickCallBack) this.onDoubleClickCallBack(obj);
    }

    onKeyDown(event) {
        let obj;
        switch (event.key) {
            case 'ArrowLeft':
            case 'ArrowRight':
            case 'ArrowUp':
            case 'ArrowDown':
                break;
            case 'r':
                if (this.camRotationSpeed) this.rotate(false);
                else this.rotate(true);
                break;

            case 'g':
                obj = this.scene.getObjectByName("Grid");
                if (obj) this.removeObjectByName("Grid");
                else {
                    this.scene.add(this.grid);
                    this.objects.push(this.grid);
                    this.objectWidget.update();
                }
                break;

            case 'o':
                obj = this.scene.getObjectByName("Origin");
                if (obj) this.removeObjectByName("Origin");
                else {
                    this.scene.add(this.origin);
                    this.objects.push(this.origin);
                    this.objectWidget.update();
                }
                break;
        }
    }

    // https://stackoverflow.com/questions/58705286/how-programmatically-focus-a-mesh-in-three-js-on-click-on-a-button
    fitCameraTo(boundingBox) {
        const camera = this.camera;
        const objPosition = boundingBox.getCenter(new THREE.Vector3());
        const objSize = boundingBox.getSize(new THREE.Vector3());
        boundingBox.min.y = 0;
        boundingBox.max.y = 0;
        const boundingSphere = boundingBox.getBoundingSphere(new THREE.Sphere());

        let dim = boundingSphere.radius * 2;
        if (dim < camera.near) {
            dim = camera.near;
        }

        const direction = THREE.Object3D.DefaultUp.clone(); // view direction

        // object angular size
        const fov = THREE.Math.degToRad(camera.fov);

        let distance = dim / (2.0 * Math.tan(fov / 2.0));

        if (camera.aspect <= 1) {
            distance = distance / camera.aspect;            
        }

        if (distance < camera.near) {
            distance = objSize.y;
        }

        if (distance < camera.near) {
            distance = camera.near;
        }

        camera.position.copy(objPosition.clone().add(direction.multiplyScalar(distance)));
        camera.lookAt(objPosition);
        camera.updateProjectionMatrix();
    }

    onPositionChange(o) {
        if(this.slaves.length) {
            for(let s=0; s < this.slaves.length; s++) {
                this.slaves[s].camera.copy(this.camera);
                this.slaves[s].controls.target = this.controls.target;
                this.slaves[s].controls.update();
            }

        }
    }
}