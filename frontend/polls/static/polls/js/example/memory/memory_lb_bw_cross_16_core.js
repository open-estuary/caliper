
$(function () {
    var test = document.getElementById("memory_tst").value;  
    
    var bandwidth_dic = getJson(test, 'lb_bw_cross_16_core')
    var columns = getHoriColumn(bandwidth_dic);
    var data = getHoriData(bandwidth_dic, columns);

    // initialize grid
    var options = {emptyRow: true, sortable: false};
	var grid = $(document.getElementById("memory_lb_bw_cross_16_core")).grid(data, columns, options);
    draw_grid(grid);
    
    // api examples
    var $row = grid.getRowByIndex(0);
    console.group("data api examples");
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
