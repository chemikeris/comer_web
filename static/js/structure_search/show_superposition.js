function show_structures(input_url, aligned_url, input_format, aligned_format, div) {
    var stage = new NGL.Stage(div);
    stage.loadFile(input_url, {ext: input_format}).then(function (o) {o.addRepresentation('cartoon', {color: 'red'}); o.autoView();});
    stage.loadFile(aligned_url, {ext: aligned_format}).then(function (o) {o.addRepresentation('cartoon', {color: 'blue'}); o.autoView();})
}
