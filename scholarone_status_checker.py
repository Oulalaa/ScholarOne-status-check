#-- coding:UTF-8 --
import os
import time
from subprocess import check_output
from bs4 import BeautifulSoup
from splinter import Browser
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

def print_ts(message):
	print( "[%s] %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), message))
def run(interval, command):
	print_ts("-"*100)
	print_ts("Command %s"%command)
	print_ts("Starting every %s seconds."%interval)
	print_ts("-"*100)
	current_status = "NULL"
	while True:
		try:
			# sleep for the remaining seconds of interval
			time_remaining = interval-time.time()%interval
			print_ts("Sleeping until %s (%s seconds)..."%((time.ctime(time.time() + time_remaining)), time_remaining))
			time.sleep(time_remaining)
			print_ts("Starting command.")
			# execute the command
			status = os.system(command)
			current_status = print_test(current_status)
			print_ts("-"*50)
		except Exception:
			print('error')

def send_email(content):
	# content = 'test'
	ret = True
	my_sender = '@qq.com'  # 发件人邮箱账号
	my_pass = 'XXXXX'  # 发件人邮箱密码(注意这个密码不是QQ邮箱的密码，是在QQ邮箱的SMTP中生成的授权码)
	my_user = 'XXXX@qq.com'  # 收件人邮箱账号，我这边发送给自己	 
	try:
	# 第三方 SMTP 服务
		 
		msg = MIMEText('There has been a new status change: \n \n \n' + content + '\n \n Check it in https://mc.manuscriptcentral.com/t-its', 'plain', 'utf-8') #修改为目标网页地址
		# print('text generated')
		msg['From'] = formataddr(["Status Monitoring Kit", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
		# print('from set')
		msg['To'] = formataddr(["我", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
		msg['Subject'] = 'Manuscript Status Changed'
		# print('msg has been compiled')
		server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器
		# print('port set')
		server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
		# print('mail logged in ')
		server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
		# print('mail sent')
		server.quit()  # 关闭连接
		# print("connection close")
	except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
		ret = False
		print("Error: 无法发送邮件")
	return ret

def print_test(status):

	wait_delay = 2
	previous_manuscript_status=status

	print('Previous status of manuscript was : ' + previous_manuscript_status)
	time.sleep(wait_delay)

	b = Browser('chrome')
	# b = Browser('chrome', headless=True)
	time.sleep(wait_delay)
	b.visit('https://mc.manuscriptcentral.com/t-its') #此处设置scholar one对应期刊的网址
	time.sleep(wait_delay)
	b.fill('USERID', 'XXXX@qq.com') #此处设置你的scholar one账号邮箱
	time.sleep(wait_delay)
	b.fill('PASSWORD','XXXX') # 此处设置你的scholar one账号密码
	time.sleep(wait_delay)
	if b.find_by_id( 'onetrust-accept-btn-handler'): # 此处处理scholar one登陆页面的cookie设置，接受cookie
		b.find_by_id( 'onetrust-accept-btn-handler').click()
		time.sleep(wait_delay)
	b.find_by_id( 'logInButton').click()
	time.sleep(wait_delay)


	b.links.find_by_partial_href("AUTHOR").click()
	time.sleep(wait_delay)
	html_obj = b.html
	soup = BeautifulSoup(html_obj,"lxml")
	#  soup = BeautifulSoup(html_obj)
	# table = soup.find("table", attrs={"class":"table table-striped rt cf"})
	table = soup.find("span", attrs={"class": "pagecontents"}) #此处需要依据scholar one中网页元素进行设置，用于定位页面元素。默认的可能有用
	print(table.string)
	# row = table.tbody.findAll('tr')[1]
	# first_column_html = str(row.findAll('td')[1].contents[0])
	current_manuscript_status = table.string
	# current_manuscript_status = BeautifulSoup(first_column_html,"lxml").text
	# current_manuscript_status = 'demo'
	# print current_status_msg
	time.sleep(wait_delay)
	b.quit()

	if current_manuscript_status == previous_manuscript_status:
		print('Your manucsript status remains unchanged ...')
		print('Please check back later \n')
	else:
		print("There has been a new status change... Sending updated paper status through email")
		send_email(current_manuscript_status)
		previous_manuscript_status = current_manuscript_status

	return current_manuscript_status



if __name__=="__main__":
	interval = 3600       #此处设置间隔时间
	command = r"ls"
	# print_test('Awaiting EIC Decision')
	
	run(interval, command)
	# send_email('test')

