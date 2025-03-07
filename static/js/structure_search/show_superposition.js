function show_structures(input_url, aligned_url, div) {
    var stage = new NGL.Stage(div);
    stage.loadFile(input_url, {ext: "pdb"}).then(function (o) {o.addRepresentation('cartoon', {color: 'red'}); o.autoView();});
    stage.loadFile(aligned_url, {ext: "pdb"}).then(function (o) {o.addRepresentation('cartoon', {color: 'blue'}); o.autoView();})
}
