
$(function () {
    var test = document.getElementById("memory_tst").value;  
    var cachebench_dic = getJson(test, 'bandwidth')
    var columns = getHoriColumn(cachebench_dic);
    var data = getHoriData(cachebench_dic, columns);  	

    // initialize grid
    var options = {emptyRow: true, sortable: false};
	var grid = $(document.getElementById("memory-cachebench")).grid(data, columns, options);

    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(0);
    console.group("data api examples");
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
