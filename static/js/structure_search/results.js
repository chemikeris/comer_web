'use strict';
function getResultsTableColumns() {
    return ['', 'No.', 'ID', 'TM-score (query)', 'TM-score (reference)', 'RMSD', 'd0 (query)', 'd0 (reference)', '2TM-score (query)', '2TM-score (reference)', 'Aligned residues', 'Query length', 'Reference length', ''];
}
function colorSummary(tm_score) {
    var color_value = 240 / (1 + Math.exp((12 * tm_score - 5)));
    return color_value;
}
function resultDescription(hit_record, button) {
    return hit_record.reference_description;
}
function generateLinkToStructureAlignment(i, button) {
    var href = aligned_structures_link_pattern + '/' + i;
    var a = '<a href="' + href + '" target=_blank ';
    if (button) a += 'class="btn btn-secondary"';
    a += '>Superposition</a>';
    return a;
}
function fillSummaryTableRowData(row, hit_record, i) {
    // ID
    row.appendChild(createTableData(createLink(shortDescription(hit_record.reference_description))));
    // TM-score query
    row.appendChild(createTableData(hit_record.alignment.tmscore_query));
    // TM-score reference
    row.appendChild(createTableData(hit_record.alignment.tmscore_refn));
    // RMSD
    row.appendChild(createTableData(hit_record.alignment.rmsd));
    // d0 query
    row.appendChild(createTableData(hit_record.alignment.d0_query));
    // d0 reference
    row.appendChild(createTableData(hit_record.alignment.d0_refn));
    // 2TM-score query
    row.appendChild(createTableData(hit_record.alignment['2tmscore_query']));
    // 2TM-score reference
    row.appendChild(createTableData(hit_record.alignment['2tmscore_refn']));
    // Aligned residues
    row.appendChild(createTableData(hit_record.alignment.n_aligned - hit_record.alignment.n_gaps));
    // Query length
    row.appendChild(createTableData(hit_record.query_length));
    // Reference length
    row.appendChild(createTableData(hit_record.reference_length));
    // Superposition button.
    var a = generateLinkToStructureAlignment(i, true);
    row.appendChild(createTableData(a));
}
function getTargetDescription(hit_record) {
    return hit_record.reference_description;
}
function getAlignmentLength(hit_record) {
    return hit_record.alignment.n_aligned;
}
function formatAlignmentDescription(alignment_div, hit_record) {
    var alignment_description = document.createElement('table');
    alignment_description.classList.add('table', 'w-auto', 'text-center', 'align-middle', 'alignment_header_table');
    var header = createTableHeader(
        [
            'TM-score\n(query)',
            'TM-score\n(reference)',
            'RMSD',
            'd0\n(query)',
            'd0\n(reference)',
            '2TM-score\n(query)',
            '2TM-score\n(reference)',
            'Length\n(query)',
            'Length\n(reference)',
            'Identities',
            'Matched',
            'Gaps'
        ]
    );
    var table_body = document.createElement('tbody');
    var row = createTableRow(
        [
            hit_record.alignment.tmscore_query,
            hit_record.alignment.tmscore_refn,
            hit_record.alignment.rmsd,
            hit_record.alignment.d0_query,
            hit_record.alignment.d0_refn,
            hit_record.alignment['2tmscore_query'],
            hit_record.alignment['2tmscore_refn'],
            hit_record.query_length,
            hit_record.reference_length,
            percentageDisplay(hit_record.alignment.n_identities, hit_record.alignment.n_aligned, '\n'),
            percentageDisplay(hit_record.alignment.n_matched, hit_record.alignment.n_aligned, '\n'),
            percentageDisplay(hit_record.alignment.n_gaps, hit_record.alignment.n_aligned, '\n')
        ]
    );
    table_body.appendChild(row);
    alignment_description.appendChild(header);
    alignment_description.appendChild(table_body);
    alignment_div.appendChild(alignment_description);
}
function formatAlignmentFooter(alignment_div, hit_record) {
    // Rotation-translation matrix should be here.
    var footer = document.createElement('div');
    var transformation_matrix_table = document.createElement('table')
    transformation_matrix_table.classList.add('table', 'w-auto');
    var tmatrix_header = createTableHeader(['Rotation matrix', 'Translation vector'], [3, 1]);
    var tmatrix_body = document.createElement('tbody');
    var matrix = hit_record.rotation_matrix_rowmajor;
    var vector = hit_record.translation_vector;
    var r1 = createTableRow([matrix[0], matrix[1], matrix[2], vector[0]]);
    tmatrix_body.appendChild(r1);
    var r2 = createTableRow([matrix[3], matrix[4], matrix[5], vector[1]]);
    tmatrix_body.appendChild(r2);
    var r3 = createTableRow([matrix[6], matrix[7], matrix[8], vector[2]]);
    tmatrix_body.appendChild(r3);
    transformation_matrix_table.appendChild(tmatrix_header);
    transformation_matrix_table.appendChild(tmatrix_body);
    footer.appendChild(transformation_matrix_table);
    alignment_div.appendChild(footer);
}

showResults(results);

