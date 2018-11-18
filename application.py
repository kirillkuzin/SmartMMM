from flask import Flask, request, render_template
from ethereum_core import Ethereum, TxWorker, HistoryWorker

application = Flask(__name__)
ethereum = Ethereum()
txWorker = TxWorker(ethereum)
historyWorker = HistoryWorker(ethereum)
txWorker.setDaemon(True)
txWorker.start()
historyWorker.setDaemon(True)
historyWorker.start()

@application.route('/')
@application.route('/index')
def index():
    wallet = request.args.get('wallet')
    if wallet is None or wallet is ' ' or wallet is '':
        isWallet = False
    else:
        isWallet = True
    contractBalance = ethereum.getContractBalance()
    contractUsdtBalance = ethereum.getContractUsdtBalance(contractBalance)
    contractPercent = ethereum.getContractPercent()
    walletInvestedAmount, walletDepositSum, walletCashback, walletReferralsLevelOneCount, walletReferralsLevelTwoCount, walletReferralPayments, walletPaymentsAmount = ethereum.getWalletDepositInfo(wallet)
    walletAllPayments = float(walletCashback) + float(walletReferralPayments) + float(walletPaymentsAmount)
    walletReferrerStatus = ethereum.getReferrerStatus(wallet)
    return render_template(
        'index.html',
        contractBalance = float(contractBalance),
        contractUsdtBalance = float(contractUsdtBalance),
        contractDaysAfterStart = ethereum.getContractDaysAfterStart(),
        contractInvestedAmount = float(ethereum.getContractInvestedAmount()),
        contractPaymentsAmount = float(ethereum.getContractPaymentsAmount()),
        contractInvestorsCount = ethereum.getContractInvestorsCount(),
        contractPercent = float(contractPercent),
        walletInvestedAmount = float(walletInvestedAmount),
        walletDepositSum = float(walletDepositSum),
        walletCashback = float(walletCashback),
        walletReferrerStatus = walletReferrerStatus,
        walletReferralsLevelOneCount = walletReferralsLevelOneCount,
        walletReferralsLevelTwoCount = walletReferralsLevelTwoCount,
        walletReferralPayments = float(walletReferralPayments),
        walletPaymentsAmount = float(walletPaymentsAmount),
        walletAllPayments = walletAllPayments,
        lastTxs = txWorker.loadTxs(),
        isWallet = isWallet,
        wallet = wallet
    )

if __name__ == '__main__':
    application.run()
