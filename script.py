import csv
import io
import datetime

def readRealtimeProcOutput(proc):
	print "Entering readRealTimeProcOutput"
	import sys
	for c in iter(lambda: proc.stdout.read(1), ''):
		sys.stdout.write(c)
		sys.stdout.flush()
	print "Leaving readRealTimeProcOutput"

def runSubProcess(cmd, report_file):
	import time
	import threading
	import os
	import signal

	#print cmd
	proc = PopenBash(cmd)
	print "Iniciando..."
	t = threading.Thread(target=readRealtimeProcOutput, args = [proc])
	t.daemon = True
	t.start()
	start_time = time.time()
	timeout = 86400 #86400 seconds of a day
	sleep_time = 5 #5 seconds
	seconds_passed = time.time() - start_time
	remaining_time = timeout - seconds_passed
	while proc.poll() is None and remaining_time > 0: # Monitor process
		# time.sleep(sleep_time) # Wait a little
		seconds_passed = time.time() - start_time
		remaining_time = timeout - seconds_passed
		# if(seconds_passed > 250):
			# sleep_time = min(seconds_passed / 50, remaining_time)
		# print "Executando: ", seconds_passed
	if(remaining_time <= 0):
		print "Timeout..."
		#print "Identified timeout after: " + str(time.time() - start_time) 
		os.killpg(proc.pid, signal.SIGINT)	
		t.join()
		proc.stdout.close()
		with open(report_file, 'a') as f:
			writeNewLine(f, "")
			writeNewLine(f, "TIMEOUT...")
		returnCode = -1
	else:
		returnCode = proc.returncode
	#proc.communicate()[0]
	print "Java Return Code: " +str(returnCode)

def PopenBash(cmd):
	import subprocess
	import os
	return subprocess.Popen(["/bin/bash","-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)

def makeFiledirs(filename):
	import os
	import os.path
	dir = os.path.dirname(filename)
	makedirs(dir)

def readLines(path):
	fil = open(path)
	return fil.read().splitlines()

def writeNewLine(file, content):
	file.write(content + "\n")

def makedirs(dir):
	import os
	import os.path
	if not os.path.exists(dir):
		os.makedirs(dir)


def exceptionToStr(ignoreExceptions):
	if ignoreExceptions == "true":
		return "noExcep"
	else:
		return "excep"

def run_joana(REV_GIT_PATH, REV_REPORTS_PATH, REV_SDGS_PATH, revContribs, heapStr, libPaths):
	print "Running Joana..."
	import sys
	import os.path
	
	baseCmd = "nohup java " + heapStr + " -jar joana_inv.jar \"" + REV_GIT_PATH + "\" \""+ REV_REPORTS_PATH + "\" \"" + REV_SDGS_PATH + "\""

	baseCmd += " \'" +revContribs + "\'"
	baseCmd += " \"" +libPaths + "\""
	#print baseCmd
	#ignoreExceptions=["true", "false"]
	ignoreExceptions=["false"]
	initialExceptionMsg = "ignoreExceptions="
	initialPrecisionMsg = "initialPrecision="
	precisions = ["TYPE_BASED", "INSTANCE_BASED","OBJECT_SENSITIVE", "N1_OBJECT_SENSITIVE", 
		"UNLIMITED_OBJECT_SENSITIVE", "N1_CALL_STACK", "N2_CALL_STACK", "N3_CALL_STACK"]
	precisionsIds = [4]#xrange(8)#[0,1,2,3,4,5,6,7]
	if(os.path.exists(REV_REPORTS_PATH + "/executionSummary.csv")):
		open(REV_REPORTS_PATH + "/executionSummary.csv","w").close()
	for ignoreException in ignoreExceptions:
		cmde = baseCmd + " \"" + initialExceptionMsg + ignoreException + "\""
		print
		print "Ignore Exceptions: "+str(ignoreException)
		for i in precisionsIds:
			cmd = cmde + " \""	+ initialPrecisionMsg + str(i) + "\"" 
			print "Precision: "+precisions[i]
			print
			sys.stdout.flush()			
			sysout_path = REV_REPORTS_PATH + "/" + precisions[i] + "_" +exceptionToStr(ignoreException) + "_sysout.txt"
			if(os.path.exists(sysout_path)):
				open(sysout_path, "w").close()
			else:
				makeFiledirs(sysout_path)
			print cmd
			print
			#runSubProcess(cmd, sysout_path)
			runSubProcess(cmd + " > "+sysout_path, sysout_path)
			sys.stdout.flush()

def getRevContribs(contribs, rev):
	revContribs=[]
	for contrib in contribs:
		splittedContrib = contrib.split("; ")
		print splittedContrib
		if len(splittedContrib) > 1:
			currentRev = splittedContrib[1]
			if currentRev == rev:
				revContribs.append(contrib)
	return '\n'.join(revContribs)

def checkIfIsInYearRange(yearRange, revHasContrib, revContribs):
	isInYearRange = len(yearRange) != 2 or (yearRange[0] == "" and yearRange[1] == "")
	if(revHasContrib and (not(isInYearRange))):
			startYear = yearRange[0]
			endYear = yearRange[1]
			fullDate = revContribs.split("\n")[0].split("; ")[2]
			strLen = len(fullDate)
			yearStr = fullDate[(strLen - 4):strLen]
			year = int(yearStr)
			isInYearRange = ((startYear == "" or year >= int(startYear)) and (endYear == "" or year <= int(endYear)))
	return isInYearRange

def getHeapComplement(path):
	if path[:27] == "/home/conflicts_analyzer/":
		comp = "-Xms1024g -Xmx2048g"#"-Xms128g -Xmx192g"
	else:
		comp = "-Xms1024g -Xmx2048g" # "-Xms1g -Xmx2g" #"-Xms4m -Xmx8m"
	return comp

def runJoanaForSpecificRevs():
	print "##########Executando###############"
	import os
	currDir = os.getcwd()
	CA_PATH = currDir + "/conflicts_analyzer"
	heapStr = getHeapComplement(currDir)
	DOWNLOAD_PATH = CA_PATH + "/downloads"
	REPORTS_PATH = CA_PATH + "/reports"
	SDGS_PATH = CA_PATH + "/sdgs"

	revList = readLines(CA_PATH + "/revList")
	print "\nRevList", revList

	for revLine in revList:
		revLineSplitted = revLine.split(",")
		project = revLineSplitted[0].strip()
		PROJECT_REPORTS_PATH = REPORTS_PATH + "/" + project
		PROJECT_SDGS_PATH = SDGS_PATH + "/" + project
		PROJECT_PATH = DOWNLOAD_PATH + "/" +project
		print "Lista de projetos ", PROJECT_PATH
		# revBaseStr = "rev"
		revStr = revLineSplitted[1].strip()
		# rev = revBaseStr + "_" + revStr
		# splittedRev = revStr.split("_")
		# left = splittedRev[0].strip()
		# right = splittedRev[1].strip()
		# inner_rev = revBaseStr + "_" + left + "-" + right
		# inner_rev = revBaseStr + "_" + revStr
		inner_rev = revStr
		ES_MC_PATH = PROJECT_PATH + "/" + revStr
		REV_GIT_PATH = ES_MC_PATH + "/" + "original-without-dependencies" + "/" + "merge"
		print "\n\nprojects " + PROJECT_REPORTS_PATH + "/editSameMCcontribs.csv"
		project_contribs = readLines(PROJECT_REPORTS_PATH + "/editSameMCcontribs.csv")
		revContribs = getRevContribs(project_contribs, inner_rev)
		print "\n\nrevContribs: "+ revContribs
		print "\n\nproject_contribs "+ PROJECT_REPORTS_PATH + " - " + inner_rev

		print "\n\nGIT PAH", REV_GIT_PATH
		
		print "\n\nREV ", revStr
		REV_REPORTS_PATH = PROJECT_REPORTS_PATH + "/" + revStr
		REV_SDGS_PATH = PROJECT_SDGS_PATH + "/" + revStr
		libStr = "/media/galileu/Arquivos/Doutorado/Pesquisa/JOANA/joana_execution/libs/"
		# if(len(revLineSplitted) >= 3):
			# libStr = revLineSplitted[2].strip()
		print "\n\nGIT", REV_GIT_PATH, "\n\nREV_REPORTS", REV_REPORTS_PATH, "\n\nSDG", REV_SDGS_PATH, "\n\nRevContrib", revContribs, "\n\nHeapSTR", heapStr, "\n\nLibSTR", libStr
		run_joana("/media/galileu/Arquivos/Doutorado/Pesquisa/JOANA/joana_execution/", REV_REPORTS_PATH, REV_SDGS_PATH, revContribs, heapStr, libStr)

def main():
	build_all = True
	build_rev_merged = True
	build_rev_ss = True
	import os
	import os.path
	currDir = os.getcwd()
	CA_PATH = currDir + "/conflicts_analyzer"
	heapStr = getHeapComplement(currDir)
	DOWNLOAD_PATH = CA_PATH + "/downloads"
	REPORTS_PATH = CA_PATH + "/reports"
	SDGS_PATH = CA_PATH + "/sdgs"
	projectList = readLines(CA_PATH + "/projectsList")
	yearRangeFil = CA_PATH + "/yearRange"
	yearRangeFilExists = os.path.exists(yearRangeFil)
	yearRange = ["",""]
	if(yearRangeFilExists):
		yearLines = readLines(yearRangeFil)
		if len(yearLines) > 0:
			yearRangeStr = yearLines[0]
			yearRange = yearRangeStr.split("-")
	for project in projectList: 
	   project_name = project.split("/")[1]
	   PROJECT_PATH = DOWNLOAD_PATH + "/" +project_name
	   projectExists = os.path.exists(PROJECT_PATH)
	   print PROJECT_PATH + " ProjectExists: " +str(projectExists)
	   if projectExists:
		   PROJECT_REPORTS_PATH = REPORTS_PATH + "/" + project_name
		   PROJECT_SDGS_PATH = SDGS_PATH + "/" + project_name
		   ES_MC_PATH = PROJECT_PATH + "/editsamemc_revisions"
		   projectHasEditSameMC = os.path.exists(ES_MC_PATH)
		   print ES_MC_PATH + " ProjectHasEditSameMC: "+str(projectHasEditSameMC)
		   if projectHasEditSameMC:
			   revs = [name for name in os.listdir(ES_MC_PATH)
			            if os.path.isdir(os.path.join(ES_MC_PATH, name))]
			   revsSize = len(revs)
			   print "Entrou", revsSize, " ", ES_MC_PATH
			   if revsSize > 0:
			   		if build_rev_ss: 
				   		buildSummaryPath = PROJECT_REPORTS_PATH + "/buildSummary.csv"
				   		makeFiledirs(buildSummaryPath)
				   		buildSummary = open(buildSummaryPath, "w", 0)
				   		writeNewLine(buildSummary, "Rev; Built; Gradle; Ant; Mvn; Built with")
				   	if build_rev_merged:
				   		buildSummaryPathMerge = PROJECT_REPORTS_PATH + "/buildSummaryMerge.csv"
				   		makeFiledirs(buildSummaryPathMerge)
				   		buildSummaryMerge = open(buildSummaryPathMerge, "w", 0)
				   		writeNewLine(buildSummaryMerge, "Rev; Built; Gradle; Ant; Mvn; Built with")
			   		project_contribs = readLines(PROJECT_REPORTS_PATH + "/editSameMCcontribs.csv")
			   for rev in revs:
			   		splittedRev = rev.split("_")
			   		left = splittedRev[1]
			   		right = splittedRev[2]
			   		inner_rev = splittedRev[0] + "_" + left + "-" + right
			   		REV_GIT_PATH = ES_MC_PATH + "/" + rev + "/" + inner_rev + "/git"
			   		print REV_GIT_PATH
			   		revContribs = getRevContribs(project_contribs, inner_rev)
			   		print "Contrib: " +revContribs
			   		revHasContrib = not(revContribs == '')
			   		print "Rev has contrib: "+str(revHasContrib)
			   		isInYearRange = checkIfIsInYearRange(yearRange, revHasContrib, revContribs)
			   		print "Is in year range: "+str(isInYearRange)
			   		shouldRunJoana = revHasContrib and isInYearRange
			   		print "Should Run Joana: "+str(shouldRunJoana)
			   		if (build_all or shouldRunJoana):		
			   			REV_REPORTS_PATH = PROJECT_REPORTS_PATH + "/" + rev
			   			built = not(build_rev_ss)
			   			if build_rev_ss:
			   				buildRes = build(REV_GIT_PATH, REV_REPORTS_PATH, "")
			   				built = buildRes.split(";")[0] == "True"
			   				writeNewLine(buildSummary, rev + "; "+buildRes)			   		
			   				print "Build Result: "+str(built)
			   			if build_rev_merged:
			   				REV_GITM_PATH = ES_MC_PATH + "/" + rev + "/rev_merged_git/git"
			   				buildResM = build(REV_GITM_PATH, REV_REPORTS_PATH, "merge_")
			   				builtM = buildResM.split(";")[0] == "True"
			   				writeNewLine(buildSummaryMerge, rev + "; "+buildResM)			   		
			   				print "Build Result merge: "+str(builtM)
			   			if built and shouldRunJoana:
				   			REV_SDGS_PATH = PROJECT_SDGS_PATH + "/" + rev
				   			#run_joana(REV_GIT_PATH, REV_REPORTS_PATH, REV_SDGS_PATH, revContribs, heapStr, "")


#home_joana = "/Users/galileu/Documents/Doutorado/Pesquisa/JOANA/joana_execution/"
home_joana = "/home/joana_execution/"

#homePath = "/Users/galileu/"
homePath = home_joana

currentDir = home_joana
datasetPath = home_joana+"downloads/"
libStr = home_joana+"libs/"
project_path_joana = home_joana

file_name_revList = homePath + "revList.csv"

def runJoana():
	print "##########Executando###############"
	import os
	#currentDir = os.getcwd()
	
	CA_PATH = currentDir + "conflicts_analyzer"
	
	heapStr = getHeapComplement(currentDir)
	
	DOWNLOAD_PATH = datasetPath
	REPORTS_PATH = homePath + "joana/reports"
	SDGS_PATH = homePath + "joana/sdgs"
	
	print "LENDO ARQUIVO DE ENTRADA DOS PROJETOS:", file_name_revList 
	
	ID = 1
	# Abrir o arquivo CSV para leitura
	with io.open(file_name_revList, mode='r', encoding='utf-8') as file:
		# Criar um leitor de CSV
		csv_reader = csv.reader(file, delimiter=';')
		
		# Ignorar a primeira linha (cabecalho)
		next(csv_reader)
		
		# Ler as linhas restantes e armazenar os dados em suas respectivas listas
		for row in csv_reader:
			project = row[0]
			merge_commit = row[1]
			class_path_name = row[2]
			
			parts = class_path_name.split('.')
			class_name = parts.pop()
			
			class_path = '.'.join(parts).replace(".", "/")

			method = row[3]
			left_modification = row[4]
			right_modification = row[7]

			revStr = project+"/"+merge_commit
			print "\n\nClass path:", class_path, class_name

			git_path_generated = datasetPath+revStr +"/source/"+class_path
			
			print "GIT PATH GENERATED:"+git_path_generated

			PROJECT_REPORTS_PATH = REPORTS_PATH + "/" + revStr
			PROJECT_SDGS_PATH = SDGS_PATH + "/" + revStr
			
			PROJECT_PATH = datasetPath + "/" + revStr
			print "Analisando projeto: ", PROJECT_PATH
			
			
			REV_GIT_PATH = git_path_generated

			print "\n\nprojects " + PROJECT_REPORTS_PATH
			
			revContribs = getContribs(row, ID)
			
			print "\n\nrevContribs: "+ revContribs
			
			print "\n\nGIT PAH", REV_GIT_PATH
			
			print "\n\nREV ", revStr
			
			REV_REPORTS_PATH = PROJECT_REPORTS_PATH+ "/" +class_path
			REV_SDGS_PATH = PROJECT_SDGS_PATH+ "/" +class_path
			
			print "\nGIT", REV_GIT_PATH, "\nREV_REPORTS", REV_REPORTS_PATH, "\nSDG", REV_SDGS_PATH, "\nRevContrib", revContribs, "\nHeapSTR", heapStr, "\nLibSTR", libStr
			
			run_joana("/Users/galileu/Documents/Doutorado/Pesquisa/JOANA/joana_execution/", REV_REPORTS_PATH, REV_SDGS_PATH, revContribs, heapStr, libStr)

			ID = ID + 1

def convert_to_list(input_str):
	clean_str = input_str.strip("[]")
	output_list = [int(x.strip()) for x in clean_str.split(",") if x.strip()]

	# Imprimindo a lista de inteiros
	return output_list


def getContribs(row, ID):

	DATE = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
	project = row[0]
	merge_commit = row[1]
	class_name = row[2]
	class_path = class_name.replace(".", "/")
	method = row[3]
	left_modification = row[4]
	right_modification = row[7]
	
	file_java = datasetPath+project+"/"+merge_commit+"/source/"+class_path+"/merge.java"

	qtd_lines = max(max(convert_to_list(left_modification)), max(convert_to_list(right_modification)))

	contribs = "%s;%s;%s;%s;%s;%s;%s;%s" % (ID, merge_commit, DATE, file_java, method, str(qtd_lines+300), left_modification, right_modification)

	# Imprimindo a saida
	return contribs

def contrib():
	# Nome do arquivo CSV
	
	file_name = home_joana+'revList.csv'
	
	ID = 1
	# Abrir o arquivo CSV para leitura
	with io.open(file_name, mode='r', encoding='utf-8') as file:
		# Criar um leitor de CSV
		csv_reader = csv.reader(file, delimiter=';')
		
		# Ignorar a primeira linha (cabecalho)
		next(csv_reader)
		
		# Ler as linhas restantes e armazenar os dados em suas respectivas listas
		for row in csv_reader:

			actual_contrib = getContribs(row, ID)

			print actual_contrib

			ID = ID + 1


# main()

#runJoanaForSpecificRevs()

runJoana()

