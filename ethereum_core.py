import json
import web3
from web3 import Web3
from utils import *
from settings import *

class Ethereum:
    web3 = Web3(Web3.HTTPProvider(INFURA_LINK))
    currencys = ['ether', 'wei', 'gwei']

    def __init__(self):
        contractAddress = Web3.toChecksumAddress(CONTRACT_ADDRESS)
        with open('smartmmm.json', 'r') as abiDefinition:
            abiStorage = json.load(abiDefinition)
        self.contract = self.web3.eth.contract(address = contractAddress, abi = abiStorage)

    def getContractBalance(self):
        address = Web3.toChecksumAddress(CONTRACT_ADDRESS)
        balance = self.web3.eth.getBalance(address)
        balance = Web3.fromWei(balance, 'ether')
        balance = correctDecimals(balance)
        return balance

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
