
$(function () {

    // define select editor properties
    var focus = {"values": ["Performance", "Functional"]};
	tools_data = [["cachebench", "Performance", "1.9", "23/05/2008"],
				["coremark  ", "Performance", "1.01", ""],
				["dhrystone", "Performance", "1.0", "26/09/2010"],
				["iozone", "Performance", "3.430", ""],
				["iperf", "Performance", "2.0.0", ""],
				["linpack", "Performance", "1.0", "26/09/2012"],
				["lmbench", "Performance", "3-alpha 1", ""],
				["memtester", "Functional", "4.3.0", "9/06/2012"],
				["nbench", "Performance", "", "11/12/1997"],
				["openssl", "Performance", "1.0.2", "22/01/2015"],
				["rttest", "Performance", "0.89-1", "30/03/2014"],
				["scimark", "Performance", "2.0", ""]]

    // generate data
	var data = [];
	for (var i = 0; i < tools_data.length; ++i) {
		data.push({
			"SL_No": i + 1,
            "toolname": tools_data[i][0],
            "tool_focus": tools_data[i][1],
            "version": tools_data[i][2],
            "Release_date": tools_data[i][3]
		});}

    // define columns
	var columns = [
		{name: "SL_No", type: "int"},
        {name: "toolname", type: "string", editor: "TextareaEditor"},
        {name: "tool_focus", type: "string", editor: "SelectEditor", editorProps: focus},
		{name: "version", type: "string", editor: "TextareaEditor"},
        {name: "Release_date", type: "string", editor: "DateEditor"}
	];

    // initialize grid
    var options = {emptyRow: true, sortable: false};
	//var grid = $(".sensei-grid:eq(1)").grid(data, columns, options);
	var grid = $(document.getElementById("tools_info")).grid(data, columns, options);
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
