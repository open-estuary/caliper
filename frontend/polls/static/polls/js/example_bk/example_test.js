
$(function () {
    var test = document.getElementById("example_tst").value;  
    alert(test)
    
    var config_dic = getJson(test, 'config')
    alert(config_dic)

    // define select editor properties
    var targets = {"values": ["D02", "I5 PC", "RH2285"]};
    var arch = {"values": [ "arm_64", "x86_64", "x86_64", "x86_64"]};
	var test_data = [["D02", "I5 PC", "rh2285-v1", "rh2285-v2"], 
                    ["1", "1", "2", "2"],
                    ["16", "4", "24", "10"],
                    ["16", "4", "96", "40"], 
					["2.1GHZ", "3.2GHz", "2.2GHZ", "3.0GHZ"], 
					["hisi", "Intel(R) Core(TM) i5 650", "Intel(R) Xeon(R) E5-2420 v2", "Intel(R) Xeon(R) E5-2690 v2"],
					["7909", "3754", "96634", "515962"], 
					["Linux 3.19.0-rc4+", "Linux 3.13.0-32-generic", "3.16.0-30-generic", "3.13.0-48-generic"], 
					["Ubuntu-Linux", "Ubuntu-Linux", "Ubuntu-Linux", "Ubuntu-Linux"]]

    // generate data
	var data = [];
	for (var i = 0; i < test_data[0].length; ++i) {
		data.push({
			"platform": test_data[0][i],
            "phy_cores": test_data[1][i],
            "log_cores": test_data[2][i],
            "sum_cores": test_data[3][i],
            "clock": test_data[4][i],
			"cpu_type": test_data[5][i],
            "memory(MB)": test_data[6][i],
			"cache": "TBD",
			"arch": arch.values[i],
            "kernel": test_data[7][i],
			"os_distrib": test_data[8][i]
		});
	}

    // define columns
	var columns = [
		{name: "platform", type: "string", editor: "SelectEditor", editorProps: targets}, 
        {name: "phy_cores", type: "int"},
        {name: "log_cores", type: "int"},
        {name: "sum_cores", type: "int"},
        {name: "clock", type: "string", editor: "TextareaEditor"},
		{name: "cpu_type", type: "string", editor: "TextareaEditor"},
        {name: "memory(MB)", type: "string", editor: "TextareaEditor"},
		{name: "cache", type: "string", editor:"TextareaEditor"},
		{name: "arch", type: "string", editor:"SelectEditor", editorProps: arch},
		{name: "kernel", type: "string", editor:"TextareaEditor"},
		{name: "os_distrib", type: "string", editor:"TextareaEditor"}
	];

    // initialize grid
    var options = {emptyRow: true, sortable: false};
    //var grid = $(".sensei_grid:eq(0)").grid(data, columns, options)
    var grid = $(document.getElementById("platform_configuration")).grid(data, columns, options)

    draw_grid(grid);

    // api examples
    var $row = grid.getRowByIndex(1);
    console.group("data api examples");
    console.log("grid.getRowDataByIndex(0):", grid.getRowDataByIndex(0));
    //console.log("grid.getRowData($row):", grid.getRowData($row));
    //console.log("grid.getCellDataByIndex(0, 1):", grid.getCellDataByIndex(0, 1));
    //console.log("grid.getCellDataByKey(2, created_at):", grid.getCellDataByKey(2, "created_at"));
    console.log("grid.getGridData():", grid.getGridData());
    console.groupEnd();

    window.grid = grid;
});

