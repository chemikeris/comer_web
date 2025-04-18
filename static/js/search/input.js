function show_cother_fields() {
    use_cother_checkbox = document.getElementById('id_use_cother');
    comer_db_input = document.getElementById('id_comer_db').parentElement;
    cother_db_input = document.getElementById('id_cother_db').parentElement;
    cother_specific_options = document.getElementById('cother_specific_advanced_options');
    if (use_cother_checkbox.checked)
    {
        comer_db_input.style.display = 'none';
        cother_db_input.style.display = 'revert';
        cother_specific_options.style.display = 'flex';
    }
    else
    {
        comer_db_input.style.display = 'revert';
        cother_db_input.style.display = 'none';
        cother_specific_options.style.display = 'none';
    }
}
function add_toggle_databases() {
    use_cother_checkbox = document.getElementById('id_use_cother');
    use_cother_checkbox.addEventListener('click', show_cother_fields);
}
function add_example_query1() {
    input_field = document.getElementById('id_sequence');
    input_field.value = '>PF11325.10 (84)\nEITGKIIAILPEQSGTSKNGEWKKQEFVLETEEQYPKKICFEFFGDKIDLLNIQVGDEVKVSFDIEGREWNGRWFNSIRAWRIE';
}
function add_example_query2() {
    input_field = document.getElementById('id_sequence');
    input_field.value = example_data;
}
function add_example_button() {
    form_element = document.forms[0];
    node_after_button = document.getElementById('query_file_input');
    button_p_element = document.createElement('p');
    button_p_element.innerHTML += '<button class="btn btn-secondary me-2 mt-2" onclick="add_example_query1()" type="button">Sequence example</button>';
    button_p_element.innerHTML += '<button class="btn btn-secondary mt-2" onclick="add_example_query2()" type="button">Multiple queries example</button>';
    form_element.insertBefore(button_p_element, node_after_button);
}
