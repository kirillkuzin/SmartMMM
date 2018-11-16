import json
import web3
from web3 import Web3
from utils import *
from settings import *

class Ethereum:
    web3 = Web3(Web3.HTTPProvider(INFURA_LINK))

    def __init__(self):
        self.contractAddress = Web3.toChecksumAddress(CONTRACT_ADDRESS)
        with open('smartmmm.json', 'r') as abiDefinition:
            abiStorage = json.load(abiDefinition)
        self.contract = self.web3.eth.contract(
            address = self.contractAddress,
            abi = abiStorage
        )

    def getContractBalance(self):
        address = Web3.toChecksumAddress(CONTRACT_ADDRESS)
        balance = self.web3.eth.getBalance(address)
        balance = Web3.fromWei(balance, 'ether')
        balance = correctDecimals(balance)
        return float(balance)

    def getContractUsdtBalance(self, ethBalance):
        ethPrice = getEtherPrice()
        usdtBalance = float(ethBalance) * float(ethPrice)
        return int(usdtBalance)

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

    def saveTxs(self, txs):
        with open('txs.txt', 'w') as txsFile:
            for tx in txs:
                txsFile.write(tx['address'])
                txsFile.write(' ')
                txsFile.write(tx['value'])
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
                    txs.append({
                        'address': address,
                        'value': amount
                    })
        except:
            pass
        return txs

import threading

class TxWorker(threading.Thread):
    def __init__(self, ethereum):
        self.ethereum = ethereum
        threading.Thread.__init__(self)

    def run(self):
        while True:
            txs = self.ethereum.loadTxs()
            try:
                with open('block.txt', 'r') as blockFile:
                    contractBlock = int(blockFile.read())
            except:
                contractBlock = self.ethereum.web3.eth.getBlock('latest')['number'] - 1
            currentBlock = contractBlock + 1
            # currentBlock = 4429576
            with open('block.txt', 'w') as blockFile:
                blockFile.write(str(currentBlock))
            while currentBlock > contractBlock:
                counter = 0
                block = self.ethereum.web3.eth.getBlock(currentBlock)
                transactions = block.transactions
                for transaction in transactions:
                    if counter < 10:
                        transactionInfo = self.ethereum.web3.eth.getTransaction(transaction)
                        transactionTo = transactionInfo['to']
                        if transactionTo == self.ethereum.contractAddress:
                            transactionValue = transactionInfo['value']
                            tx = {
                                'address': transactionTo,
                                'value': str(Web3.fromWei(transactionValue, 'ether'))
                            }
                            try:
                                txs[counter] = tx
                            except:
                                txs.append(tx)
                            counter += 1
                    else:
                        break
                currentBlock -= 1
            self.ethereum.saveTxs(txs)

import time

class HistoryWorker(threading.Thread):
    def __init__(self, ethereum):
        self.ethereum = ethereum
        threading.Thread.__init__(self)

    def run(self):
        while True:
            timestamp = str(time.time()).split('.')[0]
            self.updateHistoryFiles(timestamp)
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
