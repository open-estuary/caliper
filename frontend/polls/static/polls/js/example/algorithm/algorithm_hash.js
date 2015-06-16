
$(function () {
    var test = document.getElementById("algorithm_tst").value;  
    
    var hash_dic = getJson(test, 'hash algorithm')
    var columns = getHoriColumn(hash_dic);
    var data = getHoriData(hash_dic, columns);

    // initialize grid
    var options = {emptyRow: true, sortable: false};
	var grid = $(".sensei-grid:eq(2)").grid(data, columns, options);

    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(1);
    console.group("data api examples");
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
