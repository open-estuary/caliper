
$(function () {
    var test = document.getElementById("cpu_multicore").value;

    var openblas_value_dic = getJson(test, 'openblas_value_4_cores')
    var columns = getHoriColumn(openblas_value_dic);
    var data = getHoriData(openblas_value_dic, columns);

    // initialize grid
    var options = {emptyRow: true, sortable: false};
    var grid = $(document.getElementById("cpu_multicore_openblas_value_4_cores")).grid(data, columns, options);

    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(0);
    console.group("data api examples");
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
