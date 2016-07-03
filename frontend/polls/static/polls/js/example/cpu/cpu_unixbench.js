
$(function () {
    var test = document.getElementById("cpu_sincore").value;

    var sin_int_dic = getJson(test, 'sincore_unixbench')
    var columns = getHoriColumn(sin_int_dic);
    var data = getHoriData(sin_int_dic, columns);
    console.log(data)
    console.log(sin_int_dic)
    // initialize grid
    var options = {emptyRow: true, sortable: false};
    var grid = $(document.getElementById("sin-unixbench")).grid(data, columns, options);

    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(0);
    console.group("data api examples");
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});