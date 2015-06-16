
$(function () {
    
    sin_int_data = [["ASSIGNMENT", "nbench", "37", "60", "50", "26"],
				["BITFIELD", "nbench", "4.1", "6.7", "6.7", "2.9"],
				["FP EMULATION", "nbench", "429", "670", "344", "269"],
				["HUFFMAN", "nbench", "3626", "5899", "3144", "2106"],
				["IDEA", "nbench", "8071", "13150", "9007", "7496"],
				["NUMERIC SORT", "nbench", "1323", "2158", "2131", "914"],
				["STRING SORT", "nbench", "713", "1160", "902", "344"],
				["dhry1", "nbench", "18433", "29996", "25387", "20964"],
				["dhry2", "nbench", "13454", "21911", "17715", ""]]
				
    // generate data
	var data = [];
	for (var i = 0; i < sin_int_data.length; ++i) {
		data.push({
			"test_case": sin_int_data[i][0],
            "tool": sin_int_data[i][1],
            "rh2285-v1": sin_int_data[i][2],
            "rh2285-v2": sin_int_data[i][3],
            "i5_pc": sin_int_data[i][4],
            "d02": sin_int_data[i][5]
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
	var grid = $(".sensei-grid:eq(4)").grid(data, columns, options);

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
