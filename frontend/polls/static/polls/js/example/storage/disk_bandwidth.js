
$(function () {
    var test = document.getElementById("storage_tst").value;
    
    var band_dic = getJson(test, 'bandwidth');
    var columns = getHoriColumn(band_dic);
    var data = getHoriData(band_dic, columns);

    // initialize grid
    var options = {emptyRow: true, sortable: false};
	var grid = $(".sensei-grid:eq(1)").grid(data, columns, options);

    draw_grid(grid) ;

    // api examples
    var $row = grid.getRowByIndex(0);
    console.group("data api examples");
    console.log("grid.getRowDataByIndex(0):", grid.getRowDataByIndex(0));
    console.log("grid.getRowData($row):", grid.getRowData($row));
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
