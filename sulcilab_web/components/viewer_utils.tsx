import { PColor } from "../api";

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

function strColor(c: PColor){
    return "rgba(" + [c.red, c.green, c.blue, c.alpha].join(', ') + ")";
}

export {computeOffset, getLabel, strColor}
