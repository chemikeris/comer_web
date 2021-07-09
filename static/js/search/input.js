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
