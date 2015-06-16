
$(function () {

	memory_data = [["cachebench", "5508", "7132", "6854"],
				["lmbench", "4795", "5550", "3130"]]
				
    // generate data
	var data = [];
	for (var i = 0; i < memory_data.length; ++i) {
		data.push({
            "tool": memory_data[i][0],
            "htsat_server": memory_data[i][1],
            "i5_pc": memory_data[i][2],
            "d02": memory_data[i][3]
		});
	}

    // define columns
	var columns = [
        {name: "tool", type: "string", editor: "TextareaEditor"},
		{name: "htsat_server", type: "string"},
        {name: "i5_pc", type: "string", editor: "TextareaEditor"},
        {name: "d02", type: "string", editor: "TextareaEditor"}
	];
	
    // initialize grid
    var options = {emptyRow: true, sortable: false};
	var grid = $(".sensei-grid:eq(0)").grid(data, columns, options);

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
    var $row = grid.getRowByIndex(3);
    console.group("data api examples");
    console.log("grid.getRowDataByIndex(0):", grid.getRowDataByIndex(0));
    console.log("grid.getRowData($row):", grid.getRowData($row));
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
