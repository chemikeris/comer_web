function show_structure(url, div) {
    var stage = new NGL.Stage(div);
    stage.loadFile(url, {ext: "pdb", defaultRepresentation: true});
}

