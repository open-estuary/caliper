
$(function () {
    var test = document.getElementById("memory_tst").value;  
    
    var cachebench_dic = getJson(test, 'bandwidth')
    var columns = getHoriColumn(cachebench_dic);
    var data = getHoriData(cachebench_dic, columns);  	

    // initialize grid
    var options = {emptyRow: true, sortable: false};
	var grid = $(".sensei-grid:eq(2)").grid(data, columns, options);

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
