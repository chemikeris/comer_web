'use strict';
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
    for (var i = 0; i < elements.length; i++) {
        elements[i].classList.add(class_name);
    }
}
function add_classes_for_inputs(inputs) {
    for (var i = 0; i < inputs.length; i++) {
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
        if (field) {
            var errors = field.getElementsByClassName('errorlist')
        }
        else {
            errors = [];
        }
        if (errors.length > 0) {
            field.classList.add('show');
        }
    }
}
