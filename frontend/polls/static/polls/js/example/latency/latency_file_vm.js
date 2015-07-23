
$(function () {
    var test = document.getElementById("latency_tst").value;  
    
    var file_vm_dic = getJson(test, 'file/vm');
    var columns = getHoriColumn(file_vm_dic);
    console.log("columns:", columns)
    var data = getHoriData(file_vm_dic, columns);

    // initialize grid
    var options = {emptyRow: true, sortable: false};
	var grid = $(document.getElementById("lat-file-vm")).grid(data, columns, options);
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
