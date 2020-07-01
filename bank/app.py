from flask import Flask, request, render_template, Response, url_for, redirect, abort, Request, g
# Cache
from flask_caching import Cache
from database import operate
from time import sleep
# stupid autopep8
app = Flask(__name__)
# tell Flask to use the above defined config
app.config.from_mapping({
  "DEBUG": True,
  "CACHE_TYPE": "simple",  # not really thread safe
  "CACHE_DEFAULT_TIMEOUT": 300000  # set the timeout = 50min
})
cache = Cache(app)
# set directly after getting value from forms
# get and use immediately

@app.route('/', methods=['POST', 'GET'])
def main_router():
  if request.method == 'POST':
    pass
  else:
    # banks: select  rows: 支行名 所在城市 资产
    # banks = [['b0', 'b0', 'b0'], ['b1', 'b1', 'b1']]
    overall = operate.Overall(branch_name=None)
    msg, banks = overall.get_overall_bank()
    if msg != 'success':
      prompt_message = '获取银行信息出错'
      return render_template("main.html", banks=banks, prompt_message=prompt_message)
    cacheprompt_message = cache.get('prompt_message')

    if request.referrer is None or cacheprompt_message is None:
      prompt_message = ''
    else:
    # unknown error, contact designer to fix bug
      if cacheprompt_message[0]:
        prompt_message = cacheprompt_message[1]
        cache.set('prompt_message', [False, prompt_message])
      else:
        prompt_message = ''
    return render_template("main.html", banks=banks, prompt_message=prompt_message)


@app.route('/branch', methods=['POST', 'GET'])
def branch():
  if request.method == 'POST':
    if request.form.get(key='branchselect') == '':
      return redirect(url_for('main_router'))
      # GET
    else:
      branch_name = request.form.get(key='branchselect')
      cache.set('branch_name', branch_name)
      overall = operate.Overall(branch_name)
      msg1, client = overall.get_overall_client()
      msg2, account = overall.get_overall_account()
      msg3, loan = overall.get_overall_loan()
      # cache.set() you can just cache branch_name
      if msg1 != 'success' or msg2 != 'success' or msg3 != 'success':
        prompt_message = '获取' + str(branch_name) + '支行信息出错'
        cache.set('prompt_message', [True, prompt_message])
        return redirect(url_for('main_router'))
      return render_template("branch.html", branch_name=branch_name, branch_prompt_msg='', client=client, account=account, loan=loan)
  else:
    if request.referrer is None:
      return redirect(url_for('main_router'))
    branch_name = cache.get('branch_name')
    overall = operate.Overall(branch_name)
    msg1, client = overall.get_overall_client()
    msg2, account = overall.get_overall_account()
    msg3, loan = overall.get_overall_loan()
    if msg1 != 'success' or msg2 != 'success' or msg3 != 'success':
      prompt_message = '获取' + str(branch_name) + '支行信息出错'
      cache.set('prompt_message', [True, prompt_message])
      return redirect(url_for('main_router'))

    cachebranch_prompt_msg = cache.get('branch_prompt_msg')
    if cachebranch_prompt_msg is None:
      branch_prompt_msg = ''
    else:
      if cachebranch_prompt_msg[0]:
        branch_prompt_msg = cachebranch_prompt_msg[1]
        cache.set('branch_prompt_msg', [False, branch_prompt_msg])
      else:
        branch_prompt_msg = ''
    return render_template("branch.html", branch_name=branch_name, branch_prompt_msg=branch_prompt_msg, client=client, account=account, loan=loan)


@app.route('/client', methods=['POST', 'GET'])
def client():
  if request.method == 'POST':
    handle_client = request.form.get(key='clientselect')
    branch_name = cache.get('branch_name')

    if handle_client == '':
      return redirect(url_for('branch'))
    elif handle_client == 'add':
      client_info = ['' for i in range(10)]
      msg = 'add'
    else:
      cache.set('handle_client', handle_client)
      operate_client = operate.ClientOperate(branch_name, handle_client)
      msg, client_info = operate_client.get_client_info()
    print(str(request.path) + '  ' + msg)
    signal = 1 if msg == 'add' else 0

    if msg != 'success' and msg != 'add':
      print(msg)
      branch_prompt_msg = '获取' + str(handle_client) + '信息出错'
      cache.set('branch_prompt_msg', [True, branch_prompt_msg])
      return redirect(url_for('branch'))

    return render_template("client.html", branch_name=branch_name, client_info=client_info, signal=signal)
  else:
    if request.referrer is None:
      return render_template("client.html",branch_name=None, client_info=['' for i in range(10)])
    branch_name = cache.get('branch_name')
    handle_client = cache.get('handle_client')
    operate_client = operate.ClientOperate(branch_name, handle_client)
    msg, client_info = operate_client.get_client_info()
    print(branch_name, msg, handle_client)

    if msg != 'success' and msg != 'add':
      branch_prompt_msg = '获取客户信息出错'
      cache.set('branch_prompt_msg', [True, branch_prompt_msg])
      return redirect(url_for('branch'))

    return render_template("client.html", branch_name=branch_name, client_info=client_info, signal=0)


@app.route('/account', methods=['POST', 'GET'])
def account():
  if request.method == 'POST':
    handle_account = request.form.get(key='accountselect')
    branch_name = cache.get('branch_name')
    if handle_account == '':
      return redirect(url_for('branch'))
    elif handle_account == 'add':
      account_info = ['' for i in range(6)]
      cheque_or_saving = 0
      client_in_account = []
      overall = operate.Overall(branch_name)
      # infer, all clients
      msg, client_notin_account = overall.get_overall_client()
      for row in client_notin_account:
        # important, for consistency
        row[0], row[1] = row[1], row[0]
    else:
      cache.set('handle_account', handle_account)
      operate_account = operate.AccountOperate(branch_name, handle_account)
      # -1: saving, 1: cheque; 0: add
      msg, account_info, cheque_or_saving, client_in_account, client_notin_account = operate_account.get_account_info()
    print(str(request.path) + '  ' + msg)

    if msg != 'success' and msg != 'add':
      print(msg)
      branch_prompt_msg = '获取' + str(handle_account) + '信息出错'
      cache.set('branch_prompt_msg', [True, branch_prompt_msg])
      return redirect(url_for('branch'))

    return render_template("account.html", branch_name=branch_name, account_info=account_info, client_in_account=client_in_account, client_notin_account=client_notin_account, cheque_or_saving=cheque_or_saving)
  else:
    if request.referrer is None:
      return render_template("account.html",branch_name=None, account_info=['' for i in range(6)], cheque_or_saving=2)
    branch_name = cache.get('branch_name')
    handle_account = cache.get('handle_account')
    operate_account = operate.AccountOperate(branch_name, handle_account)
    msg, account_info, cheque_or_saving, client_in_account, client_notin_account = operate_account.get_account_info()
    print(branch_name, msg, handle_account)

    if msg != 'success' and msg != 'add':
      branch_prompt_msg = '获取账户信息出错'
      cache.set('branch_prompt_msg', [True, branch_prompt_msg])
      return redirect(url_for('branch'))

    return render_template("account.html", branch_name=branch_name, account_info=account_info, client_in_account=client_in_account, client_notin_account=client_notin_account, cheque_or_saving=cheque_or_saving)


@app.route('/loan', methods=['POST', 'GET'])
def loan():
  if request.method == 'POST':
    handle_loan = request.form.get(key='loanselect')
    branch_name = cache.get('branch_name')
    if handle_loan == '':
      return redirect(url_for('branch'))
    elif handle_loan == 'add':
      loan_info = ['' for i in range(3)]
      add_loan = True
      overall = operate.Overall(branch_name)
      # infer
      msg, all_client = overall.get_overall_client()
      client_in_loan = []
      loan_payments = ['', '', '']
    else:
      cache.set('handle_loan', handle_loan)
      operate_loan = operate.LoanOperate(branch_name, handle_loan)
      # infer
      msg, loan_info, client_in_loan, loan_payments = operate_loan.get_loan_info()
      add_loan = False
      all_client = []
    print(str(request.path) + '  ' + msg)

    if msg != 'success' and msg != 'add':
      print(msg)
      branch_prompt_msg = '获取' + str(handle_loan) + '信息出错'
      cache.set('branch_prompt_msg', [True, branch_prompt_msg])
      return redirect(url_for('branch'))

    return render_template("loan.html",branch_name=branch_name, loan_info=loan_info, add_loan=add_loan, all_client=all_client,client_in_loan=client_in_loan,loan_payments=loan_payments)
  else:
    if request.referrer is None:
      return render_template("loan.html",branch_name=None, loan_info=None, add_loan=False, all_client=None, client_in_loan=None, loan_payments=None)
    branch_name = cache.get('branch_name')
    handle_loan = cache.get('handle_loan')
    # infer
    operate_loan = operate.LoanOperate(branch_name, handle_loan)
    # infer
    msg, loan_info, client_in_loan, loan_payments = operate_loan.get_loan_info()
    add_loan = False
    all_client = []
    print(str(request.path) + '  ' + msg)

    if msg != 'success' and msg != 'add':
      print(msg)
      branch_prompt_msg = '获取' + str(handle_loan) + '信息出错'
      cache.set('branch_prompt_msg', [True, branch_prompt_msg])
      return redirect(url_for('branch'))

    return render_template("loan.html",branch_name=branch_name, loan_info=loan_info, add_loan=add_loan, all_client=all_client, client_in_loan=client_in_loan, loan_payments=loan_payments)


@app.route('/statistic', methods=['POST', 'GET'])
def statistic():
   if request.method == 'POST':
      start_time = request.form.get(key='starttime')
      sta_select = request.form.get(key='staselect')
      if start_time == '' or sta_select == '':
        return redirect(url_for('branch'))
      branch_name = cache.get('branch_name')

      msg = operate.generate_dateframe(start_time, branch_name, sta_select)
      if msg != 'success' and msg != 'add':
        print(msg)
        branch_prompt_msg = '统计信息出错'
        cache.set('branch_prompt_msg', [True, branch_prompt_msg])
        return redirect(url_for('branch'))
      return render_template("statistic.html")
   else:
      if request.referrer is None:
        return render_template("statistic.html")


@app.route('/operation', methods=['POST', 'GET'])
def operation():
  if request.method == 'POST':
    op = request.form.get(key='opselect')
    if op == '':
      # just handle obvious problem and redirect
      return redirect(request.referrer)
    branch_name = cache.get('branch_name')
    if 'client' in op:
      client_name, client_id, client_phone, client_address, contact_name, relationship, contact_phone, contact_email = request.form.get(
             key='clientname'), request.form.get(key='clientid'), request.form.get(key='clientphone'), request.form.get(key='clientaddress'), request.form.get(key='contactname'), request.form.get(key='relationship'), request.form.get(key='contactphone'), request.form.get(key='contactemail')
      if 'add' in op:
        operate_client = operate.ClientOperate(branch_name, handle_client='')
        msg = operate_client.insert_client_info(
                client_name, client_id, client_phone, client_address, contact_name, relationship, contact_phone, contact_email)
      elif 'delete' in op:
        handle_client = cache.get('handle_client')
        operate_client = operate.ClientOperate(branch_name, handle_client=handle_client)
        msg = operate_client.delete_client()
      elif 'change' in op:
        handle_client = cache.get('handle_client')
        operate_client = operate.ClientOperate(branch_name, handle_client=handle_client)
        msg = operate_client.change_client_info(
                client_name, client_phone, client_address, contact_name, relationship, contact_phone, contact_email)
      else:
        msg = 'operation not found'
        abort(406)
        print(msg)
      if msg != 'success':
        branch_prompt_msg = '出现错误' + str(msg)
        cache.set('branch_prompt_msg', [True, branch_prompt_msg])
    elif 'account' in op:
      if request.form.get(key='accountclient') is None:
        return redirect(request.referrer)
      elif len(request.form.get(key='accountclient')) == 0:
        return redirect(request.referrer)
      handle_account = cache.get('handle_account')
      client_in_account = request.form.getlist('accountclient')
      visit_date = request.form.getlist('visitdate')
      print(client_in_account, visit_date)
      remaining_sum, account_number, open_date, cheque_or_saving, interest_rate, currency, overdraft = request.form.get(key='remainingsum'), request.form.get(
             key='accountnumber'), request.form.get(key='opendate'), request.form.get(key='chequeorsaving'), request.form.get(key='interestrate'), request.form.get(key='currency'), request.form.get(key='overdraft')
      operate_account = operate.AccountOperate(branch_name, handle_account)
      if 'add' in op:
        msg = operate_account.insert_account_info(
                remaining_sum, client_in_account, account_number, open_date, cheque_or_saving, interest_rate, currency, overdraft)
      elif 'delete' in op:
        msg = operate_account.delete_account()
      elif 'change' in op:
        # changing client in account not supported
        msg = operate_account.change_account_info(
                remaining_sum, client_in_account, visit_date, interest_rate, overdraft)
      else:
        msg = 'operation not found'
        abort(406)
        print(msg)
      if msg != 'success':
        branch_prompt_msg = '出现错误' + str(msg)
        cache.set('branch_prompt_msg', [True, branch_prompt_msg])
    elif 'loan' in op:
      handle_loan = cache.get('handle_loan')
      loan_number, overall_issue_amount, overall_issue_time = request.form.get(
             key='loannumber'), request.form.get(key='overallissueamount'), request.form.get(key='overallissuetime')
      add_loan_client, payments_date, payments_amount = request.form.getlist(
             'addloanclient'), request.form.getlist('paymentsdate'), request.form.getlist('paymentsamount')
      operate_loan = operate.LoanOperate(branch_name, handle_loan)
      if 'add' in op:
        if add_loan_client is None:
          return redirect(request.referrer)
        elif len(add_loan_client) == 0:
          return redirect(request.referrer)
        else:
          msg = operate_loan.insert_loan_info(
                loan_number, overall_issue_amount, overall_issue_time, add_loan_client, payments_date, payments_amount)
      elif 'delete' in op:
        msg = operate_loan.delete_loan()
      else:
        msg = 'operation not found'
        abort(406)
      if msg != 'success':
        branch_prompt_msg = '出现错误' + str(msg)
        cache.set('branch_prompt_msg', [True, branch_prompt_msg])

    return redirect(url_for('branch'))
  else:
    return redirect(url_for('main_router'))


if __name__ == '__main__':
  app.run(host="127.0.0.1", port="5000", debug=True)
