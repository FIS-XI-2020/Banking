
from django.shortcuts import render,redirect
from .models import Accounts
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from random import choice
import mysql.connector as mysc

# Create your views here.
user = None
payeeBalance = None
interestRate = 6/100
def Home(request):
	return render(request, 'Home.html')

def login(request):
	if(request.method == "POST"):
		data = request.POST
		username = request.POST['username']
		password = request.POST['password']
		info = Accounts.objects.all()
		#print("Login -",username, password)
		index = 0
		
		for i in range(0, len(info)):
			#print(info[i].UserName, info[i].Password, "\n")
			if(username == info[i].UserName and password == info[i].Password):
				index = i

		
		
		#if user is not None:
		if(username == info[index].UserName and password == info[index].Password):
			global user
			user = username
			print("Success")
			return render(request, 'Home.html')
		else:
			#print(Accounts.UserName, username)
			print("Invalid username or password.")
			return render(request, 'Login.html')

	else:
		return render(request, 'Login.html')
	


def Sign_Up2(request):
	if(request.method == "POST"):
		data = request.POST
		username = request.POST['username']
		password = request.POST.get('password')
		full_name = request.POST.get('FullName')
		email = request.POST.get('E_ID')
		print(username, password, full_name, email)
		database = Accounts.objects.all()
		present = []
		for i in database:
			present.append(i.Account_No)

		new_AN = choice([i for i in range(1000, 9999) if i not in present])
		print("New Acc No -", new_AN, "\n")
		info = Accounts(UserName = username, Password = password, Account_No = new_AN, Customer_Name = full_name, Curr_Balance = 10000, email = email)
		info.save()
		global user 
		user = username
		return render(request, 'Home.html')

	else:
		return render(request, 'Sign_Up2.html')

def transaction(request):
	if(request.method == "POST"):
		global user
		global payeeBalance
		data = request.POST
		payee=data["payee"]
		acc_no=data["acc_no"]
		amount=data["amount"]

		if(payee == user):
			return render(request, 'SelfTransact.html')
		info = Accounts.objects.all()
		#print(amount, "\n")
		index1, index2 = None, None
		for i in range(0, len(info)):
			print(info[i].Account_No, acc_no)
			if(payee == info[i].UserName and int(acc_no) == int(info[i].Account_No)):
				print(acc_no, info[i].Account_No)
				index1 = i
				break
			if(i == len(info)-1):
				return render(request, 'AccNoMismatch.html')	
		print("User -",user)
		for i in range(0, len(info)):
			#print(info[i].UserName, "\n")
			
			if(user == info[i].UserName):
				index2 = i
		
		con = mysc.connect(host = "localhost", user = "root", passwd = '0009', database = "12_athira")
		if con.is_connected():
			print("Successful")
		cur = con.cursor()
		try:
			if(int((info[index2].Curr_Balance)) > int(amount)):
				#adding the same amount in the second account
				info[index1].Curr_Balance = int((info[index1].Curr_Balance)) + int(amount)
				payeeBalance = info[index1].Curr_Balance
				print(payeeBalance, "\n")
				#subtracting the amount from the account 1
				info[index2].Curr_Balance = int((info[index2].Curr_Balance)) - int(amount)
				print(info[index2].Curr_Balance, "\n")
			
				cur.execute("update B_App_accounts set Curr_Balance = '%s' where Account_No = ('%s')"%(info[index1].Curr_Balance, int(acc_no)))
				cur.execute("update B_App_accounts set Curr_Balance = '%s' where UserName = ('%s')"%(info[index2].Curr_Balance, user)) 
				con.commit()
			else:
				return render(request, 'TrGreater.html')
			
		except(TypeError):
			return render(request, 'Error.html')
		except(ValueError):
			return render(request, 'AmtMissing.html')

		con = mysc.connect(host = "localhost", user = "root", passwd = '0009', database = "12_athira")
		cur = con.cursor()
		cur.execute("select Account_No, Curr_Balance from B_App_accounts where Account_No = ('%s')"%(acc_no))
		
		info = cur.fetchall()
		info1 = [info[0][0], payeeBalance]
		print(info1)

		return render(request,'personal_banking.html',{'info':info1})
	else:
		return render(request, 'Transactions.html')
	
def personal_bank(request):	
	global user
	if(user == None):
		return render(request, 'Error.html')

	con = mysc.connect(host = "localhost", user = "root", passwd = '0009', database = "12_athira")
	cur = con.cursor()
	cur.execute("select Account_No, Curr_Balance from B_App_accounts where UserName = ('%s')"%(user))
	info = cur.fetchall()
	print("info -", info)
	info1 = [info[0][0], info[0][1]]
	return render(request,'personal_banking.html',{'info':info1})

def loan(request):
	if request.method == 'POST':
		global user
		global interestRate
		data = request.POST
		Account_No = data['AccNo']
		name = data['FullName']
		months = data['months']
		amount = data['amount']
		db = Accounts.objects.all()
		#print(info, "\n")
		index = None
		for i in range(0, len(db)):
			if(int(Account_No) == db[i].Account_No and name == db[i].Customer_Name):
				index = i	
				break	
			if(i == len(db)-1):
				return render(request, 'AccNoMismatch.html')	
		if(db[index].UserName != user):
			return render(request, 'CrossLoan.html')
			
		
		db[index].Curr_Balance = db[index].Curr_Balance + int(amount)
		print(db[index].Curr_Balance)
		
		emi = (int(amount) + (int(amount)*interestRate))/int(months)
		print("EMI -",emi, "\n")
		
		con = mysc.connect(host = "localhost", user = "root", passwd = '0009', database = "12_athira")
		if con.is_connected():
			print("Successful")
		cur = con.cursor()
		cur.execute("update B_App_accounts set Curr_Balance = '%s' where Account_No = ('%s')", (db[index].Curr_Balance, int(Account_No)))
		con.commit()
		
		info = [Account_No, name, months, amount, int(emi)]
		return render(request, 'DisplayLoan.html', {'info':info})
	else:    
		return render(request, 'loan.html')


