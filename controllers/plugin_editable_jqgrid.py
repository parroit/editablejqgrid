import cgi

def contains_html(field):
    return field.__dict__.has_key('contains_html') and field.contains_html
def non_textfield(field):
    return field.type!="string" and field.type!="text"

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()


@service.json
def save_row():
    table=get_db()[request.args[2]]
    if request.vars.oper=='edit':
        from gluon.storage import Storage
        cust=Storage()
        
        for f in table.fields:
            if request.vars.has_key(f) and f!='id':
                #here non-html fields are escaped
                field=table[f]
                value=request.vars[f]
                if value=='' and field.default and request.vars.id=='new': 
                    value=field.default
                    
                if non_textfield(field) or contains_html(field):
                    cust[f]=value                        
                else:
                    cust[f]=cgi.escape(value)                        

        if request.args[4]!='None':
            cust[request.args[4]]=request.args[5]
            
        if request.vars.id=='new':
            return dict(Id=table.insert(**cust))
        else:
            get_db()(table.id==request.vars.id).update(**cust)
            return dict(Id=request.vars.id)
    else:
        if request.vars.oper=='del':
            for del_id in request.vars.id.split(','):
                get_db()(table.id==del_id).delete()
            
def get_db():
    return eval(request.args[3])

@service.json
def get_rows():
    table=get_db()[request.args[2]]
    fields = table.fields
    rows = []
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    orderby = table[request.vars.sidx]
    if orderby and request.vars.sord == 'desc': orderby = ~orderby
    
    filter_field_name=request.args[5]    
    filter_field_value=request.args[6]    
    id_represent=''
    from StringIO import StringIO     
    out=StringIO(id_represent)
    import cgi
    
    
    if request.args[8]=='None':
        id_represent='%(id)s' 
    else:
        cgi.mimetools.decode(StringIO(request.args[8]),out,'base64')
        id_represent=out.getvalue()
        id_represent='<a href="%s">%s</a>' %(id_represent,request.args[7])
        
    field_names=request.args[4].split('@')
    
    fields=[table[f] for f in field_names]
    
    searchField=request.vars.searchField
    searchString=request.vars.searchString
    searchOper={'eq':lambda a,b: a==b,
                'nq':lambda a,b: a!=b,
                'gt':lambda a,b: a>b,
                'ge':lambda a,b: a>=b,
                'lt':lambda a,b: a<b,
                'le':lambda a,b: a<=b,
                'bw':lambda a,b: a.like(b+'%'),
                'bn':lambda a,b: ~a.like(b+'%'),
                'ew':lambda a,b: a.like('%'+b),
                'en':lambda a,b: ~a.like('%'+b),
                'cn':lambda a,b: a.like('%'+b+'%'),
                'nc':lambda a,b: ~a.like('%'+b+'%'),
                'in':lambda a,b: a.belongs(b.split()),
                'ni':lambda a,b: ~a.belongs(b.split())}\
                [request.vars.searchOper or 'eq']
    
    if filter_field_name!='None':
        dbset = get_db()(table[filter_field_name]==filter_field_value)
    else:
        dbset = get_db()(table.id>0)
        
    if searchField: dbset=dbset(searchOper(table[searchField],searchString))    
    
    for r in dbset.select(limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f.name =='id':
                vals.append(id_represent % r)
            else:
                rep = f.represent
                #if rep:
                #    vals.append(rep(r[f.name]))
                #else:
                vals.append(r[f.name])
        rows.append(dict(id=r.id,cell=vals))
    total = get_db()(table.id>0).count()       
    pages = int(total/pagesize)
    if total % pagesize > 0: pages += 1 
    data = dict(total=pages,page=page,rows=rows)
    return data
