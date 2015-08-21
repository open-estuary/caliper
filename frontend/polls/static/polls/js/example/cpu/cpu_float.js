
$(function () {
	var test = document.getElementById("cpu_tst").value;  
    
    var float_dic = getJson(test, 'multicore_float')
    var columns = getHoriColumn(float_dic);
    var data = getHoriData(float_dic, columns);

    // initialize grid
    var options = {emptyRow: true, sortable: false};
	var grid = $(document.getElementById("multi-float")).grid(data, columns, options);

    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(0);
    console.group("data api examples");
    console.log("grid.getRowDataByIndex(0):", grid.getRowDataByIndex(0));
    console.log("grid.getRowData($row):", grid.getRowData($row));
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
