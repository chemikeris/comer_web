'use sctrict';
const ALIGNMENT_LENGTH = 80;
function showResults(results) {
    const summary_div = document.getElementById('schematic_sequences');
    const table_div = document.getElementById('results_table');
    const alignments_div = document.getElementById('alignments');

    var results_parts = resultsParts(results);
    var search_summary = results_parts[0];
    var search_hits = results_parts[1];
    var number_of_hits = search_hits.length

    var results_table = document.createElement('table');
    results_table.classList.add('table');
    results_table.classList.add('table-striped');
    results_table.classList.add('table-sm');
    var results_table_columns = ['', 'No.', 'ID', 'Description', 'P-value', 'E-value', 'Score (bits)', 'Length'];
    var results_table_head = createTableHeader(results_table_columns);
    results_table.appendChild(results_table_head);
    var results_table_body = document.createElement('tbody');
    // Creating query sequence schematic view.
    var query_summary_element = document.createElement('div');
    query_summary_element.classList.add('sequence_scheme');
    query_summary_element.style.background = 'grey';
    query_summary_element.innerHTML = '<a>Query</a>';
    summary_div.appendChild(query_summary_element);
    for (var i = 0; i < number_of_hits; i++) {
        var hit_record = search_hits[i].hit_record;
        // Parsing sequence summaries for summary display.
        var sequence_summary = formatSummary(search_summary[i].summary_entry, i);
        addStyleForSummary(sequence_summary, hit_record.query_length, hit_record.alignment.query_from, hit_record.alignment.query_to, hit_record.alignment.pvalue);
        summary_div.appendChild(sequence_summary);

        // Parsing detailed information on search hits and adding info to table and formatting alignments for display.
        var row = document.createElement('tr');
        row.classList.add('results_table_row');
        row.classList.add('results_table_row_part_'+resultsPartNo(i));

        // 0th column is a checkbox
        row.appendChild(createTableData('<input type="checkbox" id="table_row_checkbox' + i + '" value="' + i + '" name="process" class="table_checkbox form-check-input">'));
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
    if (number_of_hits == 0) {
        summary_div.innerHTML += '<p>No hits found.</p>';
        results_table_body.innerHTML = '<td colspan="8">No hits found.</td>';
        alignments_div.innerHTML += '<p>No hits found.</p>';
    }
    results_table.appendChild(results_table_head);
    results_table.appendChild(results_table_body);
    table_div.appendChild(results_table);
    // Creating initial pagination.
    number_of_parts =  numberOfParts(number_of_hits)
    summary_div.appendChild(createPaginationNav('summary', number_of_parts));
    showPage('summary', 0);
    table_div.appendChild(createPaginationNav('results_table_row', number_of_parts));
    showPage('results_table_row', 0);
}
function resultsParts(results) {
    var search_method = Object.keys(results)[0];
    var search_summary = results[search_method].search_summary;
    var search_hits = results[search_method].search_hits;
    return [search_summary, search_hits];
}
function resultsPartNo(result_no) {
    var results_in_page = 25;
    return Math.floor(result_no/results_in_page);
}
function numberOfParts(number_of_hits) {
    var results_in_page = 25;
    if (number_of_hits % results_in_page == 0) {
        return resultsPartNo(number_of_hits);
    }
    else {
        return resultsPartNo(number_of_hits) + 1;
    }
}
function shortDescription(description) {
    if (description.startsWith('sp|'))
    {
        return description.split('|')[1];
    }
    else
    {
        return description.split(' ')[0];
    }
}
function formatSummary(summary, result_no) {
    var summary_element = document.createElement('div');
    summary_element.classList.add('summary');
    summary_element.classList.add('summary_part_'+resultsPartNo(result_no));
    var short_description = shortDescription(summary.description);
    var long_description = 'Score=' + summary.score + ', E-value=' + summary.evalue + ' ' + summary.description;

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
    var td = document.createElement('td'); td.innerHTML = text;
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
    else if (result_id.startsWith('sp|')) {
        link = createUniProtLink(result_id, false);
    }
    else if (result_id.match('[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}'))
    {
        link = createUniProtLink(result_id, true);
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
function createUniProtLink(swissprot_id, raw_id) {
    uniprot_ac = raw_id ? swissprot_id : swissprot_id.split('|')[1];
    return 'https://www.uniprot.org/uniprot/' + uniprot_ac;
}
function createRCSBLink(pdb_chain_id) {
    pdb_id = pdb_chain_id.substr(0,4)
    return 'https://www.rcsb.org/structure/' + pdb_id;
}
function formatAlignment(result_no, hit_record) {
    var alignment_div = document.createElement('div');
    alignment_div.classList.add('alignment');
    alignment_div.classList.add('alignment_part_'+resultsPartNo(result_no));
    // Alignment header.
    var header = document.createElement('h3');
    header.innerHTML = '<input type="checkbox" id="alignment_checkbox' + result_no + '" class="alignment_checkbox form-check-input h5"> ';
    header.innerHTML += (result_no+1).toString();
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
    alignment_description.innerText += 'P-value=' + hit_record.alignment.pvalue + ', ';
    alignment_description.innerText += 'E-value=' + hit_record.alignment.evalue + ', ';
    alignment_description.innerText += 'Score=' + hit_record.alignment.score + '(' + hit_record.alignment.bit_score + ' bits)' + ', ';
    alignment_description.innerText += 'Identities=' + percentageDisplay(hit_record.alignment.n_identities, hit_record.alignment.aln_length) + ', ';
    alignment_description.innerText += 'Positives=' + percentageDisplay(hit_record.alignment.n_positives, hit_record.alignment.aln_length) + ', ';
    alignment_description.innerText += 'Gaps=' + percentageDisplay(hit_record.alignment.n_gaps, hit_record.alignment.aln_length) + '.';
    alignment_div.appendChild(alignment_description);

    // Alignment itself.
    var sequence_alignment_div = document.createElement('div');
    sequence_alignment_div.classList.add('sequence_alignment');

    var spacer_size = 6;
    var prefix_size = 15;
    var spacer = ' '.repeat(spacer_size);
    var query_sec_str_prefix = 'Query_SS'.padEnd(prefix_size, ' ');
    var query_prefix = 'Query'.padEnd(prefix_size, ' ');
    var middle_prefix = ' '.repeat(prefix_size);
    var result_prefix = shortDescription(hit_record.target_description).padEnd(prefix_size, ' ');
    var target_sec_str_prefix = (shortDescription(hit_record.target_description)+'_SS').padEnd(prefix_size, ' ');

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

        if (query_ss) alignment_str += query_sec_str_prefix + spacer + colorSS(query_ss).padEnd(ALIGNMENT_LENGTH, ' ') + '\n';
        alignment_str += query_prefix + query_starts.toString().padEnd(spacer_size, ' ') + colorResidues(aligned_query).padEnd(ALIGNMENT_LENGTH, ' ') + query_ends.toString().padStart(spacer_size, ' ') + '\n';
        alignment_str += middle_prefix + spacer + colorResidues(middle).padEnd(ALIGNMENT_LENGTH, ' ') + '\n';
        alignment_str += result_prefix + target_starts.toString().padEnd(spacer_size, ' ' ) + colorResidues(aligned_target).padEnd(ALIGNMENT_LENGTH, ' ') + target_ends.toString().padStart(spacer_size, ' ') + '\n';
        if (target_ss) alignment_str += target_sec_str_prefix + spacer + colorSS(target_ss).padEnd(ALIGNMENT_LENGTH, ' ') + '\n';
        alignment_str += '\n';

        query_starts = query_ends + 1;
        target_starts = target_ends + 1;
    }
    sequence_alignment_div.innerHTML = alignment_str;

    alignment_div.appendChild(sequence_alignment_div);

    // Footer.
    var footer = document.createElement('div');
    var parameters_table = document.createElement('table');
    parameters_table.classList.add('table', 'w-auto');
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
function colorResidues(sequence) {
    var colored_sequence = '';
    for (var i = 0; i < sequence.length; i++) {
        var residue = sequence[i];
        if (residue == '-' || residue == '+') {
            var colored_residue = residue;
        }
        else {
            var colored_residue = '<span class="res' + residue + '">' + residue + '</span>';
        }
        colored_sequence += colored_residue;
    }
    return colored_sequence;
}
function colorSS(ss) {
    var colored_ss = '';
    for (var i = 0; i < ss.length; i++) {
        if (ss[i] != ' ') {
            colored_ss += '<span class="ss' + ss[i].toUpperCase() + '">' + ss[i] + '</span>'
        }
        else {
            colored_ss += ss[i];
        }
    }
    return colored_ss;
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
function createPaginationNav(element_class, num_pages) {
    var nav = document.createElement('nav');
    var nav_ul = document.createElement('ul');
    nav_ul.classList.add('pagination');
    nav_ul.classList.add('justify-content-center');
    nav_ul.classList.add('flex-wrap');
    nav_ul.id = navId(element_class);
    // Creating Previous link
    nav_ul.innerHTML += '<li class="page-item"><a class="page-link" onclick=navPrevious("'+element_class+'") aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>';
    for (var i = 0; i < num_pages; i++) {
        var nav_li = document.createElement('li');
        nav_li.id = nav_ul.id + '_' + i;
        nav_li.classList.add('page-item');
        var nav_a = document.createElement('a');
        nav_a.classList.add('page-link');
        nav_a.innerHTML = i + 1;
        nav_a.setAttribute('onclick', 'showPage("'+element_class+'",'+i+');');
        nav_li.appendChild(nav_a);
        nav_ul.appendChild(nav_li);
    }
    nav_ul.innerHTML += '<li class="page-item"><a class="page-link" onclick=navNext("'+element_class+'",'+num_pages+') aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>';
    nav.appendChild(nav_ul);
    return nav;
}
function navId(element_class) {
    return 'nav_' + element_class;
}
function showPage(element_class, part_no) {
    var part_to_show = element_class + '_part_' + part_no;
    var all_divs = document.getElementsByClassName(element_class);
    var display_divs = document.getElementsByClassName(part_to_show);
    changeDisplay(all_divs, 'none');
    changeDisplay(display_divs, null);
    // Setting active nav element.
    var nav_ul = document.getElementById(navId(element_class));
    var nav_lis = nav_ul.childNodes;
    for (i = 1; i < (nav_lis.length-1); i++) {
        if (i == (part_no+1)) {
            nav_lis[i].classList.add('active');
        }
        else {
            nav_lis[i].classList.remove('active');
        }
    }
}
function changeDisplay(elements, display) {
    for (var i = 0; i < elements.length; i++) {
        elements[i].style.display = display;
    }
}
function activeLi(element_class) {
    var nav_lis = document.getElementById(navId(element_class)).childNodes;
    for (i = 1; i < (nav_lis.length-1); i++) {
        if (nav_lis[i].classList.contains('active')) {
            return i-1;
        }
    }
}
function navNext(element_class, max_no) {
    var active_li_no = activeLi(element_class);
    if (active_li_no >= (max_no-1)) {
        return;
    }
    else {
        showPage(element_class, active_li_no+1);
    }
}
function navPrevious(element_class) {
    var active_li_no = activeLi(element_class);
    if (active_li_no == 0) {
        return;
    }
    else {
        showPage(element_class, active_li_no-1);
    }
}

showResults(results);

var submit_buttons = document.getElementsByClassName('results_button');
for (var i = 0; i < submit_buttons.length; i++) {
    submit_buttons[i].addEventListener(
        'click',
        function(event) {
            var inputs = document.getElementsByClassName('table_checkbox');
            var num_checked_checkboxes = 0;
            for (var i = 0; i < inputs.length; i++) {
                if (inputs[i].type == 'checkbox') {
                    if (inputs[i].checked) {
                        num_checked_checkboxes += 1;
                    }
                }
            }
            if (num_checked_checkboxes == 0) event.preventDefault();
        }
    );
}
function syncCheckboxes(cb, id1, id2) {
    var other_cb_id = cb.id.replace(id1, id2);
    var other_cb = document.getElementById(other_cb_id);
    other_cb.checked = cb.checked;
}
var table_checkboxes = document.getElementsByClassName('table_checkbox');
for (var i = 0; i < table_checkboxes.length; i++) {
    table_checkboxes[i].addEventListener(
        'change',
        function(event) {syncCheckboxes(this, 'table_row_checkbox', 'alignment_checkbox');}
    )
}
var alignment_checkboxes = document.getElementsByClassName('alignment_checkbox');
for (var i = 0; i < alignment_checkboxes.length; i++) {
    alignment_checkboxes[i].addEventListener(
        'change',
        function(event) {syncCheckboxes(this, 'alignment_checkbox', 'table_row_checkbox');}
    )
}

function select_all_results(on) {
    table_checkboxes = document.getElementsByClassName('table_checkbox');
    for (var i = 0; i < table_checkboxes.length; i++) {
        table_checkboxes[i].checked = on;
        syncCheckboxes(table_checkboxes[i], 'table_row_checkbox', 'alignment_checkbox');
    }
}
function select_by_Evalue() {
    select_all_results(false);
    var min_evalue = document.getElementById("id_min_evalue").value;
    var max_evalue = document.getElementById("id_max_evalue").value;
    if (min_evalue || max_evalue) {
        min_evalue = min_evalue == '' ? -1 : parseFloat(min_evalue);
        max_evalue = max_evalue == '' ? Infinity : parseFloat(max_evalue);
    }
    else {
        return;
    }
    var search_hits = resultsParts(results)[1];
    var selectable_checkboxes = [];
    for (var i = 0; i < search_hits.length; i++) {
        var hit_evalue = parseFloat(search_hits[i].hit_record.alignment.evalue)
        if (hit_evalue > min_evalue && hit_evalue < max_evalue) {
            selectable_checkboxes.push('table_row_checkbox'+i);
            selectable_checkboxes.push('alignment_checkbox'+i);
        }
    }
    for (var i = 0; i < selectable_checkboxes.length; i++) {
        document.getElementById(selectable_checkboxes[i]).checked = true;
    }
}
