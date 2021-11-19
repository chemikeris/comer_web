'use sctrict';
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
    input_field.value = '>PF11325.10 (84)\nEITGKIIAILPEQSGTSKNGEWKKQEFVLETEEQYPKKICFEFFGDKIDLLNIQVGDEVKVSFDIEGREWNGRWFNSIRAWRIE';
    input_field.value += '\n//\n';
    var alignment_parts = [
        '>T0991',
        'AYKLIKMAGGNSAI-QTYAREDKTTQTLSTQKTISVLRNGSTSTRIIKVHINSTAPVTINTCDPTKCGPTVPMGVSFKSSMPEDADPAEVLKAAKAALALFE-ANLNSAFNKNVDEISVA',
        '>MGYP001152841429',
        'AYKLIKMAGGNSAT-QTYAREDKTTQTLSTQKTIAVLRNGSTSTRIIKVHINSTAPVTINTCDPTKCGPTVPMGVSFKSSMPEGANSAEILKAAKAALALFE-ANLNSAFNKNVDEITVA',
        '>MGYP001124449466',
        '-----KVAGNSSAPqQVFMRKDNTNFVLTVSHKMVEAKTPKQAARIIKTTIDVRTVVDLATCDPNACPPKFPALVKLEYSAPEGQLPADLLAAVLAANTAFT-SSSNSVFFPQIETVTVA',
        '>MGYP001070764390',
        '----------------SYVNTKDYGFRLNVDHKVVNVDNRGTPTTVVKCEFDVRRMVDGKACG-TSCPSRFPALIKFTISAPLETDISENVKIAAHMLNLYTrGGIPSPFIANDDEITVA',
    ];
    input_field.value += alignment_parts.join('\n');
}
function add_example_button() {
    form_element = document.forms[0];
    node_after_button = document.getElementById('query_file_input');
    button_p_element = document.createElement('p');
    button_p_element.innerHTML += '<button class="btn btn-secondary me-2 mt-2" onclick="add_example_query1()" type="button">Load single query example</button>';
    button_p_element.innerHTML += '<button class="btn btn-secondary mt-2" onclick="add_example_query2()" type="button">Load multiple queries example</button>';
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
    show_errorlists_in_hidden_fields(['sequence_search_options', 'advanced_options']);
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
function show_errorlists_in_hidden_fields(fieldnames) {
    for (var i = 0; i < fieldnames.length; i++) {
        var field = document.getElementById(fieldnames[i]);
        var errors = field.getElementsByClassName('errorlist')
        if (errors.length > 0) {
            field.classList.add('show');
        }
    }
}
