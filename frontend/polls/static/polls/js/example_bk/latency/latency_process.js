
$(function () {

	process_data = [["exec proc", "lmbench", "2.06", "1.89", "1.68", "1.67"],
				["fork proc", "lmbench", "6.0", "4.23", "9.62", "4.67"],
				["null IO", "lmbench", "6429", "9083", "2326", "3497"],
				["null call", "lmbench", "15625", "17423", "2762", "5058"],
				["open close", "lmbench", "744", "1145", "560", "545"],
				["sh proc", "lmbench", "0.95", "0.77", "1.12", "0.81"],
				["sig hndl", "lmbench", "1024", "1581", "889", "654"],
				["sig inst", "lmbench", "6761", "11025", "2365", "2902"],
				["slct TCP", "lmbench", "282", "185", "328", "202"],
				["stat", "lmbench", "2453", "3214", "1600", "1538"]]
				
    // generate data
	var data = [];
	for (var i = 0; i < process_data.length; ++i) {
		data.push({
			"test_case": process_data[i][0],
            "tool": process_data[i][1],
            "rh2285-v1": process_data[i][2],
            "rh2285-v2": process_data[i][3],
            "i5_pc": process_data[i][4],
            "d02": process_data[i][5]
		});
	}

    // define columns
	var columns = [
		{name: "test_case", type: "string"},
        {name: "tool", type: "string", editor: "TextareaEditor"},
        {name: "rh2285-v1", type: "string"},
		{name: "rh2285-v2", type: "string"},
        {name: "i5_pc", type: "string", editor: "TextareaEditor"},
        {name: "d02", type: "string", editor: "TextareaEditor"}
	];
	
    // initialize grid
    var options = {emptyRow: true, sortable: false};
	var grid = $(".sensei-grid:eq(3)").grid(data, columns, options);

    // register editors that are bundled with sensei grid
    grid.registerEditor(BasicEditor);
    grid.registerEditor(BooleanEditor);
    grid.registerEditor(TextareaEditor);
    grid.registerEditor(SelectEditor);
    grid.registerEditor(DateEditor);
    //grid.registerEditor(DisabledEditor);

    // example listeners on grid events
    grid.events.on("editor:save", function (data, $cell) {
        console.info("save cell:", data, $cell);
    });
    grid.events.on("editor:load", function (data, $cell) {
        console.info("set value in editor:", data, $cell);
    });
    grid.events.on("cell:select", function ($cell) {
        console.info("active cell:", $cell);
    });
    grid.events.on("cell:clear", function (oldValue, $cell) {
        console.info("clear cell:", oldValue, $cell);
    });
    grid.events.on("cell:deactivate", function ($cell) {
        console.info("cell deactivate:", $cell);
    });
    grid.events.on("row:select", function ($row) {
        console.info("row select:", $row);
    });
    grid.events.on("row:save", function (data, $row, source) {
        console.info("row save:", source, data);
        // save row via ajax or any other way
        // simulate delay caused by ajax and set row as saved
        setTimeout(function () {
            grid.setRowSaved($row);
        }, 1000);
    });

    // render grid
	grid.render();

    // api examples
    var $row = grid.getRowByIndex(1);
    console.group("data api examples");
    console.log("grid.getRowDataByIndex(0):", grid.getRowDataByIndex(0));
    console.log("grid.getRowData($row):", grid.getRowData($row));
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
