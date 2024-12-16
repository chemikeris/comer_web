'use sctrict';
function getResultsTableColumns() {
    return ['', 'No.', 'ID', 'TM-score (reference)', 'TM-score (query)', 'RMSD', 'Aligned residues', 'Reference length'];
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
    // TM-score reference
    row.appendChild(createTableData(hit_record.alignment.tmscore_refn));
    // TM-score query
    row.appendChild(createTableData(hit_record.alignment.tmscore_query));
    // RMSD
    row.appendChild(createTableData(hit_record.alignment.rmsd));
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
    alignment_description.innerText = 'TM-score(reference)=' + hit_record.alignment.tmscore_refn;
    alignment_description.innerText += ', TM-score(query)=' + hit_record.alignment.tmscore_query;
    alignment_description.innerText += ', RMSD=' + hit_record.alignment.rmsd;
    alignment_description.innerText += ', Identities=' + percentageDisplay(hit_record.alignment.n_identities, hit_record.alignment.n_aligned);
    alignment_description.innerText += ', Matched=' + percentageDisplay(hit_record.alignment.n_matched, hit_record.alignment.n_aligned);
    alignment_description.innerText += ', Gaps=' + percentageDisplay(hit_record.alignment.n_gaps, hit_record.alignment.n_aligned) + '.';
    alignment_div.appendChild(alignment_description);
}
function formatAlignmentFooter(alignment_div, hit_record) {
    // Rotation-translation matrix should be here.
}

showResults(results);

