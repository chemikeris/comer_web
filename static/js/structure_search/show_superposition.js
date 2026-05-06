function show_structures(viewer, input_url, aligned_url, input_format, aligned_format) {
    //viewer.loadStructureFromUrl(input_url, input_format);
    //viewer.loadStructureFromUrl(aligned_url, aligned_format);
    const builder = molstar.lib.extensions.mvs.createBuilder();
    create_MVS_structure_view(builder, input_url, input_format, 'red');
    create_MVS_structure_view(builder, aligned_url, aligned_format, 'blue');
    const mvsData = builder.getState();
    viewer.loadMvsData(mvsData, 'mvsj');
}
function create_MVS_structure_view(builder, structure_url, structure_format, color)
{
    const structure = builder
        .download({ url: structure_url })
        .parse({ format: structure_format })
        .modelStructure({});
    structure
        .component({ selector: 'polymer' })
        .representation({ type: 'cartoon' })
        .color({ color: color });
    structure
        .component({ selector: 'ligand' })
        .representation({ type: 'ball_and_stick' })
        .color({ color: color });
}
