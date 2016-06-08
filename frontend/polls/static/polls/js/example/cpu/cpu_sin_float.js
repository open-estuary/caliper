
$(function () {
	var test = document.getElementById("cpu_sincore").value;
    
    var sin_float_dic = getJson(test, 'sincore_float')
    console.log(sin_float_dic)
    var columns = getHoriColumn(sin_float_dic);
    var data = getHoriData(sin_float_dic, columns);
       
    // initialize grid
    var options = {emptyRow: true, sortable: false};
	var grid = $(document.getElementById("sin-float")).grid(data, columns, options);

    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(0);
    console.group("data api examples");
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
