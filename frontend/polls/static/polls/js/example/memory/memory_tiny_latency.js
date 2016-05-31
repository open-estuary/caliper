
$(function () {
    var test = document.getElementById("memory_tst").value;  
    var tiny_dic = getJson(test, 'tiny_latency')
    var columns = getHoriColumn(tiny_dic);
    var data = getHoriData(tiny_dic, columns);  	

    // initialize grid
    var options = {emptyRow: true, sortable: false};
	var grid = $(document.getElementById("memory-tiny-latency")).grid(data, columns, options);

    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(0);
    console.group("data api examples");
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
