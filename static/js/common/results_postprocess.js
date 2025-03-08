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
function select_checkboxes(selectable_checkboxes) {
    for (var i = 0; i < selectable_checkboxes.length; i++) {
        document.getElementById(selectable_checkboxes[i]).checked = true;
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
    select_checkboxes(selectable_checkboxes);
}
function select_by_TMscore(query_or_reference) {
    select_all_results(false);
    var min_tmscore = document.getElementById("id_min_tmscore").value;
    var max_tmscore = document.getElementById("id_max_tmscore").value;
    if (min_tmscore || max_tmscore) {
        min_tmscore = min_tmscore == '' ? -1 : parseFloat(min_tmscore);
        max_tmscore = max_tmscore == '' ? Infinity : parseFloat(max_tmscore);
    }
    else {
        return;
    }
    if (query_or_reference == 'query') {
        field = 'tmscore_query';
    }
    else if (query_or_reference == 'reference') {
        field = 'tmscore_refn';
    }
    else
    {
        return;
    }
    var search_hits = resultsParts(results, true)[1];
    var selectable_checkboxes = [];
    for (var i = 0; i < search_hits.length; i++) {
        var hit_tmscore = parseFloat(search_hits[i].hit_record.alignment[field])
        if (hit_tmscore > min_tmscore && hit_tmscore < max_tmscore) {
            selectable_checkboxes.push('table_row_checkbox'+i);
            selectable_checkboxes.push('alignment_checkbox'+i);
        }
    }
    select_checkboxes(selectable_checkboxes);
}
function select_by_TMscore_both() {
    select_all_results(false);
    var min_tmscore = document.getElementById("id_min_tmscore").value;
    var max_tmscore = document.getElementById("id_max_tmscore").value;
    if (min_tmscore || max_tmscore) {
        min_tmscore = min_tmscore == '' ? -1 : parseFloat(min_tmscore);
        max_tmscore = max_tmscore == '' ? Infinity : parseFloat(max_tmscore);
    }
    else {
        return;
    }
    var search_hits = resultsParts(results, true)[1];
    var selectable_checkboxes = [];
    for (var i = 0; i < search_hits.length; i++) {
        var hit_tmscore_query = parseFloat(search_hits[i].hit_record.alignment.tmscore_query)
        var hit_tmscore_reference = parseFloat(search_hits[i].hit_record.alignment.tmscore_refn)
        if (hit_tmscore_query > min_tmscore && hit_tmscore_reference > min_tmscore) {
            if (hit_tmscore_query < max_tmscore && hit_tmscore_reference < max_tmscore) {
                selectable_checkboxes.push('table_row_checkbox'+i);
                selectable_checkboxes.push('alignment_checkbox'+i);
            }
        }
    }
    select_checkboxes(selectable_checkboxes);
}
