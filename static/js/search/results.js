'use sctrict';
const ALIGNMENT_LENGTH = 80;
function showResults(results) {
    const summary_div = document.getElementById('schematic_sequences');
    const table_div = document.getElementById('results_table');
    const alignments_div = document.getElementById('alignments');

    var search_summary = results.comer_search.search_summary;
    var search_hits = results.comer_search.search_hits;
    
    var results_table = document.createElement('table');
    var results_table_columns = ['No.', 'ID', 'Description', 'Pvalue', 'Evalue', 'Score (bits)', 'Length'];
    var results_table_head = createTableHeader(results_table_columns);
    results_table.appendChild(results_table_head);
    var results_table_body = document.createElement('tbody');
    // Creating query sequence schematic view.
    var query_summary_element = document.createElement('div');
    query_summary_element.classList.add('sequence_scheme');
    query_summary_element.style.background = 'grey';
    query_summary_element.innerHTML = '<a>Query</a>';
    summary_div.appendChild(query_summary_element);
    for (var i = 0; i < search_hits.length; i++) {
        var hit_record = search_hits[i].hit_record;
        // Parsing sequence summaries for summary display.
        var sequence_summary = formatSummary(search_summary[i].summary_entry, i);
        addStyleForSummary(sequence_summary, hit_record.query_length, hit_record.alignment.query_from, hit_record.alignment.query_to, hit_record.alignment.pvalue);
        summary_div.appendChild(sequence_summary);
    
        // Parsing detailed information on search hits and adding info to table and formatting alignments for display.
        var row = document.createElement('tr');

        // First column contains a link, thus it is different.
        // No.
        var number_column = createTableData('');
        number_column.appendChild(createLinkToAlignment(i, i+1));
        row.appendChild(number_column);
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
        // Finished table row.
        results_table_body.appendChild(row);

        // Formatting sequence alignments.
        alignments_div.appendChild(formatAlignment(i, hit_record));
    }
    results_table.appendChild(results_table_head);
    results_table.appendChild(results_table_body);
    table_div.appendChild(results_table);
}
function shortDescription(description) {
    return description.split(' ')[0];
}
function formatSummary(summary, result_no) {
    var summary_element = document.createElement('div');
    var short_description = shortDescription(summary.description);
    var long_description = 'Score=' + summary.score + ', Evalue=' + summary.evalue + ' ' + summary.description;

    summary_element.title = long_description;
    summary_element.classList.add('sequence_scheme');
    summary_element.appendChild(createLinkToAlignment(result_no, short_description));
    return summary_element;
}
function addStyleForSummary(summary_element, query_length, query_starts, query_ends, p) {
    // Adding length styling according to query and alignment length.
    var left_margin = Math.round(100 * ((query_starts - 1) / query_length));
    var right_margin = 100 - Math.round(100 * (query_ends / query_length));
    summary_element.style.marginLeft = left_margin + '%';
    summary_element.style.marginRight = right_margin + '%';
    // Coloring according to p value. Linear scheme is used between log10(p)<-10 (red) and log10(p)>-0.3 (p~0.5) (blue).
    // Different color schemes can be also implemented.
    log_p = Math.log10(p)
    if (log_p <= -10) {
        color_value = 0;
    }
    else if (log_p > -0.3)
    {
        color_value = 250;
    }
    else
    {
        color_value = (26 * log_p) + 260;
    }
    console.log(p, log_p, color_value);
    summary_element.style.background = 'hsl(' + color_value + ', 100%, 40%)';
}
function createTableHeader(column_names) {
    var table_head = document.createElement('thead');
    var table_header_row = document.createElement('tr');
    for (var i = 0; i < column_names.length; i++) {
        table_header_row.appendChild(createTableData(column_names[i]));
    }
    table_head.append(table_header_row);
    return table_head;
}
function createTableData(text) {
    var td = document.createElement('td');
    td.innerHTML = text;
    return td;
}
function createLinkToAlignment(result_no, description) {
    var a = document.createElement('a');
    a.appendChild(document.createTextNode(description));
    a.href = '#alignment_' + result_no;
    return a;
}
function createLink(result_id) {
    if (result_id.startsWith('PF')) {
        link = createPfamLink(result_id);
    }
    else if ((result_id[0] == 'd') || (result_id[0] == 'g')) {
        link = createSCOPeLink(result_id);
    }
    else {
        link = createRCSBLink(result_id);
    }
    return '<a href="' + link + '">' + result_id + '</a>'
}
function createSCOPeLink(scop_id) {
    return 'https://scop.berkeley.edu/sid=' + scop_id;
}
function createPfamLink(pfam_id) {
    return 'https://pfam.xfam.org/family/' + pfam_id;
}
function createRCSBLink(pdb_chain_id) {
    pdb_id = pdb_chain_id.substr(0,4)
    return 'https://www.rcsb.org/structure/' + pdb_id;
}
function formatAlignment(result_no, hit_record) {
    var alignment_div = document.createElement('div');
    // Alignment header.
    var header = document.createElement('h3');
    header.innerHTML = (result_no+1).toString();
    var [short_description, ...other_description] = hit_record.target_description.split(" ");
    header.innerHTML += ' ';
    header.innerHTML += createLink(short_description);
    header.innerHTML += ' ' + other_description.join(' ');
    header.id = 'alignment_' + result_no;
    alignment_div.appendChild(header);

    var alignment_description = document.createElement('p');
    alignment_description.innerText = 'Length/ENO: ';
    alignment_description.innerText += 'Query=' + hit_record.query_length + '/' + hit_record.query_eno.toFixed(1) + ', ';
    alignment_description.innerText += 'Target=' + hit_record.target_length + '/' + hit_record.target_eno.toFixed(1);
    alignment_div.appendChild(alignment_description);

    var alignment_description = document.createElement('p');
    alignment_description.innerText = '';
    alignment_description.innerText += 'Pvalue=' + hit_record.alignment.pvalue + ', ';
    alignment_description.innerText += 'Evalue=' + hit_record.alignment.evalue + ', ';
    alignment_description.innerText += 'Score=' + hit_record.alignment.score + '(' + hit_record.alignment.bit_score + ' bits)' + ', ';
    alignment_description.innerText += 'Identities=' + percentageDisplay(hit_record.alignment.n_identities, hit_record.alignment.aln_length) + ', ';
    alignment_description.innerText += 'Positives=' + percentageDisplay(hit_record.alignment.n_positives, hit_record.alignment.aln_length) + ', ';
    alignment_description.innerText += 'Gaps=' + percentageDisplay(hit_record.alignment.n_gaps, hit_record.alignment.aln_length) + '.';
    alignment_div.appendChild(alignment_description);

    // Alignment itself.
    var sequence_alignment_div = document.createElement('div');
    sequence_alignment_div.classList.add('sequence_alignment');

    var spacer = ' '.repeat(10);
    var query_sec_str_prefix = 'Query_SS'.padEnd(10, ' ');
    var query_prefix = 'Query'.padEnd(10, ' ');
    var middle_prefix = spacer;
    var result_prefix = shortDescription(hit_record.target_description).padEnd(10, ' ');
    var target_sec_str_prefix = 'Target_SS'.padEnd(10, ' ');

    var alignment_str = '';
    var query_starts = hit_record.alignment.query_from;
    var target_starts = hit_record.alignment.target_from;
    for (var i = 0; i <= hit_record.alignment.aln_length; i += ALIGNMENT_LENGTH) {
        var query_ss = hit_record.alignment.query_secstr.substr(i, ALIGNMENT_LENGTH);
        var aligned_query = hit_record.alignment.query_aln.substr(i, ALIGNMENT_LENGTH);
        var middle = hit_record.alignment.middle.substr(i, ALIGNMENT_LENGTH);
        var aligned_target = hit_record.alignment.target_aln.substr(i, ALIGNMENT_LENGTH);
        var target_ss = hit_record.alignment.target_secstr.substr(i, ALIGNMENT_LENGTH);

        query_ends = Math.min(hit_record.alignment.query_to, query_starts+ALIGNMENT_LENGTH-1-countGaps(aligned_query));
        target_ends = Math.min(hit_record.alignment.target_to, target_starts+ALIGNMENT_LENGTH-1-countGaps(aligned_target));

        alignment_str += query_sec_str_prefix + spacer + query_ss.padEnd(ALIGNMENT_LENGTH, ' ') + '\n';
        alignment_str += query_prefix + query_starts.toString().padEnd(10, ' ') + aligned_query.padEnd(ALIGNMENT_LENGTH, ' ') + query_ends.toString().padStart(10, ' ') + '\n';
        alignment_str += middle_prefix + spacer + middle.padEnd(ALIGNMENT_LENGTH, ' ') + '\n';
        alignment_str += result_prefix + target_starts.toString().padEnd(10, ' ' ) + aligned_target.padEnd(ALIGNMENT_LENGTH, ' ') + target_ends.toString().padStart(10, ' ') + '\n';
        alignment_str += target_sec_str_prefix + spacer + target_ss.padEnd(ALIGNMENT_LENGTH, ' ') + '\n';
        alignment_str += '\n';

        query_starts = query_ends + 1;
        target_starts = target_ends + 1;
    }
    sequence_alignment_div.innerText = alignment_str;

    alignment_div.appendChild(sequence_alignment_div);

    // Footer.
    var footer = document.createElement('div');
    footer.classList.add('f');
    var parameters_table = document.createElement('table');
    var parameters_table_header = createTableHeader(['', 'K', 'Lambda']);
    var parameters_table_tbody = document.createElement('tbody');
    var r1 = document.createElement('tr');
    r1.appendChild(createTableData('Computed ungapped'));
    r1.appendChild(createTableData(hit_record.alignment.computed_K_ungapped.toString()));
    r1.appendChild(createTableData(hit_record.alignment.computed_lambda_ungapped.toString()));
    parameters_table_tbody.append(r1);
    var r2 = document.createElement('tr');
    r2.appendChild(createTableData('Estimated gapped'));
    r2.appendChild(createTableData(hit_record.alignment.estimated_K_gapped.toString()));
    r2.appendChild(createTableData(hit_record.alignment.estimated_lambda_gapped.toString()));
    parameters_table_tbody.append(r2);
    // Finished parameters table
    parameters_table.appendChild(parameters_table_header);
    parameters_table.appendChild(parameters_table_tbody);
    footer.appendChild(parameters_table);
    alignment_div.appendChild(footer);

    return alignment_div;
}
function percentageDisplay(a, b) {
    percentage_display = '';
    percentage_display += a + '/' + b;
    percentage_display += ' (' + Math.round(100 * a / b) + '%)';
    return percentage_display;
}
function countGaps(sequence) {
    return sequence.length - sequence.replace(/-/g, '').length;
}

showResults(results);

