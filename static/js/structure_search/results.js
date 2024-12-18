'use sctrict';
function getResultsTableColumns() {
    return ['', 'No.', 'ID', 'TM-score (query)', 'TM-score (reference)', 'RMSD', 'd0 (query)', 'd0 (reference)', '2TM-score (query)', '2TM-score (reference)', 'Aligned residues', 'Reference length'];
}
function colorSummary(tm_score) {
    return '42'
}
function resultDescription(hit_record) {
    return hit_record.reference_description;
}
function fillSummaryTableRowData(row, hit_record) {
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
    // Reference lengtha
    row.appendChild(createTableData(hit_record.reference_length));
}
function getTargetDescription(hit_record) {
    return hit_record.reference_description;
}
function getAlignmentLength(hit_record) {
    return hit_record.alignment.n_aligned;
}
function formatAlignmentDescription(alignment_div, hit_record) {
    var alignment_description = document.createElement('p');
    alignment_description.innerText = 'TM-score(query)=' + hit_record.alignment.tmscore_query;
    alignment_description.innerText += ', TM-score(reference)=' + hit_record.alignment.tmscore_refn;
    alignment_description.innerText += ', RMSD=' + hit_record.alignment.rmsd;
    alignment_description.innerText += ', Identities=' + percentageDisplay(hit_record.alignment.n_identities, hit_record.alignment.n_aligned);
    alignment_description.innerText += ', Matched=' + percentageDisplay(hit_record.alignment.n_matched, hit_record.alignment.n_aligned);
    alignment_description.innerText += ', Gaps=' + percentageDisplay(hit_record.alignment.n_gaps, hit_record.alignment.n_aligned) + '.';
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

