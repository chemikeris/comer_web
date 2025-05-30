'use strict';
const ALIGNMENT_LENGTH = 80;
function showResults(results) {
    const summary_div = document.getElementById('schematic_sequences');
    const table_div = document.getElementById('results_table');
    const alignments_div = document.getElementById('alignments');

    var program = which_program(results);
    var structure_search = (program == 'gtalign') ? true : false;

    var results_parts = resultsParts(results, structure_search);
    var search_summary = results_parts[0];
    var search_hits = results_parts[1];
    var number_of_hits = search_hits.length

    var results_table = document.createElement('table');
    results_table.classList.add('table');
    results_table.classList.add('table-striped');
    results_table.classList.add('table-sm');
    var results_table_columns = getResultsTableColumns(); // Defined separately for COMER and GTalign
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
        var sequence_summary = formatSummary(search_summary[i].summary_entry, i, structure_search);
        if (structure_search)
        {
            var sort_order = parseInt(results['gtalign_search'].sort_order);
            switch (sort_order) {
                /* GTalign documentation says:
                0: Sort results by the greater TM-score of the two;
                1: Sort by reference length-normalized TM-score;
                2: Sort by query length-normalized TM-score;
                3: Sort by the harmonic mean of the two TM-scores;
                4: Sort by RMSD.
                5: Sort by the greater 2TM-score;
                6: Sort by reference length-normalized 2TM-score;
                7: Sort by query length-normalized 2TM-score.
                8: Sort by the harmonic mean of the 2TM-scores;
                */
                case 0:
                case 4:
                    var coloring_value = Math.max(hit_record.alignment.tmscore_query, hit_record.alignment.tmscore_refn);
                    break;
                case 1:
                    var coloring_value = hit_record.alignment.tmscore_refn;
                    break;
                case 2:
                    var coloring_value = hit_record.alignment.tmscore_query;
                    break;
                case 3:
                    var coloring_value = harmonicMean([hit_record.alignment.tmscore_query, hit_record.alignment.tmscore_refn]);
                    break;
                case 5:
                    var coloring_value = Math.max(hit_record.alignment['2tmscore_query'], hit_record.alignment['2tmscore_refn']);
                    break;
                case 6:
                    var coloring_value = hit_record.alignment['2tmscore_refn'];
                    break;
                case 7:
                    var coloring_value = hit_record.alignment['2tmscore_query'];
                    break;
                case 8:
                    var coloring_value = harmonicMean([hit_record.alignment['2tmscore_query'], hit_record.alignment['2tmscore_refn']]);
                    break;
                default:
                    var coloring_value = hit_record.alignment.tmscore_query;
            }
        }
        else
        {
            var coloring_value = hit_record.alignment.pvalue;
        }
        addStyleForSummary(sequence_summary, hit_record.query_length, hit_record.alignment.query_from, hit_record.alignment.query_to, coloring_value);
        summary_div.appendChild(sequence_summary);

        // Parsing detailed information on search hits and adding info to table and formatting alignments for display.
        var row = document.createElement('tr');
        row.classList.add('results_table_row');
        row.classList.add('results_table_row_part_'+resultsPartNo(i));
        row.classList.add('text-center');

        // 0th column is a checkbox
        row.appendChild(createTableData('<input type="checkbox" id="table_row_checkbox' + i + '" value="' + i + '" name="process" class="table_checkbox form-check-input">'));
        // First column contains a link, thus it is different.
        // No.
        var number_column = createTableData('');
        number_column.appendChild(createLinkToAlignment(i, i+1));
        row.appendChild(number_column);
        // Fill row with data.
        fillSummaryTableRowData(row, hit_record, i);
        // Finished table row.
        results_table_body.appendChild(row);

        // Formatting sequence alignments.
        alignments_div.appendChild(formatAlignment(i, hit_record, structure_search));
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
    var number_of_parts = numberOfParts(number_of_hits);
    summary_div.appendChild(createPaginationNav('summary', number_of_parts));
    showPage('summary', 0);
    table_div.appendChild(createPaginationNav('results_table_row', number_of_parts));
    showPage('results_table_row', 0);
}
function which_program(results) {
    var search_method = Object.keys(results)[0];
    return results[search_method].program;
}
function resultsParts(results, structure_search) {
    var search_method = Object.keys(results)[0];
    var search_summary = results[search_method].search_summary;
    if (structure_search) {
        var search_hits = results[search_method].search_results;
    }
    else {
        var search_hits = results[search_method].search_hits;
    }
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
    else if (description.startsWith('ECOD')) {
        return description.split(' ')[0].split('_').pop();
    }
    else if (description.startsWith('SCOP')) {
        return description.split(' ')[0].split(/_(.*)/s)[1];
    }
    else
    {
        return description.split(' ')[0];
    }
}
function formatSummary(summary, result_no, structure_search) {
    var summary_element = document.createElement('div');
    summary_element.classList.add('summary');
    summary_element.classList.add('summary_part_'+resultsPartNo(result_no));
    var short_description = shortDescription(summary.description);
    if (structure_search) {
        var long_description = 'TM-score(query)=' + summary.tmscore_query + ', TM-score(reference)=' + summary.tmscore_refn + ' ' + summary.description;
    }
    else {
        var long_description = 'Score=' + summary.score + ', E-value=' + summary.evalue + ' ' + summary.description;
    }
    summary_element.title = long_description;
    summary_element.classList.add('sequence_scheme');
    summary_element.appendChild(createLinkToAlignment(result_no, short_description));
    return summary_element;
}
function addStyleForSummary(summary_element, query_length, query_starts, query_ends, coloring_value) {
    // Adding length styling according to query and alignment length.
    var left_margin = Math.round(100 * ((query_starts - 1) / query_length));
    var right_margin = 100 - Math.round(100 * (query_ends / query_length));
    summary_element.style.marginLeft = left_margin + '%';
    summary_element.style.marginRight = right_margin + '%';
    // coloring_value is p for COMER, and TM-score for GTalign
    var color_value = colorSummary(coloring_value);
    summary_element.style.background = 'hsl(' + color_value + ', 100%, 40%)';
}
function createTableHeader(column_names, colspan=null) {
    var table_head = document.createElement('thead');
    table_head.classList.add('align-middle');
    table_head.classList.add('text-center');
    var table_header_row = document.createElement('tr');
    for (var i = 0; i < column_names.length; i++) {
        var td = createTableData(column_names[i]);
        try {
            var cspan = colspan[i];
        }
        catch (TypeError) {
            var cspan = 1;
        }
        td.colSpan = cspan;
        table_header_row.appendChild(td);
    }
    table_head.append(table_header_row);
    return table_head;
}
function createTableData(text) {
    var td = document.createElement('td'); td.innerHTML = text;
    return td;
}
function createTableRow(row_data) {
    var tr = document.createElement('tr');
    for (var i = 0; i < row_data.length; i++ ) {
        tr.appendChild(createTableData(row_data[i]));
    }
    return tr;
}
function createLinkToAlignment(result_no, description) {
    var a = document.createElement('a');
    a.appendChild(document.createTextNode(description));
    a.href = '#alignment_' + result_no;
    return a;
}
function createLink(result_id) {
    var link = '';
    if (result_id.startsWith('PF')) {
        link = createPfamLink(result_id);
    }
    else if (result_id.startsWith('SCOP')) {
        link = createSCOPeLink(result_id, false);
    }
    else if ((result_id[0] == 'd') || (result_id[0] == 'g')) {
        link = createSCOPeLink(result_id, true);
    }
    else if (result_id.startsWith('ECOD')) {
        link = createECODLink(result_id, false);
    }
    else if (result_id.startsWith('e')) {
        link = createECODLink(result_id, true);
    }
    else if (result_id.startsWith('sp|')) {
        link = createUniProtLink(result_id, false);
    }
    else if (result_id.match('[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}'))
    {
        link = createUniProtLink(result_id, true);
    }
    else if (result_id.startsWith('cd') || result_id.startsWith('COG') || result_id.startsWith('KOG')) {
        link = createNCBILink(result_id);
    }
    else {
        link = createRCSBLink(result_id);
    }
    return '<a href="' + link + '">' + result_id + '</a>'
}
function createSCOPeLink(scop_id, raw_id) {
    var scop_domain = raw_id ? scop_id : scop_id.split(/_(.*)/s)[1];
    return 'https://scop.berkeley.edu/sid=' + scop_domain;
}
function createECODLink(ecod_id, raw_id) {
    var ecod_domain = raw_id ? ecod_id : ecod_id.split('_')[2];
    return 'http://prodata.swmed.edu/ecod/complete/domain/' + ecod_domain;
}
function createPfamLink(pfam_id) {
    return 'https://www.ebi.ac.uk/interpro/entry/pfam/' + pfam_id.split('.')[0];
}
function createUniProtLink(swissprot_id, raw_id) {
    var uniprot_ac = raw_id ? swissprot_id : swissprot_id.split('|')[1];
    return 'https://www.uniprot.org/uniprot/' + uniprot_ac;
}
function createNCBILink(cdd_or_cog_uid) {
    return 'https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=' + cdd_or_cog_uid;
}
function createRCSBLink(pdb_chain_id) {
    var pdb_id = pdb_chain_id.substr(0,4)
    return 'https://www.rcsb.org/structure/' + pdb_id;
}
function formatAlignment(result_no, hit_record, structure_search) {
    // Different target description names are used for GTalign and COMER, therefore...
    if (structure_search) {
        var target_from = 'refn_from';
        var target_to = 'refn_to';
        var target_aln = 'refrn_aln';
        var target_secstr = 'refrn_secstr';
    }
    else {
        var target_from = 'target_from';
        var target_to = 'target_to';
        var target_aln = 'target_aln';
        var target_secstr = 'target_secstr';
    }
    var alignment_div = document.createElement('div');
    alignment_div.classList.add('alignment');
    alignment_div.classList.add('alignment_part_'+resultsPartNo(result_no));
    // Alignment header.
    var header = document.createElement('h3');
    header.innerHTML = '<input type="checkbox" id="alignment_checkbox' + result_no + '" class="alignment_checkbox form-check-input h5"> ';
    header.innerHTML += (result_no+1).toString();
    var [short_description, ...other_description] = getTargetDescription(hit_record).split(" ");
    header.innerHTML += ' ';
    header.innerHTML += createLink(short_description);
    header.innerHTML += ' ' + other_description.join(' ');
    if (structure_search) header.innerHTML += ' ';
    header.innerHTML += generateLinkToStructureAlignment(result_no, true);
    header.id = 'alignment_' + result_no;
    alignment_div.appendChild(header);

    formatAlignmentDescription(alignment_div, hit_record);

    // Alignment itself.
    var sequence_alignment_div = document.createElement('div');
    sequence_alignment_div.classList.add('sequence_alignment');

    var spacer_size = 6;
    var prefix_size = 15;
    var spacer = ' '.repeat(spacer_size);
    var query_sec_str_prefix = 'Query_SS'.padEnd(prefix_size, ' ');
    var query_prefix = 'Query'.padEnd(prefix_size, ' ');
    var middle_prefix = ' '.repeat(prefix_size);
    var result_prefix = shortDescription(getTargetDescription(hit_record)).padEnd(prefix_size, ' ');
    var target_sec_str_prefix = (shortDescription(getTargetDescription(hit_record))+'_SS').padEnd(prefix_size, ' ');

    var alignment_str = '';
    var query_starts = hit_record.alignment.query_from;
    var target_starts = hit_record.alignment[target_from];
    var aln_length = getAlignmentLength(hit_record);
    for (var i = 0; i <= aln_length - 1; i += ALIGNMENT_LENGTH) {
        var query_ss = hit_record.alignment.query_secstr.substr(i, ALIGNMENT_LENGTH);
        var aligned_query = hit_record.alignment.query_aln.substr(i, ALIGNMENT_LENGTH);
        var middle = hit_record.alignment.middle.substr(i, ALIGNMENT_LENGTH);
        var aligned_target = hit_record.alignment[target_aln].substr(i, ALIGNMENT_LENGTH);
        var target_ss = hit_record.alignment[target_secstr].substr(i, ALIGNMENT_LENGTH);

        var query_ends = Math.min(hit_record.alignment.query_to, query_starts+ALIGNMENT_LENGTH-1-countGaps(aligned_query));
        var target_ends = Math.min(hit_record.alignment[target_to], target_starts+ALIGNMENT_LENGTH-1-countGaps(aligned_target));

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
    formatAlignmentFooter(alignment_div, hit_record);

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
function percentageDisplay(a, b, sep=' ') {
    var percentage_display = '';
    percentage_display += a + '/' + b;
    percentage_display += sep;
    percentage_display += '(' + Math.round(100 * a / b) + '%)';
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
    for (var i = 1; i < (nav_lis.length-1); i++) {
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
function harmonicMean(arr) {
    var sum = 0; 
    var n = arr.length;
    for (var i = 0; i < n; i++) {
        sum = sum + (1 / arr[i]);
    }
    var hm = n / sum;
    return hm;
}
