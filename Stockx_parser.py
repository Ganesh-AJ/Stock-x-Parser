import requests, csv, json, time

def writer(data,file):
	f = open(file,'a+')
	f.write(data+'\n')
	f.close()
	
class StockxParser():
	def __init__(self):
		self.domain = "https://stockx.com"
		self.session = requests.session()
		self.stockx_lvl = '3'   # ENTER YOUR STOCKX LEVEL HERE
		self.ship_cost = '0' #ENTER YOUR SHIPPING FEE WITHOUT THE $ SIGN
		if self.stockx_lvl == '1':
			self.fee = float('0.095')
		elif self.stockx_lvl == '2':
			self.fee == float('0.09')
		elif self.stockx_lvl == '3':
			self.fee = float('0.085')
		elif self.stockx_lvl == '4':
			self.fee = float('0.08')
		self.login()

	def login(self):
		h = {
			'user-agent':			'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
			'content-type':			'application/json',
			'appversion':			'0.1',
			'appos':				'web',
			'x-requested-with':		'XMLHttpRequest',
			'jwt-authorization':	'false',
			'accept':				'*/*',
			'referer':				'https://stockx.com/signup',
			'accept-encoding':		'gzip, deflate, br',
			'accept-language':		'en-GB,en-US;q=0.9,en;q=0.8'
			}

		j = {
				"email": "chirojake@hotmail.com", #Enter your StockX email here
				"password": "Password123" #Replace with your StockX password
			}
		l = self.session.post("https://stockx.com/api/login", headers=h, json=j)
		if l.status_code == 200 and l.json()['Customer']['id'] != None:
			self.customerID = l.json()['Customer']['id']
			self.number = 1
			self.jwtauth = l.headers['jwt-authorization']
			print("Successfully Logged In")
			return self.parse()
		else:
			print("Failed To Login... Please Check Credentials And Try Again")

	def parse(self, currentPage=1):
		h = {
			'appos':						'web',
			'x-requested-with':				'XMLHttpRequest',
			'user-agent':					'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
			'jwt-authorization':			self.jwtauth,
			'appversion':					'0.1',
			'accept':						'*/*',
			'referer':						'https://stockx.com/selling',
			'accept-encoding':				'gzip, deflate, br',
			'accept-language':				'en-GB,en-US;q=0.9,en;q=0.8'
			}
		url = "{}/api/customers/{}/selling/history?sort=matched_with_date&order=DESC&limit=20&page={}".format(self.domain, self.customerID, currentPage)
		history = self.session.get(url, headers=h)

		for items in history.json()['PortfolioItems']:
			sellprice = int(items['amount'])
			retail = items['purchasePrice']
			selldate = items['matchedWithDate'].split('T')[0]
			UPS_tracking = items['Tracking']['number']
			product_name = items['product']['title']
			SKU = items['product']['styleId']
			size = items['product']['shoeSize']
			payout = int(sellprice * (1 - self.fee - 0.03))
			profit = float(payout) - float(retail)
			data = '{},{},{},{},{},{},{},{},{}'.format(self.number, product_name, SKU, size, selldate, retail, sellprice, profit, UPS_tracking)
			writer(data, 'Stockx_Sales - {}.csv'.format(time.strftime('%b %d %Y')))
			print("{}. - Parsing Complete, Sales Records Pushed To File".format(self.number))
			self.number += 1
		if history.json()['Pagination']['lastPage'] == 0:
			return self.parse(currentPage + 1)


if __name__ == "__main__":
	print("@Chirojake -- StockxParser")
	StockxParser()