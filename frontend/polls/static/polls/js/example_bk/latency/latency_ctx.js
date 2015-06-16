
$(function () {
	
	ctx_data = [["16p/16K ctxsw", "lmbench", "227", "100", "156", "336"],
				["16p/64K ctxsw", "lmbench", "209", "57", "97", "308"],	
				["2p/0K ctxsw", "lmbench", "272", "236", "409", "546"],
				["2p/16K ctxsw", "lmbench", "270", "181", "195", "	480"],
				["2p/64K ctxsw", "lmbench", "260", "135", "163", "456"],
				["8p/16K ctxsw", "lmbench", "253", "118", "95", "278"],
				["8p/64K ctxsw", "lmbench", "236", "71", "99", "373"]]
				
    // generate data
	var data = [];
	for (var i = 0; i < ctx_data.length; ++i) {
		data.push({
			"test_case": ctx_data[i][0],
            "tool": ctx_data[i][1],
            "rh2285-v1": ctx_data[i][2],
            "rh2285-v2": ctx_data[i][3],
            "i5_pc": ctx_data[i][4],
            "d02": ctx_data[i][5]
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
	var grid = $(".sensei-grid:eq(1)").grid(data, columns, options);

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
