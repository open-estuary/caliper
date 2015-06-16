
$(function () {

	hash_data = [["md5", "openssl", "138808", "226631", "236814", "95546"],
				["sha1", "openssl", "161681", "223800", "229189", "159828"],
				["sha256","openssl", "124064", "202290", "160463", "271100"],
				["sha512", "openssl", "144480", "235585", "170585", "100114"]]
    // generate data
	var data = [];
	for (var i = 0; i < hash_data.length; ++i) {
		data.push({
			"test_case": hash_data[i][0],
            "tool": hash_data[i][1],
            "rh2285-v1": hash_data[i][2],
            "rh2285-v2": hash_data[i][3],
            "i5_pc": hash_data[i][4],
            "d02": hash_data[i][5]
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
    var $row = grid.getRowByIndex(1);
    console.group("data api examples");
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});
