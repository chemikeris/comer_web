'use sctrict';
function getResultsTableColumns() {
    return ['', 'No.'];
}
function colorSummary(tm_score) {
    return '42'
}
function resultDescription(hit_record) {
    return hit_record.reference_description;
}
function fillSummaryTableRowData(row, hit_record) {

}
function getTargetDescription(hit_record) {
    return hit_record.reference_description;
}
function getAlignmentLength(hit_record) {
    return hit_record.alignment.n_aligned;
}
function formatAlignmentDescription(alignment_div, hit_record) {

}
function formatAlignmentFooter(alignment_div, hit_record) {

}

showResults(results);

