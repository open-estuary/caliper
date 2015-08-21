
$(function () {
    var test = document.getElementById("disk_tst").value;
    var cached_dic = getJson(test, 'Iozone-Cached')
    console.log(cached_dic)
    var columns = getHoriColumn(cached_dic);
    var data = getHoriData(cached_dic, columns);

    // initialize grid
    var options = {emptyRow: true, sortable: false};
    var grid = $(document.getElementById("disk-cached")).grid(data, columns, options);
    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(0);
    console.group("data api examples");
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
