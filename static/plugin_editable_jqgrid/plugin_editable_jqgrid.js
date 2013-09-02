
lastSel=''
lookups={}

function create_grid(grid_name,pager,controller_url,col_names,col_models,caption,edit_url){ 
  jQuery(grid_name).jqGrid({
    url:controller_url,
    data: "{}",
    datatype: 'json',
    mtype: 'GET',
    contentType: "application/json; charset=utf-8",
    complete: function(jsondata, stat) {
        if (stat == "success") {
            var thegrid = jQuery(grid_name)[0];
            thegrid.addJSONData(JSON.parse(jsondata.responseText).d);
        }
    },
  
   onSelectRow: function(id){
     if(id && lastSel!='' && id!==lastSel){ 
        jQuery(grid_name).restoreRow(lastSel); 
     }
     lastSel=id;
     jQuery(grid_name).editRow(id, true, '', '', '', '', function(rowid, resultText){reload(grid_name,rowid, resultText);}); 
   },
    colNames:col_names,
    colModel:col_models,
    pager: pager,
    rowNum:10,
    rowList:[10,100,1000],
    sortorder: 'desc',
    multiselect: true,
    multiboxonly:true,
    viewrecords: true,
    editurl:edit_url,
    caption: caption
  });
  jQuery(grid_name).jqGrid('navGrid',pager, {search:true,add:false,edit:false,del:false}); 
  jQuery(grid_name).jqGrid('navButtonAdd',pager,{ caption:"", buttonicon:"ui-icon-plus", onClickButton:function(){addRow(grid_name)}});
  jQuery(grid_name).jqGrid('navButtonAdd',pager,{ caption:"", buttonicon:"ui-icon-trash", onClickButton:function(){deleteRows(grid_name)}});

  jQuery(grid_name).setGridWidth(900,false);
  jQuery(grid_name).setGridHeight(300,false);
}
        

function reload(grid_name,rowid, resultText) {
  result=eval("("+resultText.responseText+")");
  if (result['Id']!=rowid) {
    lastSel=''; 
  }
  jQuery(grid_name).trigger("reloadGrid");
}

function addRow(grid_name){
  if (lastSel=='new') return;
  var datarow = {id:'new',name:'',vat_code:''};
  lastSel='new';
  var su= jQuery(grid_name).jqGrid('addRowData','new', datarow, 'last') ;
  if (su) 
    jQuery(grid_name).editRow('new', true, '', '', '', '', function(rowid, resultText){reload(grid_name,rowid, resultText);});
  }
function deleteRows(grid_name){
  var rowKeys = jQuery(grid_name).getGridParam("selarrrow");

  jQuery(grid_name).delGridRow( rowKeys);
  
}
function get_normal_value(elem) {
    return $(elem).children(0).val();
}

function get_bool_value(elem) {
    return $(elem).attr('checked');
}
function get_bool_widget(value, options) {
    return value.replace('disabled="disabled"','');
}


function calendar_setup_date(id) {
   Calendar.setup({
      inputField:id, ifFormat:"%Y-%m-%d", showsTime:false
   }); 
   
}
function calendar_setup_datetime(id) {
   Calendar.setup({
      inputField:id, ifFormat:"%Y-%m-%d %H:%M:%S", showsTime:true
   }); 
   
}

function integer_setup(integer_element) {
   
   integer_element.onkeyup=function(){this.value=this.value.reverse().replace(/[^0-9\-]|\-(?=.)/g,'').reverse();};
   
}
function time_setup(time_id) {
   jQuery('#'+time_id).clockpick({
       starthour:0, endhour:23, showminutes:true, military:true
    });
   
   
}
function double_setup(integer_element) {
   
   integer_element.onkeyup=function(){this.value=this.value.reverse().replace(/[^0-9\-\.]|[\-](?=.)|[\.](?=[0-9]*[\.])/g,'').reverse();};
   
}
