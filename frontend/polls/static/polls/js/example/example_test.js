
$(function () {
    var test = document.getElementById("example_tst").value;
    var config_dic = getJson(test, 'config');
    var columns = getVertColumn(config_dic);
    var data = getVertData(config_dic, columns);

    // initialize grid
    var options = {emptyRow: true, sortable: false};
    var grid = $(document.getElementById("platform_configuration")).grid(data, columns, options)

    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(0);
    //console.group("data api examples");
    console.groupEnd();
    window.grid = grid;
});

