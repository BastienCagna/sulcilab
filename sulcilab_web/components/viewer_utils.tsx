import { PColor } from "../api";
import * as THREE from 'three';


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


function getLabel(nomenclature: PNomenclature, labelId: number) {
    let label;
    for(let l = 0; l < nomenclature.labels.length; l++) {
        label = nomenclature.labels[l];
        if(label.id == labelId) {
            return label;
        }
    }
    return null;
}

/*
*   Convert PColor to CSS "rgba(red, green, blue, alpha)"
*/
function strColor(c: PColor){
    return "rgba(" + [c.red, c.green, c.blue, c.alpha].join(', ') + ")";
}

function threeJsColor(color: PColor) {
    return new THREE.Color(color.red/255.0, color.green/255.0, color.blue/255.0);
}

/*
* Return lightColor or darkColor depending on the hexcolor value
*/
function checkBackgrounColor(color: PColor, darkColor: any, lightColor: any){
    var yiq = ((color.red*299)+(color.green*587)+(color.blue*114))/1000;
    // Return new color if to dark, else return the original
    return (yiq < 40) ? lightColor : darkColor;
}

export {computeOffset, getLabel, strColor, threeJsColor, checkBackgrounColor}
