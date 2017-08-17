import re
import os
import psycopg2

OKGREEN = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'

##CALLING TCL FILE IN PYTHON CODE##

os.system('./login_demo')

##CONNECTING TO THE POSTGRES##
try:
        conn = psycopg2.connect("dbname='template1' user='postgres' host= 'localhost'")
	print "\n\n"
	print OKGREEN + "CONNECTION ESTABLISHED" + ENDC	
        cur = conn.cursor()
	print OKGREEN + "CURSOR OBJECT CREATED" + ENDC
except:
        print FAIL + "UNABLE TO CONNECT TO DATABASE" + ENDC

##TO DROP THE TABLE##

try:
        drop_table = "DROP TABLE interface"
	print OKGREEN + "TABLE DROPPED" + ENDC
        cur.execute(drop_table)
        conn.commit()
	print OKGREEN + "TRANSACTION COMMIT DONE" + ENDC
except:
        print FAIL + "CANT DROP TABLE INTERFACE" + ENDC

##CREATING A TABLE INTERFACE##

try:
        create_table = """CREATE TABLE interface (
		HOSTNAME varchar(30),
                INTERFACE varchar(30),
                IP_ADDRESS varchar(30),
                SUBNET_MASK varchar(30),
		STATUS varchar(30));"""
        cur.execute(create_table)

	print OKGREEN + "TABLE CREATED SUCCESFULLY" + ENDC
        conn.commit()

except:
        print FAIL + "CANNOT CREATE TABLE INTERFACE" + ENDC

##CREATING MS EXCEL FILE##

fp2 = open("data.csv","a")
print OKGREEN + "CSV FILE CREATED" + ENDC
fp2.write("Hostname"+","+"Interface"+","+"Ip_address"+","+"Subnet"+","+"Status")
fp2.write("\n")
fp2.close()

##CREATING FUNCTION TO EXTRACT DATA##

def config(cfg,txt):

##OPENING TWO FILES##

	try:
        	fp = open(cfg,"r")
		fp1 = open(txt,"r")
		print OKGREEN + cfg + " FILE OPENED " + ENDC 
		print OKGREEN + txt + " FILE OPENED " + ENDC 

	except:
        	print FAIL + "CANNOT OPEN FILE " + ENDC

##CREATING LIST TO SAVE THE RAW DATA##

	main_list = []

##WHILE (ALWAYS TRUE)##
	while(1):

##READING DATA FROM FILE LINE BY LINE##

        	str = fp.readline()

##BREAK AT THE END OF LINE##
        	if not str:
                	break
##REGULAR EXPRESSION TO EXTRACT INTERFACES##
        	obj = re.match(r"(interface) (FastEthernet.\/+[0-9]+)",str)
        	obj1 = re.match(r"(^ ip address) (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",str)

		obj2 = re.match(r"(hostname) ([A-Za-z0-9]*)",str)
	
		if obj2:
			hostname = obj2.group(2)

        	if obj:
                	list = []
                	list.append(obj.group(2))
                	main_list.append(list)


        	if obj1:
                	list.append(obj1.group(2))
                	list.append(obj1.group(3))

##CREATING INNER LIST TO APPEND THE DATA INTO MAIN LIST##
	inner_list = []
	main_list1 = []

##LOOP TO ADD THE MISSING FEILDS##
	for n in main_list:
        	length = len(n)
        	if length == 3:
			inner_list.append(hostname)	
                	inner_list.append(n[0])
                	inner_list.append(n[1])
                	inner_list.append(n[2])
                	main_list1.append(inner_list)
                	inner_list = []
        	if length == 1:
			inner_list.append(hostname)
                	inner_list.append(n[0])
                	inner_list.append("unassigned")
                	inner_list.append("unassigned")
              	 	main_list1.append(inner_list)
                	inner_list = []

##CONVERTING LIST INTO TUPLE##
	main_tuple = tuple(main_list1)
	print OKGREEN + "TUPLE CREATED" + ENDC
##MATCHING THE STATE OF INTERFACE##

	substr = "up"
	int_main = []

	while(1):
        	str = fp1.readline()
        	if not str:
                	break
        	intr = re.match(r"(FastEthernet.\/+[0-9]+)",str)
       		if intr:
                	list = []
##MATCHING THE SUBSTRING IN STRIN##
	#IF TRUE THEN APPEND##
                
                	if substr in str:
             
                        	list.append(substr)
                	else:
       
                        	list.append("administratively down")
##APPEND LIST INTO INT_MAIN LIST##
        	int_main.append(list)
	
##REMOVING THE FIRST ELEMENT OF THE LIST WHICH IS "TYPE OF STRING"##
	int_main = int_main[1:len(int_main)]


##CREATING FINAL LIST CONTAINING DATA OF BOTH LIST##

	final_list = []

##TO READ BOTH THE LIST ELEMENTS PARALLELY##
	for a,b in zip(main_list1,int_main):
		final_list.append(tuple(a+b))

##CONVERTING FINAL LIST INTO TUPLE##
	main_tuple = tuple(final_list)


##WRITING INSERT QUERY##
	try:
        	insert_query = """INSERT INTO interface (hostname,interface,ip_address,subnet_mask,status) VALUES (%s, %s, %s, %s, %s)"""
        	cur.executemany(insert_query, main_tuple)
		print OKGREEN + "DATA INSERTED SUCCESSFULLY" + ENDC
       		conn.commit()
	except:
        	print OKGREEN + "UNABLE TO INSERT DATA IN  INTERFCACE TABLE"+ ENDC
	

##OPENING CSV FILE##
	fp2 = open("data.csv","a")

##LOOP TO WRITE IN CSV FILE##
	for n in main_tuple:
		for ele in n:
			fp2.write(ele+",")
		fp2.write("\n")
	fp1.close()
	fp2.close()

##TAKING .cfg AND .txt FROM LIST## 

config_files = os.popen('ls *cfg').read()
config_files_list = config_files.split()

txt_files = os.popen('ls *txt').read()
txt_files_list = txt_files.split()

##LOOP TO CALL CONFIG FUNCTION FOR EACH FILE##
for n,m in zip (config_files_list,txt_files_list):
	config(n,m)

