
$(function () {
	var test = document.getElementById("algorithm_tst").value;  
    
    var symm_dic = getJson(test, 'symmetric cyphers');
	var columns = getHoriColumn(symm_dic);
    var data = getHoriData(symm_dic, columns);

    // initialize grid
    var options = {emptyRow: true, sortable: false};
	var grid = $(document.getElementById("alg_symmetric")).grid(data, columns, options);

    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(2);
    console.group("data api examples");
    console.log("grid.getRowDataByIndex(0):", grid.getRowDataByIndex(0));
    console.log("grid.getRowData($row):", grid.getRowData($row));
    console.log("grid.getGridData():", grid.getGridData());
    console.log("symm_dic: ", symm_dic)
    console.groupEnd();

    window.grid = grid;
});
