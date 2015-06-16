
$(function () {

	exec_data = [["101", "12", "12", "0", "11", "0", "11", "1"],
				["85.7", "12", "12", "0	", "11", "0","11", "1"],
				["80.7", "12", "12", "0", "11", "0", "11", "1"],
                ["76.2", "12", "12", "0", "11", "0", "11", "1"]]

    // define select editor properties
    var targets = {"values": ["D02", "I5 PC", "rh2285_v1", "rh2285_v2"]};
    
    // generate data
	var data = [];
	for (var i = 0; i < exec_data.length; ++i) {
		data.push({
			"platforms": targets.values[i],
            "totaltime(min)": exec_data[i][0],
			"tools_selected": exec_data[i][1],
            "build_pass": exec_data[i][2],
            "build_fail": exec_data[i][3],
            "total_exec_num": exec_data[i][4],
            "exec_pass": exec_data[i][5],
            "exec_fail": exec_data[i][6],
            "exec_partial": exec_data[i][7]
		});}

    // define columns
	var columns = [
		{name: "platforms", type: "string", editor:"SelectEditor", editorProps: targets},
        {name: "totaltime(min)", type: "string", editor: "TextareaEditor"},
		{name: "tools_selected", type: "int"},
        {name: "build_pass", type: "int"},
        {name: "build_fail", type: "int"},
        {name: "total_exec_num", type: "int"},
        {name: "exec_pass", type: "int"},
        {name: "exec_fail", type: "int"},
		{name: "exec_partial", type: "int"}
	];

    // initialize grid
    var options = {emptyRow: true, sortable: false};
	//var grid = $(".sensei-grid:eq(2)").grid(data, columns, options);
	var grid = $(document.getElementById("exec_info")).grid(data, columns, options);
    draw_grid(grid)
    //// register editors that are bundled with sensei grid
    //grid.registerEditor(BasicEditor);
    //grid.registerEditor(BooleanEditor);
    //grid.registerEditor(TextareaEditor);
    //grid.registerEditor(SelectEditor);
    //grid.registerEditor(DateEditor);
    ////grid.registerEditor(DisabledEditor);

    //// example listeners on grid events
    //grid.events.on("editor:save", function (data, $cell) {
    //    console.info("save cell:", data, $cell);
    //});
    //grid.events.on("editor:load", function (data, $cell) {
    //    console.info("set value in editor:", data, $cell);
    //});
    //grid.events.on("cell:select", function ($cell) {
    //    console.info("active cell:", $cell);
    //});
    //grid.events.on("cell:clear", function (oldValue, $cell) {
    //    console.info("clear cell:", oldValue, $cell);
    //});
    //grid.events.on("cell:deactivate", function ($cell) {
    //    console.info("cell deactivate:", $cell);
    //});
    //grid.events.on("row:select", function ($row) {
    //    console.info("row select:", $row);
    //});
    //grid.events.on("row:save", function (data, $row, source) {
    //    console.info("row save:", source, data);
    //    // save row via ajax or any other way
    //    // simulate delay caused by ajax and set row as saved
    //    setTimeout(function () {
    //        grid.setRowSaved($row);
    //    }, 1000);
    //});

    //// render grid
	//grid.render();

    // api examples
    var $row = grid.getRowByIndex(1);
    console.group("data api examples");
    //console.log("grid.getRowDataByIndex(0):", grid.getRowDataByIndex(0));
    //console.log("grid.getRowData($row):", grid.getRowData($row));
    //console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    //window.grid = grid;
});
