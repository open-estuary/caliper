
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
	var grid = $(document.getElementById("exec_info")).grid(data, columns, options);
    draw_grid(grid)

    // api examples
    var $row = grid.getRowByIndex(1);
    console.group("data api examples");
    console.groupEnd();
});
