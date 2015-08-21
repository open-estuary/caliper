
$(function () {
    var test = document.getElementById("network_tst").value;  
    
    var sum_dic = getJson(test, 'sum')
    var columns = getHoriColumn(sum_dic);
    var data = getHoriData(sum_dic, columns);   

    // initialize grid
    var options = {emptyRow: true, sortable: false};
	var grid = $(document.getElementById("network-summary")).grid(data, columns, options);
    draw_grid(grid);
    
    // api examples
    var $row = grid.getRowByIndex(0);
    console.group("data api examples");
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
