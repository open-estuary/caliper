
$(function () {
    var test = document.getElementById("application_tst").value;

    var nginx_dic = getJson(test, 'nginx_32_core_local_wrps')
    var columns = getHoriColumn(nginx_dic);
    var data = getHoriData(nginx_dic, columns);

    // initialize grid
    var options = {emptyRow: true, sortable: false};
    var grid = $(document.getElementById("application_nginx_32_core_local_wrps")).grid(data, columns, options);

    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(1);
    console.group("data api examples");
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});

