
$(function () {
    var test = document.getElementById("example_tst").value;  
    
    var config_dic = getJson(test, 'config');
    var columns = getVertColumn(config_dic);
    console.log("columns", columns);
    var data = getVertData(config_dic, columns);
    console.log("data:", data)

    // initialize grid
    var options = {emptyRow: true, sortable: false};
    //var grid = $(".sensei_grid:eq(0)").grid(data, columns, options)
    var grid = $(document.getElementById("platform_configuration")).grid(data, columns, options)

    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(1);
    console.group("data api examples");
    console.log("grid.getRowDataByIndex(0):", grid.getRowDataByIndex(0));
    //console.log("grid.getRowData($row):", grid.getRowData($row));
    //console.log("grid.getCellDataByIndex(0, 1):", grid.getCellDataByIndex(0, 1));
    //console.log("grid.getCellDataByKey(2, created_at):", grid.getCellDataByKey(2, "created_at"));
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});

