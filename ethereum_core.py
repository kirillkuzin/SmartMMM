import json
import math
import web3
from web3 import Web3, WebsocketProvider
from utils import *
from settings import *

class Ethereum:
    web3 = Web3(WebsocketProvider(INFURA_LINK))

    def __init__(self):
        self.contractAddress = Web3.toChecksumAddress(CONTRACT_ADDRESS)
        with open('smartmmm.json', 'r') as abiDefinition:
            abiStorage = json.load(abiDefinition)
        self.contract = self.web3.eth.contract(
            address = self.contractAddress,
            abi = abiStorage
        )

    def getContractBalance(self, isWei=False):
        address = Web3.toChecksumAddress(CONTRACT_ADDRESS)
        balance = self.web3.eth.getBalance(address)
        if not isWei:
            balance = Web3.fromWei(balance, 'ether')
            balance = correctDecimals(balance)
        return float(balance)

    def getContractUsdtBalance(self, ethBalance):
        ethPrice = getEtherPrice()
        usdtBalance = float(ethBalance) * float(ethPrice)
        return correctDecimals(usdtBalance)

    def getContractDaysAfterStart(self):
        daysAfterStart = self.contract.call().getDaysAfterStart()
        return daysAfterStart

    def getContractInvestedAmount(self):
        investedAmount = self.contract.call().invested()
        investedAmount = Web3.fromWei(investedAmount, 'ether')
        investedAmount = correctDecimals(investedAmount)
        return investedAmount

    def getContractPaymentsAmount(self):
        paymentsAmount = self.contract.call().payments()
        paymentsAmount = float(Web3.fromWei(paymentsAmount, 'ether'))
        paymentsAmount = correctDecimals(paymentsAmount)
        return paymentsAmount

    def getContractInvestorsCount(self):
        investorsCount = self.contract.call().investorsCount()
        return investorsCount

    def getContractPercent(self):
        balance = self.getContractBalance(True)
        percent = self.contract.call().getPercents(int(balance))[0]
        percent /= 100000000000000
        percent *= 1440
        percent = round(percent)
        return percent

    def getWalletDepositInfo(self, wallet):
        try:
            wallet = Web3.toChecksumAddress(wallet)
        except:
            return 0, 0, 0, 0, 0, 0, 0
        else:
            walletDepositInfo = self.contract.call().deposits(wallet)
            investedAmount = correctDecimals(Web3.fromWei(walletDepositInfo[4], 'ether'))
            depositSum = correctDecimals(Web3.fromWei(walletDepositInfo[1], 'ether'))
            cashback = correctDecimals(Web3.fromWei(walletDepositInfo[7], 'ether'))
            referralsLevelOneCount = walletDepositInfo[8]
            referralsLevelTwoCount = walletDepositInfo[9]
            referralPayments = correctDecimals(Web3.fromWei(walletDepositInfo[6], 'ether'))
            paymentsAmount = correctDecimals(Web3.fromWei(walletDepositInfo[5], 'ether'))
            return investedAmount, depositSum, cashback, referralsLevelOneCount, referralsLevelTwoCount, referralPayments, paymentsAmount

    def getReferrerStatus(self, wallet):
        try:
            wallet = Web3.toChecksumAddress(wallet)
            getEtherPrice()
        except Exception as e:
            print(e)
            return 'Не партнер'
        else:
            referrerStatus = self.contract.call().referrers(wallet)
            if referrerStatus:
                return 'Партнер'
            else:
                return 'Не партнер'

import threading
import time

class TxWorker(threading.Thread):
    def __init__(self, ethereum):
        self.ethereum = ethereum
        threading.Thread.__init__(self)

    def run(self):
        previousBlock = 0
        while True:
            txs = self.loadTxs()
            blockNumber = self.ethereum.web3.eth.getBlock('latest')['number']
            if blockNumber != previousBlock:
                try:
                    event = self.ethereum.contract.events.Deposit.createFilter(fromBlock = blockNumber)
                    eventsInfo = event.get_all_entries()
                except:
                    pass
                else:
                    for eventInfo in eventsInfo:
                        transactionHash = str(Web3.toHex(eventInfo['transactionHash']))
                        writed = False
                        for tx in txs:
                            if transactionHash == tx['hash']:
                                writed = True
                        if not writed:
                            tx = {
                                'address': str(eventInfo['args']['from']),
                                'value': str(Web3.fromWei(eventInfo['args']['value'], 'ether')),
                                'hash': transactionHash
                            }
                            if len(txs) < 20:
                                txs = [tx] + txs
                            else:
                                txCached = None
                                for i in range(len(txs) - 1):
                                    if i != 0 and i + 1 <= len(txs) - 1:
                                        nextTxCached = txs[i + 1]
                                        txs[i + 1] = txCached
                                        txCached = nextTxCached
                                    elif i == 0:
                                        txCached = txs[i + 1]
                                        txs[i + 1] = txs[i]
                                txs[0] = tx
                            self.saveTxs(txs)
                    previousBlock = blockNumber

    def saveTxs(self, txs):
        with open('txs.txt', 'w') as txsFile:
            for tx in txs:
                txsFile.write(tx['address'])
                txsFile.write(' ')
                txsFile.write(tx['value'])
                txsFile.write(' ')
                txsFile.write(tx['hash'])
                txsFile.write('\n')

    def loadTxs(self):
        txs = []
        try:
            with open('txs.txt', 'r') as txsFile:
                for line in txsFile:
                    line = line.split('\n')
                    line = line[0].split(' ')
                    address = line[0]
                    amount = line[1]
                    hash = line[2]
                    txs.append({
                        'address': address,
                        'value': amount,
                        'hash': hash
                    })
        except:
            pass
        return txs

class HistoryWorker(threading.Thread):
    def __init__(self, ethereum):
        self.ethereum = ethereum
        threading.Thread.__init__(self)

    def run(self):
        while True:
            timestamp = str(time.time()).split('.')[0]
            timestamp = int(timestamp) * 1000
            try:
                self.updateHistoryFiles(timestamp)
            except:
                pass
            else:
                time.sleep(HISTORY_WAITING_SECONDS)

    def updateHistoryFiles(self, timestamp):
        self.updateBalanceHistory(int(timestamp))
        self.updateInvestorsHistory(int(timestamp))

    def updateBalanceHistory(self, timestamp):
        with open('static/load-eth-history.json', 'r') as balanceFile:
            balanceHistory = balanceFile.read()
        balanceHistory = json.loads(balanceHistory)
        balance = self.ethereum.getContractBalance()
        history = [timestamp, balance]
        balanceHistory.append(history)
        with open('static/load-eth-history.json', 'w') as balanceFile:
            balanceFile.write(json.dumps(balanceHistory))

    def updateInvestorsHistory(self, timestamp):
        with open('static/load-investors-history.json', 'r') as invesotrsFile:
            investorsHistory = invesotrsFile.read()
        investorsHistory = json.loads(investorsHistory)
        investors = self.ethereum.getContractInvestorsCount()
        history = [timestamp, investors]
        investorsHistory.append(history)
        with open('static/load-investors-history.json', 'w') as invesotrsFile:
            invesotrsFile.write(json.dumps(investorsHistory))
