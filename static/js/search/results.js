'use sctrict';
function getResultsTableColumns() {
    return ['', 'No.', 'ID', 'Description', 'P-value', 'E-value', 'Score (bit-score)', 'Aln. length'];
}
function colorSummary(p) {
    // Coloring according to p value. Linear scheme is used between log10(p)<-10 (red) and log10(p)>-0.3 (p~0.5) (blue).
    // Different color schemes can be also implemented.
    if (p > 0.1) {
        color_value = 220;
    }
    else if (Math.log10(p) <= -10) {
        color_value = 0;
    }
    else {
        // Using logistic function to have midpoint at p=0.025
        color_value = 220 / (1 + Math.exp(-120 * (p - 0.025)));
    }
    return color_value;
}
function generateLinkToStructureAlignment(i, button) {
    return '';
}
function fillSummaryTableRowData(row, hit_record, unused_i) {
    // ID
    row.appendChild(createTableData(createLink(shortDescription(hit_record.target_description))));
    // Description
    row.appendChild(createTableData(hit_record.target_description));
    // Pvalue
    row.appendChild(createTableData(hit_record.alignment.pvalue));
    // Evalue
    row.appendChild(createTableData(hit_record.alignment.evalue));
    // Score (bits)
    score_for_display = Math.round(hit_record.alignment.score) + ' (' + Math.round(hit_record.alignment.bit_score) + ')';
    row.appendChild(createTableData(score_for_display));
    // Length
    row.appendChild(createTableData(hit_record.alignment.aln_length));
}
function getTargetDescription(hit_record) {
    return hit_record.target_description;
}
function getAlignmentLength(hit_record) {
    return hit_record.alignment.aln_length;
}
function formatAlignmentDescription(alignment_div, hit_record) {
    var alignment_description = document.createElement('p');
    alignment_description.innerText = 'Length/ENO: ';
    alignment_description.innerText += 'Query=' + hit_record.query_length + '/' + hit_record.query_eno.toFixed(1) + ', ';
    alignment_description.innerText += 'Target=' + hit_record.target_length + '/' + hit_record.target_eno.toFixed(1);
    alignment_div.appendChild(alignment_description);

    var alignment_description = document.createElement('p');
    alignment_description.innerText = '';
    alignment_description.innerText += 'P-value=' + hit_record.alignment.pvalue + ', ';
    alignment_description.innerText += 'E-value=' + hit_record.alignment.evalue + ', ';
    alignment_description.innerText += 'Score=' + hit_record.alignment.score + '(' + hit_record.alignment.bit_score + ' bits)' + ', ';
    alignment_description.innerText += 'Identities=' + percentageDisplay(hit_record.alignment.n_identities, hit_record.alignment.aln_length) + ', ';
    alignment_description.innerText += 'Positives=' + percentageDisplay(hit_record.alignment.n_positives, hit_record.alignment.aln_length) + ', ';
    alignment_description.innerText += 'Gaps=' + percentageDisplay(hit_record.alignment.n_gaps, hit_record.alignment.aln_length) + '.';
    alignment_div.appendChild(alignment_description);
}
function formatAlignmentFooter(alignment_div, hit_record) {
    var footer = document.createElement('div');
    var parameters_table = document.createElement('table');
    parameters_table.classList.add('table', 'w-auto');
    var parameters_table_header = createTableHeader(['', 'K', 'Lambda']);
    var parameters_table_tbody = document.createElement('tbody');
    var r1 = createTableRow(['Computed ungapped', hit_record.alignment.computed_K_ungapped.toString(), hit_record.alignment.computed_lambda_ungapped.toString()]);
    parameters_table_tbody.append(r1);
    var r2 = createTableRow(['Estimated gapped', hit_record.alignment.estimated_K_gapped.toString(), hit_record.alignment.estimated_lambda_gapped.toString()]);
    parameters_table_tbody.append(r2);
    // Finished parameters table
    parameters_table.appendChild(parameters_table_header);
    parameters_table.appendChild(parameters_table_tbody);
    footer.appendChild(parameters_table);
    alignment_div.appendChild(footer);
}
showResults(results);
