
$(function () {
    var test = document.getElementById("cpu_multicore").value;

    var sin_int_dic = getJson(test, 'multicore_misc')
    var columns = getHoriColumn(sin_int_dic);
    var data = getHoriData(sin_int_dic, columns);

    // initialize grid
    var options = {emptyRow: true, sortable: false};
    var grid = $(document.getElementById("multi-misc")).grid(data, columns, options);

    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(0);
    console.group("data api examples");
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});