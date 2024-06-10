import string
from web3 import *
from web3.middleware import *
from contract_info import *
from flask import *

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

contract = w3.eth.contract(address=address_contract, abi=abi)

app = Flask(__name__)
public_key = ''

@app.route('/', methods=['post','get'])
def login():
    if request.method=='POST':
        global public_key
        public_key = request.form.get('login')
        password = request.form.get('password')
        if not public_key:
            print("Ошибка авторизации: Пустой адрес")
            return render_template('login.html')
        else:
            try:
                check_sum = w3.to_checksum_address(public_key)
                w3.geth.personal.unlock_account(check_sum, password)
                return redirect('/home')
            except Exception as e:
                print(f"\nОшибка авторизации: {e}\n")
                return render_template('login.html', error=str(e))
    return render_template('login.html')

@app.route('/reg', methods=['post','get'])
def reg():
    if request.method=='POST':
        password = request.form.get('password')
        if check_pass(password):
            account = w3.geth.personal.new_account(password)
            message = f"Номер вашего аккаунта: {account}\nВаш пароль {password} . Советую сделать скриншот"
            return render_template('reg.html', message=message)
        else:
            message = "Пароль должен быть больше 12 символов, содержать строчные буквы, числа и спец символы"
            return render_template('reg.html', message=message)
    return render_template('reg.html')

@app.route('/home', methods=['post','get'])
def home():
    accbal = w3.eth.get_balance(public_key)
    accnum = public_key
    conbal = w3.eth.get_balance(address_contract)
    return render_template('home.html', accnum=accnum, accbal=accbal, conbal=conbal, estates=estList(), ads=adList())

@app.route('/crest', methods=['post','get'])
def createEst():
    if request.method == 'POST':
        size = int(request.form.get('size'))
        address = request.form.get('address')
        estype = int(request.form.get('type'))
        try:
            contract.functions.createEstate(size, address, estype).transact({'from': public_key})
            print("заебумба")
        except Exception as e:
            print(f"Ошибка: {e}")
    return redirect('/home')

@app.route('/crad', methods=['post','get'])
def createAd():
    if request.method == 'POST':
        price = int(request.form.get('price'))
        id_estate = int(request.form.get('id'))
        try:
            contract.functions.createAd(price, id_estate, 0).transact({'from': public_key})
            print("заебумба")
        except Exception as e:
            print(f"Ошибка: {e}")
    return redirect('/home')

@app.route('/chngEst', methods=['post','get'])
def chngEst():
    if request.method == 'POST':
        id_estate = int(request.form.get('id'))
        try:
            contract.functions.changeStatusEstate(id_estate).transact({'from': public_key})
            print("заебумба")
        except Exception as e:
            print(f"Ошибка: {e}")
    return redirect('/home')

@app.route('/chngAd', methods=['post','get'])
def chngAd():
    if request.method == 'POST':
        id_estate = int(request.form.get('id-est'))
        id_ad = int(request.form.get('id-ad'))
        try:
            contract.functions.changeStatusAd(id_ad, id_estate).transact({'from': public_key})
            print("заебумба")
        except Exception as e:
            print(f"Ошибка: {e}")
    return redirect('/home')

@app.route('/buy', methods=['post','get'])
def buy():
    if request.method == 'POST':
        id_ad = int(request.form.get('id-ad'))
        try:
            contract.functions.buyEstate(id_ad).transact({'from': public_key})
            print("заебумба")
        except Exception as e:
            print(f"Ошибка: {e}")
    return redirect('/home')

@app.route('/pay', methods=['post','get'])
def pay():
    if request.method == 'POST':
        value = int(request.form.get('value'))
        try:
            contract.functions.pay().transact({'from': public_key,'value': value})
        except Exception as e:
            print(f"Ошибка: {e}")
    return redirect('/home')

@app.route('/withdr', methods=['post','get'])
def withdr():
    if request.method == 'POST':
        value = int(request.form.get('value'))
        try:
            contract.functions.withDraw(value).transact({'from': public_key})
        except Exception as e:
            print(f"Ошибка: {e}")
    return redirect('/home')

def estList():
    EstateType = ['Дом', 'Квартира', 'Лофт']
    try:
        estates = contract.functions.getEstates().call({'from': public_key})
        estat = []
        for est in estates:
            estat.append(f'{est[5]}. Площадь: {est[0]}, адрес: {est[1]}, владелец: {est[2]}, тип: {EstateType[est[3]]}, активно: {est[4]}')
        return estat
    except Exception as e:
        print(f"Ошибка: {e}")
        
def adList():
    adStat = ['Открыто', 'Закрыто']
    try:
        q = contract.functions.getAds().call({'from': public_key})
        ads = []
        for ad in q:
            ads.append(f'{ad[3]}. Владелец: {ad[0]}, цена: {ad[2]}, статус: {adStat[ad[5]]}')
        return ads
    except Exception as e:
        print(f"Ошибка: {e}")

def check_pass(password):
    if len(password) < 12:
        print("Пароль должен быть больше 12 символов")
        return False

    if not any(item.islower() for item in password):
        print("Пароль должен содержать прописные буквы")
        return False
    
    if not any(item.isupper() for item in password):
        print("Пароль должен содержать строчные буквы")
        return False
    
    if not any(item.isdigit() for item in password):
        print("Пароль должен содержать числа")
        return False
    
    if not any(item in string.punctuation for item in password):
        print("Пароль должен содержать спец символы")
        return False
    else:
        return True

if __name__ == '__main__':
    app.run(debug=True)