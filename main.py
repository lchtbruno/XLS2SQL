import mysql.connector, MySQLdb, xlrd, xlwt, os, getSheetNames

# detecting xls file
dir_path = os.path.dirname(os.path.realpath(__file__))
all_files = os.listdir(dir_path+"/ExcelFiles/")
if len(all_files)>1:
	print "More than one file detected in the 'ExcelFiles' folder. Use different worksheets to create multiple tables. A single .xls file represents a database."
	exit()

#importing xls file
excel_file=dir_path+"/ExcelFiles/"+all_files[0]
length_front_cutoff= len(dir_path+"/ExcelFiles/")
length_back_cutoff=len(".xls")

#set up database name
db_name=excel_file[length_front_cutoff:len(excel_file)-4]

#import workbook and sheets
workbook = xlrd.open_workbook(excel_file)
number_of_tables=len(workbook.sheet_names())

#create connection to mysql
mydb=mysql.connector.connect(host="localhost",user="root")

#init cursor
mycursor=mydb.cursor()

##delete database
#create_statement = "DROP DATABASE {:s}".format(db_name)
#mycursor.execute(create_statement)

#create and select database
create_statement = "CREATE DATABASE {:s}".format(db_name)
mycursor.execute(create_statement)

#select database
create_statement = "USE {:s}".format(db_name)
mycursor.execute(create_statement)

#list all sheet names in a workbook
list_of_sheet_tuples=getSheetNames.getting(excel_file)
list_of_sheet_names=[]
for i in range(len(list_of_sheet_tuples)):
	
	list_of_sheet_names.append(list_of_sheet_tuples[i][1])

#count nr of sheets in workbook
number_of_sheets = len(list_of_sheet_names) 

######################################################################################################################################################################################################################################################################################################################################################

for j in range(number_of_sheets):
	worksheet = workbook.sheet_by_index(j)

	#counting number_of_rows and columns
	number_of_rows=worksheet.nrows-1
	number_of_columns=worksheet.ncols

	try:
		mycursor.execute("CREATE TABLE %s (id MEDIUMINT NOT NULL AUTO_INCREMENT,PRIMARY KEY (id));" % list_of_sheet_names[j])
		
	except:
		print "An error occurred while creating a table. Are the sheets all named properly (no special characters and not solely a number!) ?"
		break

	#identify datatype and name of column, then create column in sql
	for i in range(number_of_columns):
		
		column_title=worksheet.cell(0,i).value
		datatype_of_column=type(worksheet.cell(1,i).value)

		if datatype_of_column==float:
			cell_type="FLOAT(10)"
		elif datatype_of_column==int:
			cell_type="INT(10)"
		elif datatype_of_column==unicode or datatype_of_column==str:
			cell_type="VARCHAR(100)"
		elif datatype_of_column==bool:
			cell_type="BINARY"
		else:
			print ('Datatype at column %s not recognized. Set to float.', i)

		mycursor.execute("ALTER TABLE %s ADD %s %s" % (list_of_sheet_names[j], column_title, cell_type))

	for n in range(1,number_of_rows+1):

		query="INSERT INTO {} (".format(list_of_sheet_names[j])
		query_values="("
		values=[]
		for i in range(number_of_columns):
			column_title=worksheet.cell(0,i).value
			value_for_table = worksheet.cell(n, i).value
			query=query+column_title if i==0 else query+','+column_title
			query_values=query_values+"%s" if i==0 else query_values+',%s'
			values.append(value_for_table)
		query=query+') VALUES '+query_values+')'
		mycursor.execute(query, values)

mydb.commit()
mydb.close()

