from flask import Flask, request, render_template
from ethereum_core import Ethereum

application = Flask(__name__)
ethereum = Ethereum()

@application.route('/')
@application.route('/index')
def index():
    wallet = request.args.get('wallet')
    contractBalance = ethereum.getContractBalance()
    contractUsdtBalance = ethereum.getContractUsdtBalance(contractBalance)
    walletInvestedAmount, walletDepositSum, walletCashback, walletReferralsLevelOneCount, walletReferralsLevelTwoCount, walletReferralPayments, walletPaymentsAmount = ethereum.getWalletDepositInfo(wallet)
    walletReferrerStatus = ethereum.getReferrerStatus(wallet)
    return render_template(
        'index.html',
        contractBalance = contractBalance,
        contractUsdtBalance = contractUsdtBalance,
        contractDaysAfterStart = ethereum.getContractDaysAfterStart(),
        contractInvestedAmount = ethereum.getContractInvestedAmount(),
        contractPaymentsAmount = ethereum.getContractPaymentsAmount(),
        contractInvestorsCount = ethereum.getContractInvestorsCount(),
        walletInvestedAmount = walletInvestedAmount,
        walletDepositSum = walletDepositSum,
        walletCashback = walletCashback,
        walletReferrerStatus = walletReferrerStatus,
        walletReferralsLevelOneCount = walletReferralsLevelOneCount,
        walletReferralsLevelTwoCount = walletReferralsLevelTwoCount,
        walletReferralPayments = walletReferralPayments,
        walletPaymentsAmount = walletPaymentsAmount
    )

if __name__ == '__main__':
    application.debug = True
    application.run()
