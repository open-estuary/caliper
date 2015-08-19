
$(function () {
    var test = document.getElementById("disk_tst").value;

    var cached_dic = getJson(test, 'Iozone-Cached')
    var columns = getHoriColumn(cached_dic);
    var data = getHoriData(cached_dic, columns);

    // initialize grid
    var options = {emptyRow: true, sortable: false};
    var grid = $(document.getElementById("disk-cached")).grid(data, columns, options);
    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(5);
    console.group("data api examples");
    console.log("grid.getRowDataByIndex(0):", grid.getRowDataByIndex(0));
    console.log("grid.getRowData($row):", grid.getRowData($row));
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
