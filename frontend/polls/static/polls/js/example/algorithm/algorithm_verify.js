
$(function () {
    var test = document.getElementById("algorithm_tst").value;  
    
    var verify_dic = getJson(test, 'digital verify');
    var columns = getHoriColumn(verify_dic);
    var data = getHoriData(verify_dic, columns);   
    // initialize grid
    var options = {emptyRow: true, sortable: false};
	var grid = $(document.getElementById("alg_verify")).grid(data, columns, options);

    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(1);
    console.group("data api examples");
    console.log("grid.getRowDataByIndex(0):", grid.getRowDataByIndex(0));
    console.log("grid.getRowData($row):", grid.getRowData($row));
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
