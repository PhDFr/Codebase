##############################################################
## Author: simon.dold@physik.uni-freiburg.de
## This file contains functions thay help
# - Reading Data from textfiles
# - Pasing filenames and extraction information from it
#
##############################################################

import re
import os
import time
import numpy as np
    
#     
#     read file, get array of lines
def readFile(filename):
         with open(filename) as f:
                 data = f.read()
         data = data.splitlines()
         return data

#       read data from a file which contains only data 
#       in columns, separated by whitespace or a sparator
#       use variable separator in that case
def readSimpleFile(filename,sparator=""):
        data=readFile(filename)
        if not sparator: 
                column_data = np.array([[float(i) for i in  row.split()] for row in data ])  
        else:
                column_data = np.array([[float(i) for i in row.split()] for row in data ])  
        column_data = np.transpose(column_data)
        return column_data

#     
#     read the first two columns of a file
#     this one, historically comes from the mass-spectra data taken with the
#     national insttruments box and labview
def getFileData(filename, invert=False, separator='\t'):
          x_column = 0
          y_column = 1
          with open(filename) as f:
                  data = f.read() 
          data = data.splitlines()
          x = np.array([float(row.split(separator)[x_column]) for row in data if len(row.split(separator)) >=2])
          y = np.array([float(row.split(separator)[y_column]) for row in data if len(row.split(separator)) >=2])
          if invert:
                  y = -y
          return [x,y]

def parseMQFilename(f):
        '''
        ###############################################
        #
        # A simple Parser to extract  
        # certain patterns form a filename 
        # don't use this approach, regex (see below)
        # is much cleaner and more flexible
        ###############################################
        '''
        Power =6666
        press= 1111
        parts = f.split('_')
        month = parts[0][4:6]
        day   = parts[0][6:8]
        T = parts[1][6:]
        T = T[:-4]
        gases=parts[2]
        L1 = parts[3]
        L2 = parts[4]
        L3 = parts[5].split('Lens')[0]
         
        if  len(parts[5].split('Lens')) > 1:
                if len(parts[5].split('Lens')[1].split('watts')) > 1:
                        Power = parts[5].split('Lens')[1].split('watts')[0]
                        if len(parts[5].split('Lens')[1].split('watts')[1].split('mbar')) >1:
                                press = parts[5].split('Lens')[1].split('watts')[1].split('mbar')[0]
                        
        
        else:
                print 'Encountered strange filename'
                Power = parts[6].split('Lens')[1].split('watts')[0]
                if len(parts[6].split('Lens')[1].split('watts')[1].split('mbar')) > 1:
                         press = parts[6].split('Lens')[1].split('watts')[1].split('mbar')[0]

#        print day+'.'+month+'|'+T +'|'+ gases+'|'+L1+'/'+L2+'/'+L3+'|'+Power+'W '+press +'m'
        return [day+'.'+month,T,gases,L1+'/'+L2+'/'+L3,Power,press]

def createLabelBits(pathToFile):
        labelBits={}
        dataFromFilename=parseHvampFilename(pathToFile)
        labelBits["Date"]        = str(dataFromFilename[0][0])+str(dataFromFilename[0][1])+str(dataFromFilename[0][2])
        labelBits["Temperature"] = str(dataFromFilename[1])
        labelBits["Power"]       = str(dataFromFilename[2])
        labelBits["AccFreq"]     = str(dataFromFilename[3])
        labelBits["Pressure"]    = str(dataFromFilename[4])
        labelBits["ADL"]         = str(str(dataFromFilename[5][0])+'/'+str(int(dataFromFilename[5][1]))+'/'+str(int(dataFromFilename[5][2])))
        labelBits["Gas"]         = str(dataFromFilename[6])

        return labelBits

#        return [date,T,power,F,pressure,adl,gas]

def getHvampLabel(pathToFile):
        infoList={"Gas","ADL","Pressure"} 
        return buildHvampLabel(pathToFile,infoList)

def buildHvampLabel(pathToFile,infoList):
        label=""
        labelBits=createLabelBits(pathToFile)
        for i in infoList:
                label+=labelBits[i]+" "
        return label

def parseHvampFilename(pathToFile):
	'''
        ###############################################
        #
        # Using Regular Expressions (regs) to extract 
        # certain patterns form a filename 
        # (filename is extracted from a pathToFile)
        # Also a nice example for functions in functions
        ###############################################
        '''

	possible_dividers = ['-','_']
	
	div_reg = '['
	for d in possible_dividers:
		div_reg+= d+'|'
	div_reg= div_reg[:-1]
	div_reg += ']'
	
        f=os.path.basename(pathToFile)
        	
	date = parseFilenameForDate(f)
	if not date:
		print('File '+f+' not of correct format')
		return
	
	temperature_reg 	=div_reg+'Tminus[0-9]{2,3}'+'('+div_reg+'|$)'
        power_reg		=div_reg+'[0-9]{1,3}(Watt|watts)'+'('+div_reg+'|$)'
	scanning_freq_reg	=div_reg+'[0-9]{1,3}(Hz|hz)'+'('+div_reg+'{0,1})'
	press_reg		=div_reg+'[0-9]{1,3}mbar'+'('+div_reg+'|$)'
	adl_reg1		=div_reg+'[0-9]{2,3}'+div_reg+'[0-9]{2,3}'+div_reg+'[0-9]{2,3}'+'('+div_reg+'|$)'
	adl_reg2		=div_reg+'ADL[0-9]{1,3}'+div_reg+'[0-9]{1,3}'+div_reg+'[0-9]{1,3}'+'('+div_reg+'|$)'
	
	possible_gases=['Ar','He','Kr','Xe','Air']
	gas_reg = '('
	for d in possible_gases:
		gas_reg+= d+'|'
	gas_reg= gas_reg[:-1]
	gas_reg += ')'
	
	gas_reg			=div_reg+'([0-9]{1,4}'+gas_reg+')*'+'('+div_reg+'|$)'

        
        def matchAndExtract(reg,f):
           match= re.search(reg,f)
           if match is not None:
                ex_str = match.group()
                for i in possible_dividers:
                    ex_str=ex_str.strip(i)
                return ex_str
           return False


        T=-1
        power=-1
        F=-1
        pressure=-1
        adl=[-1,-1,-1]
        gas=""
        
        ex_str = matchAndExtract(temperature_reg,f)        
        if ex_str:
          T=float(ex_str.strip("Tminus"))
        
        ex_str = matchAndExtract(power_reg,f)        
        if ex_str:
          Power=float(ex_str.strip("Watt"))

        ex_str=matchAndExtract(scanning_freq_reg,f)
        if ex_str:
          F=float(ex_str.strip("Hz").strip("hz"))

        ext_str= matchAndExtract(press_reg,f)
        if ext_str:
          if float(ext_str.strip("mbar")[:1]) == 0: 
            pressure = float((ext_str[:1]+'.'+ext_str[1:]).strip("mbar"))
          else:
                pressure = float(ext_str.strip("mbar"))

        ext_str= matchAndExtract(adl_reg1,f)
        print(ext_str)
        if ext_str:
          for i in possible_dividers:
            if len(ext_str.split(i)) > 1:
                ext_str=ext_str.split(i)
                break
          k=0 
          for i in ext_str:
            adl[k]=float(i)
            k+=1



        ext_str= matchAndExtract(adl_reg2,f)
        if ext_str:
          ext_str=ext_str.strip("ADL")
          for i in possible_dividers:
            if len(ext_str.split(i)) > 1:
                ext_str=ext_str.split(i)
                break
          k=0 
          for i in ext_str:
            adl[k]=float(i)
            k+=1

  
        ex_str = matchAndExtract(gas_reg,f)
        if ex_str:
            gas=ex_str



        return [date,T,power,F,pressure,adl,gas]
	

	
	
def parseFilenameForDate(filename):
    '''
    ###############################################
    #
    # If a String starts with a date of YYYYmmdd
    # return year month day
    #
    ###############################################
    '''
    potential_date_str = filename[0:10]
    
    dividers = {'_','-','.'}
    
    divided_date_regs = []
    
    # American Dates
    for d in dividers:
        divided_date_regs.append('^(19|20)\d{2}['+d+']{1}(0[1-9]|1[012])['+d+']{1}(0[1-9]|[12][0-9]|3[01])')
    
    date_reg = '^(19|20)\d{2}(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])'
    
    ret=False
    
    for reg in divided_date_regs:
        match = re.match(reg, potential_date_str)
#        print(match)
        if match is not None:
#            print("This string starts with a date")
            year = potential_date_str[0:4]
            month = potential_date_str[5:7]
            day = potential_date_str[8:10]
            ret=True
            
            
    match = re.match(date_reg, potential_date_str)
#    print(match)
    if match is not None:
#        print("This string starts with a date")
        year = potential_date_str[0:4]
        month = potential_date_str[4:6]
        day = potential_date_str[6:8]
        ret=True
        
    return [year,month,day] if ret else False ;
        
def checkStringForDate(filename):
    return parseFilenameForDate(filename)

     
  
def convertToUnixTime(string):
    '''
    ###############################################
    #
    # Read a date from a filename and convert the
    # date to a Unix Timestamp
    #
    ###############################################
    '''
    if parseFilenameForDate(string) is not False:
            year,month,day = parseFilenameForDate(string)
    else:
        raise ValueError("Couldn't add to database: "+string+"is not a valid recTime")        
    startDate = '%s %s %s' % (day, month, year)
    return time.mktime(time.strptime(startDate, '%d %m %Y'))
