    
function getJson(test, key){
    var dic = JSON.parse(test);
    for (var item in dic){
        if (item==key){
            var jValue=dic[item];
            return jValue
        }
    }
    return undefined
};

function pushData2Array(data, key, json){
    var value = json[key];
    if ( typeof(value) == "string" ){
        data.push({
            name: key, type: "string"
        });
    }
    else if ( typeof(value) == "number" ){
        data.push({
            name: key, type: "string"
        });
    }
    else{
        data.push({
            name: key, type: "string"
        });
    }
    return data
};

function getVertColumn(json){
    var is={
        types: ["Array", "Boolean", "Date", "Number", "Object", "String"]
    };
    
    var columns = [];
    columns.push({name: "platform", type: "string"});
    for (var key in json) {
        var jValue = json[key];

        for( var key in jValue){
            if (key == "hostname")
                continue;
            columns = pushData2Array(columns, key, jValue);
        }
        return columns;
    }
};

function getVertData(json, columns){
    data = [];
    for (var key in json){
        var each_row = json[key];
        platform = key;
        for (var key in each_row){
            if ('hostname' == key)
                delete each_row.hostname;
        }
        each_row['platform'] = platform;
        data.push( each_row );
    }
    return data;
};

function getHoriColumn(json){
    var columns = [];
    columns.push({name: "test_case", type: "string"});
    for (var key in json){
        columns = pushData2Array(columns, key, json);
    }
    return columns;
};

function getHoriData(json, columns){
    data = [];
    keys = [];
    for (var key in json){
        tmp_dic = json[key];
        for (var key in tmp_dic)
            keys.push(key);
        break;
    }
    for (var element in keys){
        tmp_json = {};
        tmp_json['test_case'] = keys[element];
        test_key = keys[element];
        for (var key in json){
            tmp_json[key] = json[key][test_key];
        }
        data.push(tmp_json);
    }
    return data
}

function draw_grid(grid){
    // register editors that are bundled with sensei grid
    //grid.registerEditor(BasicEditor);
    //grid.registerEditor(BooleanEditor);
    //grid.registerEditor(TextareaEditor);
    //grid.registerEditor(SelectEditor);
    //grid.registerEditor(DateEditor);
    //grid.registerEditor(DisabledEditor);

    // example listeners on grid events
    //grid.events.on("editor:save", function (data, $cell) {
    //    console.info("save cell:", data, $cell);
    //});
    //grid.events.on("editor:load", function (data, $cell) {
    //    console.info("set value in editor:", data, $cell);
    //});
    //grid.events.on("cell:select", function ($cell) {
    //    console.info("active cell:", $cell);
    //});
    //grid.events.on("cell:clear", function (oldValue, $cell) {
    //    console.info("clear cell:", oldValue, $cell);
    //});
    //grid.events.on("cell:deactivate", function ($cell) {
    //    console.info("cell deactivate:", $cell);
    //});
    //grid.events.on("row:select", function ($row) {
    //    console.info("row select:", $row);
    //});
    //grid.events.on("row:save", function (data, $row, source) {
    //    console.info("row save:", source, data);
    //    // save row via ajax or any other way
    //    // simulate delay caused by ajax and set row as saved
    //    setTimeout(function () {
    //        grid.setRowSaved($row);
    //    }, 1000);
    //});

    // render grid
	grid.render();
}
