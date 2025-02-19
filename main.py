from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.uix.widget import Widget
from kivy.resources import resource_add_path
from kivy.utils import platform
from kivy.core.window import Window
from kivy.properties import NumericProperty
import japanize_kivy
from kivy.config import Config

import jpholiday
from dateutil.relativedelta import relativedelta
import datetime
import sqlite3
import os


class ScreenMain(BoxLayout):
    def __init__(self, **kwargs):
        super(ScreenMain, self).__init__(**kwargs)
        
	

class Screen_Entry(BoxLayout):
    # 平均回数
	average = 0
	txt_year = ObjectProperty(None)
	txt_month = ObjectProperty(None)
	txt_day = ObjectProperty(None)
	txt_num = ObjectProperty(None)
	lbl_ave = ObjectProperty(None)

	def __init__(self, **kwargs):
		super(Screen_Entry, self).__init__(**kwargs)
		self.set_text()
	
	def set_text(self):
		txt_year = str(datetime.date.today().year)
		txt_month = f"{datetime.date.today().month:02}"
		txt_day = f"{datetime.date.today().day - 1:02}"
		self.txt_day = txt_year + "-" + txt_month + "-" +txt_day
		self.txt_num = str(1)
		self.GetAverage()

	def GetAverage(self):
		print("Ave")
		str_sql = 'SELECT avg(master_num) FROM master_dt'
		# sqliteを操作するカーソルオブジェクトを作成
		cur = conn.cursor()
		cur.execute(str_sql)
		ret = cur.fetchall()
		if ret[0][0] == None:
			self.average = 0
		else:
			self.average = ret[0][0]
		self.lbl_ave = "Average : " + format(self.average, '.5f')

	def EntryClicked(self):
		str_date = self.ids.txt_day.text
		result = self.ids.txt_num.text
		self.DataEntry(str_date, result)
		self.GetAverage()

	def DataEntry(self, date, num):
		str_sql = f"SELECT date, master_num FROM master_dt WHERE date = '{date}'"
		cur = conn.cursor()
		cur.execute(str_sql)
		ret = cur.fetchall()
		# データがなければ新しく追加
		if len(ret) == 0:
			str_sql = "INSERT INTO master_dt (date, master_num) values(" + f"'{date}'" + ", " + f'{num}' + ")"
		# データがあれば更新する
		else:
			str_sql = "UPDATE master_dt SET master_num =" + num + " where date = '" + date + "'"
		cur.execute(str_sql)
		conn.commit()

class Screen_Record(BoxLayout):
	rv = ObjectProperty(None)
	def __init__(self, **kwargs):
		super(Screen_Record, self).__init__(**kwargs)

	def on_enter(self, *args):
		print("GetData")
		self.ids.rv.data = self.setDataInRowForRecicleView()
	
	def get_data(self):
		str_sql = "SELECT date, master_num FROM master_dt ORDER BY date DESC"
		cur = conn.cursor()
		cur.execute(str_sql)
		ret = cur.fetchall()
		return ret
	def setDataInRowForRecicleView(self):
		RVTable = []
		CSVforRecycleView = self.get_data()
		RVTable = [{'day': item[0], 'num': str(item[1])} for item in CSVforRecycleView]
		return RVTable

	def DataRepair(self):
		# データ修正パッチ用
		temp = 1

class MasterLayout(TabbedPanel):
	def __init__(self, **kwargs):
		super(MasterLayout, self).__init__(**kwargs)
	
	def on_release(self):
		sr = self.ids.Screen_Record
		sr.on_enter()

class MoneyLayout(BoxLayout):
	def __init__(self, **kwargs):
		super(MoneyLayout, self).__init__(**kwargs)
    
	def on_release(self):
		sr = self.ids.Screen_Record_Money
		sr.on_enter()
		sr.set_text()

class Screen_Entry_Money(BoxLayout):
	txt_day_money = ObjectProperty(None)
	spn_kind = ObjectProperty(None)
	
	def __init__(self, **kwargs):
		super(Screen_Entry_Money, self).__init__(**kwargs)
		self.set_text()

	def set_text(self):
		txt_year = str(datetime.date.today().year)
		txt_month = f"{datetime.date.today().month:02}"
		txt_day = f"{datetime.date.today().day:02}"
		self.txt_day_money = txt_year + "-" + txt_month + "-" +txt_day

	def get_kind(self):
		inout = self.ids.spn_inout.text
		if inout == '収入':
			str_sql = f"SELECT category FROM mst_category WHERE inout = '収入'"
		elif inout == '支出':
			str_sql = f"SELECT category FROM mst_category WHERE inout = '支出'"
		else:
			str_sql = f"SELECT category FROM mst_category"
		cur = conn.cursor()
		cur.execute(str_sql)
		ret = cur.fetchall()
		result_list = [row[0] for row in ret]
		self.ids.spn_kind.values = result_list
	
	def entry_data(self):
		day = self.ids.txt_day_money.text
		inout = self.ids.spn_inout.text
		category = self.ids.spn_kind.text
		money = self.ids.txt_money_money.text
		freeword = self.ids.txt_free_money.text
		if inout != '収支' and category != 'Kind' and money != '':
			str_sql = "INSERT INTO balance_hist (date, inout, category, price, freeword) values(" + f"'{day}'" + ", "+ f"'{inout}'" + ", "  + f"'{category}'" + ", " + f"{money}" + ", " + f"'{freeword}'" + ")"
			cur = conn.cursor()
			cur.execute(str_sql)
			conn.commit()
			self.ids.spn_inout.text = '収支'
			self.ids.spn_kind.text = 'kind'
			self.ids.txt_money_money.text = ''
			self.ids.txt_free_money.text = ''


class Screen_Record_Money(BoxLayout):
	rv_money = ObjectProperty(None)
	lbl_income = ObjectProperty(None)
	lbl_expense = ObjectProperty(None)
	lbl_sum = ObjectProperty(None)

	def __init__(self, **kwargs):
		super(Screen_Record_Money, self).__init__(**kwargs)
		self.set_text()
    
	def set_text(self):
		if self.get_salary_day() != 'None':
			income = self.get_income_data()
			expense = self.get_expense_data()
			if income == 'None':
				income = 0
			if expense == 'None':
				expense = 0
			sum = self.get_sum_data(int(income), int(expense))
			self.lbl_income = "収入： " + str(income)
			self.lbl_expense = "支出： " + str(expense)
			self.lbl_sum = "合計： " + str(sum)
		else:
			self.lbl_income = "収入： -"
			self.lbl_expense = "支出： -"
			self.lbl_sum = "合計： -"

	def on_enter(self, *args):
		print("GetData")
		self.ids.rv_money.data = self.setDataInRowForRecicleView_Money()

	
	def get_data(self):
		str_sql = "SELECT date, inout, category, price, freeword FROM balance_hist ORDER BY date DESC"
		cur = conn.cursor()
		cur.execute(str_sql)
		ret = cur.fetchall()
		return ret
	def setDataInRowForRecicleView_Money(self):
		RVTable = []
		CSVforRecycleView = self.get_data()
		RVTable = [{'day': item[0], 'inout': str(item[1]), 'category': str(item[2]), 'price': str(item[3]), 'free': str(item[4])} for item in CSVforRecycleView]
		return RVTable

	def get_income_data(self):
		salary_day , next_salary_day = self.get_salary_day()
		str_sql = "SELECT SUM(price) FROM balance_hist WHERE inout = '収入' AND " \
				  "(DATE(date) BETWEEN DATE('" + salary_day + "') AND DATE('" + next_salary_day + "'))"
		cur = conn.cursor()
		cur.execute(str_sql)
		ret = cur.fetchall()
		income = str(ret[0][0])
		return income

	def get_expense_data(self):
		salary_day , next_salary_day = self.get_salary_day()
		str_sql = "SELECT SUM(price) FROM balance_hist WHERE inout = '支出' AND " \
				  "(DATE(date) BETWEEN DATE('" + salary_day + "') AND DATE('" + next_salary_day + "'))"
		cur = conn.cursor()
		cur.execute(str_sql)
		ret = cur.fetchall()
		expense = str(ret[0][0])
		return expense

	def get_sum_data(self, income, expense):
		return str(income - expense)

	def get_salary_day(self):
		str_sql = "SELECT kind_value FROM config_list WHERE kind = 'Salary_day' limit 1"
		cur = conn.cursor()
		cur.execute(str_sql)
		ret = cur.fetchall()
		if len(ret) != 0:
			salary_day = int(ret[0][0])
			now = datetime.datetime.now()
			if salary_day > int(now.day):
				if int(now.month) == 1:
					date_salary_day = datetime.datetime(now.year-1, 12, int(salary_day-1))
				else:
					date_salary_day = datetime.datetime(now.year, int(now.month) - 1, int(salary_day-1))
			else:
				date_salary_day = datetime.datetime(now.year, now.month, int(salary_day-1))
			temp_str_salary_day = date_salary_day.strftime('%Y%m%d')
			str_salary_day = self.returnBizDay(temp_str_salary_day)
			# 来月の給料支給日
			if salary_day > int(now.day):
				date_salary_day_next = (now).replace(day=int(salary_day-1))
			else:
				date_salary_day_next = (now + relativedelta(months=1)).replace(day=int(salary_day-1))
			temp_str_salary_day_next = date_salary_day_next.strftime('%Y%m%d')
			str_salary_day_next = self.returnBizDay(temp_str_salary_day_next)

			return str_salary_day, str_salary_day_next
		else:
			return 'None'

	def returnBizDay(self, DATE):
		Date = datetime.date(int(DATE[0:4]), int(DATE[4:6]), int(DATE[6:8]))
		while Date.weekday() >= 5 or jpholiday.is_holiday(Date):
			Date = datetime.date(Date.year, Date.month, Date.day - 1)
		return Date.strftime("%Y-%m-%d")
    
class Screen_Config_Money(BoxLayout):
	spn_inout = ObjectProperty(None)
	txt_money_kind = ObjectProperty(None)
	txt_SalaryDay_money = ObjectProperty(None)

	def __init__(self, **kwargs):
		super(Screen_Config_Money, self).__init__(**kwargs)

	def DataEntry(self):
		category1 = self.ids.spn_inout2.text
		category2 = self.ids.txt_money_kind.text
		if ((category1 == '支出') or (category1 == '収入')) and category2 != '':
			str_sql = f"SELECT category FROM mst_category WHERE category = '{category2}'"
			cur = conn.cursor()
			cur.execute(str_sql)
			ret = cur.fetchall()
			# データがなければ新しく追加
			if len(ret) == 0:
				str_sql = "INSERT INTO mst_category (inout, category) values(" + f"'{category1}'" + ", " + f"'{category2}'" + ")"
			# データがあれば何もしない
			else:
				str_sql = "SELECT category FROM mst_category WHERE category = '{category2}'"
			cur.execute(str_sql)
			conn.commit()
		else:
			temp = 1
		# 登録後は空白にする
		self.ids.spn_inout2.text = 'inout'
		self.ids.txt_money_kind.text = ''

	def Entry_salary_date(self):
		salary_day = self.ids.txt_SalaryDay_money.text
		if salary_day != '':
			str_sql = f"SELECT kind_value FROM config_list WHERE kind = 'Salary_day'"
			cur = conn.cursor()
			cur.execute(str_sql)
			ret = cur.fetchall()
			# データがなければ新しく追加
			if len(ret) == 0:
				str_sql = "INSERT INTO config_list (kind, kind_value, description) values('Salary_day', " + f"'{salary_day}', " + "'給料日')"
			# データがあれば更新
			else:
				str_sql = "UPDATE config_list SET kind_value =" + salary_day + " where kind = 'Salary_day'"
			cur.execute(str_sql)
			conn.commit()
		else:
			temp = 1
		# 登録後は空白にする
		self.ids.txt_SalaryDay_money.text = ''

class TableRow_Master(RecycleDataViewBehavior, BoxLayout):
    day = ObjectProperty(None)
    num = ObjectProperty(None)
    
class TableRow_Money(RecycleDataViewBehavior, BoxLayout):
    day = ObjectProperty(None)
    inout = ObjectProperty(None)
    category = ObjectProperty(None)
    price = ObjectProperty(None)
    free = ObjectProperty(None)

class MainApp(App):
	font_size = NumericProperty(20)
	def __init__(self, **kwargs):
		super(MainApp, self).__init__(**kwargs)
	
	def build(self):
		print("goDEBUG2")
		return ScreenMain()

	


if __name__=="__main__":
	print("goDEBUG")
	global db_path
	global conn
	if platform == "android":
		db_path = os.environ['ANDROID_PRIVATE'] + '/MASTER.db'
		conn = sqlite3.connect(db_path)
	else:
		db_path = 'MASTER.db'
		# 接続の取得
		conn = sqlite3.connect(db_path)
	# テーブルを作成する 
	conn.execute('''
		CREATE TABLE IF NOT EXISTS master_dt ( 
			id INTEGER PRIMARY KEY AUTOINCREMENT, 
			date TEXT NOT NULL,
			master_num INTEGER NOT NULL
		)
	''')
	conn.execute('''
		CREATE TABLE IF NOT EXISTS mst_category ( 
			id INTEGER PRIMARY KEY AUTOINCREMENT, 
			inout TEXT NOT NULL,
			category TEXT NOT NULL
		)
	''')
	conn.execute('''
		CREATE TABLE IF NOT EXISTS balance_hist ( 
			id INTEGER PRIMARY KEY AUTOINCREMENT, 
			date TEXT NOT NULL,
			inout TEXT NOT NULL,
			category TEXT NOT NULL,
			price INTEGER NOT NULL,
			freeword TEXT
		)
	''')
	conn.execute('''
		CREATE TABLE IF NOT EXISTS config_list ( 
			id INTEGER PRIMARY KEY AUTOINCREMENT, 
			kind TEXT NOT NULL,
			kind_value TEXT NOT NULL,
			description TEXT
		)
	''')
	
	MainApp().run()