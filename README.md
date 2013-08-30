editablejqgrid
==============

Editable JqGrid is a plugin for [http://www.web2py.com]web2py that make it easy to use [http://www.trirand.com/blog]JqGrid in your application.

**What is Editable JqGrid**


Editable JqGrid is a plugin for web2py that make it easy to use JqGrid in your application.
It's just a matter of install the plugin in the application and then call a single function from your controller.
Editable JqGrid is still in Beta stage, so use at your own risk!

**What is web2py**
Web2py is a Free and open source full-stack enterprise framework for agile development of fast, scalable, secure
 and portable database-driven web-based applications. Written and programmable in Python .

**What are web2py plugins**
web2py plugins are self contained pieces of an application that can be added to any existing application.
They usually define components, i.e. objects that can be embedded in a page and talk to the server via ajax.
Often they include corresponding jQuery plugins and the serverside funcitonality to make them work.
Here you can find some examples. The web2py admin interface provides a web interface to upload and manage the plugins.
The plugin themsselves are .w2p files (as for web2py apps). There are just tar gzipped files containing the source code.
You do not need to unzip them. The admin interface will unzip them on upload in web2py. Once a plugin becomes part of
your app, you can customize it without affecting other apps. Look and feel can be customized via CSS.

**Features**

* Inline editing of rows using web2py standard widgets
* Ajax updates,insertion,deletes of data
* Multiple grid in same page allowed
* Multiple database allowed
* Fully customizable by simple inheritance of a class (TODO)
* SQLTable similar syntax to easing the replace of your html table in existing application (TODO)
* Licensed under LGPL. You can use it in your commercial or open source application

*Download*
Download version 0.2.0 from [https://github.com/parroit/editablejqgrid/releases/download/0.0.2/web2py.plugin.editable_jqgrid.w2p]here


**Simple example**
First and obviously, you have to have a web2py application. For this example, we have defined following model:

    db_invoice = DAL('sqlite://invoice.sqlite')
    db_invoice.define_table('customer',
        Field('name','string'),
        Field('vat_code','string')
        )
    db_invoice.define_table('payment_type',
        Field('name','string'),
        Field('days','integer'),
        Field('end_of_month','boolean')
        )
    db_invoice.define_table('invoice',
        Field('code','string'),
        Field('customer',db_invoice.customer),
        Field('created_on','datetime'),
        Field('emitted_on','date'),
        Field('emitted_at','time'),
        Field('emitted','boolean'),
        Field('remarks','text'),
        Field('total_amount','double'),
        Field('tax_percentage','integer')
        )
    db_invoice.invoice.customer.requires=IS_IN_DB(db_invoice,'customer.id','customer.name')

This is standard w2p code... just an explanation on the function set_description_column.
This is a function that let you define a default column to compute the description for a row of a table.
The plugin use this information to show column values for reference column. Just pass the function the table
you want to use as a reference and the name of the descriptive column.

Now to use Editable JqGrid, Just put following line in your controller:


	return dict(
		customers=plugin_editable_jqgrid(db_invoice.customer,grid_name='customer',db_name='db_invoice'),
		invoice=plugin_editable_jqgrid(db_invoice.invoice,grid_name='invoice',db_name='db_invoice')
		)</pre>

And in your view:

    {{extend 'layout.html'}}
    {{=customers}}
    {{=invoice}}</pre>

Just that! And note that you must specify grid_name only if you want to use more than one grid in
the same page, and db_name only if it differ from 'db'.

To just use one simple grid, just use

*return dict(customers=jqGrid(db.customer)*
