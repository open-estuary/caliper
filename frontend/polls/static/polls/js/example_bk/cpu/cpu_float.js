
$(function () {

    float_data = [["float_add", "lmbench", "735", "1204", "1149", "420"],
				["float_bogomflops", "lmbench", "11", "507", "246", "262"],
				["float_div", "lmbench", "166", "272", "242", "116"],
				["float_mul", "lmbench", "440", "719", "862", "349"],
				["linpack_sp", "lmbench", "1486529", "2907266", "1926234", "1041267"],
				["scimark", "lmbench", "342", "559", "402", "101"]]
				
    // generate data
	var data = [];
	for (var i = 0; i < float_data.length; ++i) {
		data.push({
			"test_case": float_data[i][0],
            "tool": float_data[i][1],
            "rh2285-v1": float_data[i][2],
            "rh2285-v2": float_data[i][3],
            "i5_pc": float_data[i][4],
            "d02": float_data[i][5]
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
	var grid = $(".sensei-grid:eq(2)").grid(data, columns, options);

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
    var $row = grid.getRowByIndex(5);
    console.group("data api examples");
    console.log("grid.getRowDataByIndex(0):", grid.getRowDataByIndex(0));
    console.log("grid.getRowData($row):", grid.getRowData($row));
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
