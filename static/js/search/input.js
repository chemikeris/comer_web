'use sctrict';
function show_db_fields() {
    use_cother_checkbox = document.getElementById('id_use_cother');
    comer_db_input = document.getElementById('id_comer_db').parentElement;
    cother_db_input = document.getElementById('id_cother_db').parentElement;
    if (use_cother_checkbox.checked)
    {
        comer_db_input.style.display = 'none';
        cother_db_input.style.display = 'revert';
    }
    else
    {
        comer_db_input.style.display = 'revert';
        cother_db_input.style.display = 'none';
    }
}
function add_toggle_databases() {
    use_cother_checkbox = document.getElementById('id_use_cother');
    use_cother_checkbox.addEventListener('click', show_db_fields);
}
function add_example_query() {
    input_field = document.getElementById('id_sequence');
    input_field.value = '>PF11325.10 (84)\nEITGKIIAILPEQSGTSKNGEWKKQEFVLETEEQYPKKICFEFFGDKIDLLNIQVGDEVKVSFDIEGREWNGRWFNSIRAWRIE';
}
function add_example_button() {
    form_element = document.forms[0];
    node_after_button = document.getElementById('id_input_query_file').parentNode;
    button_p_element = document.createElement('p');
    button_p_element.innerHTML = '<button class="btn btn-secondary" onclick="add_example_query()" type="button">Load example</button>';
    form_element.insertBefore(button_p_element, node_after_button);
}
function add_bootstrap_for_form() {
    var labels = document.getElementsByTagName('label');
    add_classes(labels, 'form-label');
    var textareas = document.getElementsByTagName('textarea');
    add_classes(textareas, 'form-control');
    var textareas = document.getElementsByTagName('select');
    add_classes(textareas, 'form-select');
    var other_inputs = document.getElementsByTagName('input');
    add_classes_for_inputs(other_inputs);
}
function add_classes(elements, class_name) {
    for (i = 0; i < elements.length; i++) {
        elements[i].classList.add(class_name);
    }
}
function add_classes_for_inputs(inputs) {
    for (i = 0; i < inputs.length; i++) {
        if (inputs[i].type == 'checkbox') {
            inputs[i].classList.add('form-check-input');
        }
        else if (inputs[i].type == 'submit') {
            continue;
        }
        else {
            inputs[i].classList.add('form-control');
        }
    }
}

