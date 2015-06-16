
$(function () {

    var test = document.getElementById("example_tst").value;  
    var sum_dic = getJson(test, 'summary');
    var columns = getVertColumn(sum_dic);
    var data = getVertData(sum_dic, columns);

    //var sum_dic = getJson(test, 'summary')
    //alert(sum_dic)
    //var targets = {"values": [ "rh2285_v1", "rh2285_v2", "I5 PC","D02"]};
	//
	//var sum_data = [["18465", "1197", "250", "440620", "5139", "6597"],
    //                ["30068", "1981", "216", "413845", "7373", "8297"],
	//				["22141", "365", "185", "89249", "6291", "5175"],
	//				["11697", "274", "218", "96535", "4631", "3947"]]
    //// generate data
	//var data = [];
	//for (var i = 0; i < sum_data.length; ++i) {
	//	data.push({
	//		"platform": targets.values[i],
	//		"CPU": sum_data[i][1],
	//		"algorithm": sum_data[i][0],
	//		"disk": sum_data[i][3],
	//		"latency":sum_data[i][2],
	//		"memory": sum_data[i][4],
	//		"total_score": sum_data[i][5]
	//	});
	//}

    //// define columns
	//var columns = [
	//	{name: "platform", type: "string", editor:"SelectorEditor", editorProps: targets},
    //    {name: "algorithm", type: "string", editor: "TextareaEditor"},
    //    {name: "CPU", type: "string", editor: "TextareaEditor"},
    //    {name: "latency", type: "string", editor: "TextareaEditor"},
    //    {name: "disk", type: "string", editor: "TextareaEditor"},
	//	{name: "memory", type: "string", editor: "TextareaEditor"},
    //    {name: "total_score", type: "string", editor: "TextareaEditor"},
	//];

    // initialize grid
    var options = {emptyRow: true, sortable: false};
	//var grid = $(".sensei-grid:eq(3)").grid(data, columns, options);
	var grid = $(document.getElementById("sum_result_info")).grid(data, columns, options);
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
