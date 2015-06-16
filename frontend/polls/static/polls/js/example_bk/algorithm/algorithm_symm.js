
$(function () {
	
	symmetric_data = [["aes-128 cbc", "openssl", "86747", "141614", "111878", "117347"],
				["aes-128 ige", "openssl", "83762", "136736", "108580", "113196"],
				["aes-192 cbc","openssl", "72465", "118349", "93375", "100935"],
				["aes-192 ige","openssl", "70450", "114806", "91076", "98039"],
				["aes-256 cbc","openssl", "62390", "101787", "80035", "88705"],
				["aes-256 ige","openssl", "60806", "99009", "78186", "86425"],	
				["blowfish cbc","openssl", "81472", "132621", "122021", "70625"],
				["cast cbc","openssl", "72939", "118893", "119585", "76011"],
				["des cbc","openssl", "45765", "74726", "71123", "50182"],
				["des ede3","openssl", "17393", "28420", "27318", "19347"],
				["idea cbc","openssl", "58372", "95076", "80821", "49683"],
				["rc2 cbc","openssl", "28687", "46772", "36955", "29963"],
				["rc4","openssl", "446817", "729107", "605510", "202056"],			
				["seed cbc","openssl", "49792", "81103", "78963", "55459"]]
				
    // generate data
	var data = [];
	for (var i = 0; i < symmetric_data.length; ++i) {
		data.push({
			"test_case": symmetric_data[i][0],
            "tool": symmetric_data[i][1],
            "rh2285-v1": symmetric_data[i][2],
            "rh2285-v2": symmetric_data[i][3],
            "i5_pc": symmetric_data[i][4],
            "d02": symmetric_data[i][5]
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

    var myvar = document.getElementById("myVar").value;
    // api examples
    var $row = grid.getRowByIndex(2);
    console.group("data api examples");
    console.log("grid.getRowDataByIndex(0):", grid.getRowDataByIndex(0));
    console.log("grid.getRowData($row):", grid.getRowData($row));
    console.log("grid.getGridData():", grid.getGridData());
    console.log("myvar:", myvar);
    console.groupEnd();

    window.grid = grid;
});
