
$(function () {

	memory_data = [["AF Unix", "lmbench", "6972", "10004", "9901", "2724"],
					["Bcopy(hand)", "lmbench", "4698", "6370", "3714", "3246"],
					["Bcopy(libc)", "lmbench", "2657", "3269", "4869", "3008"],
					["File reread", "lmbench", "3839", "4383", "4651", "2272"],
					["Mem read", "lmbench", "8409", "12021", "6204", "3955"],
					["Mem write", "lmbench", "6255", "8594", "6389", "6572"],
					["Mmap reread", "lmbench", "6965", "9058", "8033", "3774"],
					["Pipe", "lmbench", "3113", "3869", "4187", "2235"],
					["TCP", "lmbench", "3517", "3277", "4500", "2174"]]
				
    // generate data
	var data = [];
	for (var i = 0; i < memory_data.length; ++i) {
		data.push({
			"test_case": memory_data[i][0],
            "tool": memory_data[i][1],
            "rh2285-v1": memory_data[i][2],
            "rh2285-v2": memory_data[i][3],
            "i5_pc": memory_data[i][4],
            "d02": memory_data[i][5]
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
	cachebench_data = [["cachebench_read", "cachebench", "1865", "2622", "3195"],
				["cachebench_rmw", "cachebench", "10974", "16193", "13689"],
				["cachebench_write", "cachebench", "8162", "8542", "7359"]]

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
    var $row = grid.getRowByIndex(5);
    console.group("data api examples");
    console.log("grid.getRowDataByIndex(0):", grid.getRowDataByIndex(0));
    console.log("grid.getRowData($row):", grid.getRowData($row));
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
