from gluon.storage import Storage
class plugin_editable_jqgrid_Description(object):
    def __init__(self,table_name,field_name):
        self.table_name=table_name
        self.field_name=field_name
    def description(self):
        try:
            description=self.__getattribute__(self.table_name)[self.field_name]
        except:
            description="Error"
        return description
    

    
from gluon.html import XmlComponent
class plugin_editable_jqgrid(XmlComponent):
    
    text="""
        <script type="text/javascript">
             jQuery(document).ready(function(){
                 create_grid("#%(grid_name)s",'#pager-%(grid_name)s','%(url)s',%(col_names)s,%(col_models)s,'%(caption)s','%(edit_url)s');
             }); 
             
             new_lookups=%(lookups)s;
             for(key in new_lookups)
                lookups[key]=new_lookups[key];
        </script>
        
        <table id="%(grid_name)s"></table> 
        <div id="pager-%(grid_name)s"></div>
        """
    @staticmethod
    def set_description_column(table,field_name):
        table.virtualfields.append(plugin_editable_jqgrid_Description(table._tablename,field_name))
        
    def get_custom_element_function(self,field):
        from gluon.sqlhtml import OptionsWidget
        if OptionsWidget.has_options(field):
            widget=SQLFORM.widgets.options.widget(field,'no_selection').xml()
            script= """
                 function (value, options) {
                       var el = document.createElement('div');
                       el.innerHTML='%s'.replace('>'+value+'<',' selected="selected">'+value+'<');
                       el.children[0].style.width="100%%";
                       return el;
                 }""" % widget;
            return script;
        elif field.type=='boolean':
            return "get_bool_widget"
        else:        
            if field.type=='time':
                calendar="el.children[0].onfocus=function(){time_setup(this.attributes['id'].value);};"
            elif field.type=='date':
                calendar="el.children[0].onfocus=function(){calendar_setup_date(this.attributes['id'].value);};"
            elif field.type=='datetime':
                calendar="el.children[0].onfocus=function(){calendar_setup_datetime(this.attributes['id'].value);};"
            elif field.type=='double':
                calendar="el.children[0].onfocus=function(){double_setup(this);};"
            elif field.type=='integer':
                calendar="el.children[0].onfocus=function(){integer_setup(this);};"
            else:
                calendar=""
            if field.widget:
                widget=field.widget(field,'a_value').xml().replace('<','\<').replace('>','\>').replace("'","\\'")
            else:
                widget=SQLFORM.widgets[field.type].widget(field,'a_value').xml()
            
            str="""
               function (value, options) {var el = document.createElement('div');  el.innerHTML='%s'.replace('a_value',value);  
               %s
               el.children[0].style.width="100%%";
               return el;
               }""" 
            return str% (widget,calendar);
        
    def get_custom_value_function(self,field):
        if field.type=='boolean':
            return "get_bool_value"        
        elif field.widget and field.widget.func_name=='nicEdit':
            return "function (elem) {return nicEditors.findEditor('%s').getContent();}" % (field._tablename+"_"+field.name)       
        else:
            return "get_normal_value"
    
    def get_custom_formatter_function(self,grid_name,field):
        
        if field.type=='boolean':

            return """function (cellvalue, options, rowObject) {
                    var checked;
                    if (cellvalue)
                         checked="checked='checked'";
                    else    
                         checked='';
                    return "<input type='checkbox' " + checked +  " disabled='disabled'/>";
            }"""        
        elif self.has_lookups(field):
            return """
            function (cellvalue, options, rowObject) 
                    {
                    if (cellvalue ==null) 
                        text=''; 
                    else {
                        text=lookups['%s-%s'][cellvalue];
                        if (text+''=='undefined')
                           text='unknown:'+cellvalue;
                    }    
                    return text;
                    }
                    
            """ % (grid_name,field.name)        
        else:
            return "undefined"
    
    def get_lookups(self,field):
        requires = field.requires
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        if requires:
            if hasattr(requires[0], 'options'):
                options = requires[0].options()        
        return ','.join(["'%s':'%s'" % o for o in options])
    
    def has_lookups(self,field):
        from gluon.sqlhtml import OptionsWidget
        return OptionsWidget.has_options(field)
        

    
    def __init__(self,table,fieldname=None,fieldvalue=None,grid_name='grid',columns=None,col_width=80,height=300,db_name='db',caption='',id_represent=['id',None]):
        if not columns:
            columns=table.fields
        if not 'id' in columns:
            columns.insert(0,'id')
        
        if fieldname and  fieldname in columns:
            columns.remove(fieldname)
            
        self.params=Storage()
        if caption=='':
            caption=table._tablename
        self.params.grid_name=grid_name
        self.params.caption=caption
        import urllib        
        columns_param='@'.join(columns)
        if id_represent[1]:
            import cgi
            from StringIO import StringIO
            id_represent_url=''
            out=StringIO(id_represent_url)
            cgi.mimetools.encode(StringIO(cgi.urlparse.unquote(str(id_represent[1]))),out,'base64')
            id_represent_url=out.getvalue()
        else:
            id_represent_url="None"
        self.params.url=URL(a=request.application,c='plugin_editable_jqgrid',f='call',args=['json','get_rows',table._tablename,db_name,columns_param,fieldname,fieldvalue,id_represent[0],id_represent_url])
        
        
        self.params.edit_url=URL(a=request.application,c='plugin_editable_jqgrid',f='call',args=['json','save_row',table._tablename,db_name,fieldname,fieldvalue])
        self.params.lookups='{'+','.join(["'"+grid_name+'-'+f+"':{"+self.get_lookups(table[f])+"}" for f in columns if self.has_lookups(table[f])])+'}'
        def get_col_header(col_name):
            if col_name=='id':
                return id_represent[0]
            else:    
                return table[col_name].label
        
        self.params.col_names='['+','.join(["'"+get_col_header(f)+"'" for f in columns])+']'
        self.params.col_models= "[{name:'id',index:'id', width:85, editable: false},\n" 
        
        def options():
            return (self.get_custom_formatter_function(grid_name,table[f]),f,f,self.get_custom_element_function(table[f]),self.get_custom_value_function(table[f]))        
        
        self.params.col_models+=','.join(["{formatter:%s,name:'%s',index:'%s',editable:true,edittype:'custom',editoptions:{custom_element: %s, custom_value:%s}}\n" % options() for f in columns if f!='id'])+']'
        
        response.files.append(URL(r=request,c='static/plugin_editable_jqgrid',f='plugin_editable_jqgrid.js'))
        response.files.append(URL(r=request,c='static/plugin_editable_jqgrid',f='jquery-ui-1.7.2.custom.min.js'))
        response.files.append(URL(r=request,c='static/plugin_editable_jqgrid',f='jquery-ui-1.7.2.custom.css'))
        response.files.append(URL(r=request,c='static/plugin_editable_jqgrid/i18n',f='grid.locale-it.js'))
        response.files.append(URL(r=request,c='static/plugin_editable_jqgrid',f='jquery.jqGrid.min.js'))
        response.files.append(URL(r=request,c='static/plugin_editable_jqgrid',f='ui.jqgrid.css'))
        
    def xml(self):
        
        return self.text % self.params
                                

    def __str__(self):
        return self.xml()
