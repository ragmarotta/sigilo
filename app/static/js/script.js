document.addEventListener('DOMContentLoaded', function() {
    // Inicializa o Sidenav
    var sidenav_elems = document.querySelectorAll('.sidenav');
    M.Sidenav.init(sidenav_elems);

    // Inicializa as abas
    var tabs_elems = document.querySelectorAll('.tabs');
    M.Tabs.init(tabs_elems);

    // Inicializa os selects
    var select_elems = document.querySelectorAll('select');
    M.FormSelect.init(select_elems);
});
