import sys
from os import path
d = path.dirname(__file__) # 获取当前路径
sys.path.append(d)
from model import BankClient, BankName, Staff, Charge, Cheque, Loan, Lend, Payments, PossessCheque, Saving, PossessSaving, database
from datetime import date, datetime, timedelta
from peewee import DatabaseError, DataError, IntegrityError, InterfaceError, InternalError, NotSupportedError, OperationalError, ProgrammingError, fn, Alias
from random import randint
import pandas as pd
import pandas_profiling as pdp

class ClientOperate(object):
  # return: msg, info
  def __init__(self, branch_name, handle_client):
    self.handle_client = handle_client
    self.branch_name = branch_name

  def get_client_info(self):
    try:
      # query2 = Charge.select(BankClient.client_id_number, BankClient.client_name, Charge.staff_id_number).join(BankClient,
      #   on=(Charge.client_id_number == BankClient.client_id_number)).where(Charge.branchbankname == self.branch_name)
      query = BankClient.select().where(BankClient.client_id_number == self.handle_client).get()
    except Exception as e:
      msg1 = repr(e)
      client_info = ['' for i in range(8)]
    else:
      client_info = [query.client_name, query.client_id_number, query.client_contact, query.client_address, query.contactor_name, query.relationship, query.contactor_phone, query.contactor_email]
      msg1 = 'success'
    finally:
      pass
    client_info.extend(['','',''])
    try:
      query2 = Charge.select().where((Charge.client_id_number == self.handle_client) & (Charge.branchbankname == self.branch_name))
    except Charge.DoesNotExist as e:
      msg2 = 'success'
    except Exception as e:
      msg2 = repr(e)
    else:
      for _query2 in query2:
        if _query2.loan_or_account == 1:
          client_info[10] = _query2.staff_id_number
        elif _query2.loan_or_account == 2:
          # 00: no account or loan ; 2: account; 1: cheque, 2: saving
          if _query2.cheque_or_saving == 1:
            client_info[9] = _query2.staff_id_number
          elif _query2.cheque_or_saving == 2:
            client_info[8] = _query2.staff_id_number
      msg2 = 'success'
    finally:
      pass
    msg = 'success' if msg1 == 'success' and msg2 == 'success' else msg1 + msg2
    return msg, client_info

  def insert_client_info(self, client_name, client_id, client_phone, client_address, contact_name, relationship, contact_phone, contact_email):
    # necessary info complete and valid -> add
    # you cannot use self.handle_client
    if len(client_name) > 20 or '"' in client_name or "'" in client_name or client_id[0:2] != 'ID' or len(client_phone) != 11:
      msg = '用户信息不合法'
    elif len(contact_phone) != 11 or '@' not in contact_email or '"' in contact_name or "'" in contact_name:
      msg = '联系人信息不合法'
    else:
      try:
        client_item = BankClient.create(client_name=client_name, client_id_number=client_id, client_contact=client_phone, client_address=client_address, contactor_name=contact_name, contactor_phone=contact_phone,
            contactor_email=contact_email, relationship=relationship)
      except Exception as e:
        msg = repr(e)
      else:
        try:
          query1 = Staff.select().where(Staff.branch_bank_name == self.branch_name)
        except Exception as e:
          client_item.delete_instance()
          msg = 'no staff, empty bank' + repr(e)
        else:
          choice_staff = randint(0, query1.count() - 1)
          charge_item = Charge.create(branchbankname=self.branch_name, client_id_number=client_id, staff_id_number=query1[choice_staff].staff_id_number,
              loan_or_account=0, cheque_or_saving=0)
          charge_item.save()
          msg = 'success'
      finally:
        print('insert_client_info: ' + msg)
      return msg

  def change_client_info(self, client_name, client_phone, client_address, contact_name, relationship, contact_phone, contact_email):
    # not none and valid -> change
    try:
      # print(client_address)
      # query2 = Charge.select(BankClient.client_id_number, BankClient.client_name, Charge.staff_id_number).join(BankClient,
      #   on=(Charge.client_id_number == BankClient.client_id_number)).where(Charge.branchbankname == self.branch_name)
      query = BankClient.select().where(BankClient.client_id_number == self.handle_client).get()
    except BankClient.DoesNotExist as e:
      msg = 'client id not exist'
    except Exception as e:
      msg = repr(e)
    else:
      msg = 'success'
      # just modify valid info, not raise exception, check whether saved by yourself
      if client_name != '' and len(client_name) < 20 and '"' not in client_name and "'" not in client_name:
        query.client_name = client_name
        try:
          query.save()
        except Exception as e:
          pass
      if client_phone != '' and len(client_phone) == 11:
        query.client_contact = client_phone
        try:
          query.save()
        except Exception as e:
          pass
      if client_address != '':
        query.client_address = client_address
        try:
          query.save()
        except Exception as e:
          pass
      if contact_name != '' and '"' not in contact_name and "'" not in contact_name:
        query.contactor_name = contact_name
        try:
          query.save()
        except Exception as e:
          pass
      if relationship != '':
        query.relationship = relationship
        try:
          query.save()
        except Exception as e:
          pass
      if contact_phone != '' and len(contact_phone) == 11:
        query.contactor_phone = contact_phone
        try:
          query.save()
        except Exception as e:
          pass
      if contact_email != '' and '@' in contact_email:
        query.contactor_email = contact_email
        try:
          query.save()
        except Exception as e:
          pass
    finally:
      print(msg)
    return msg

  def delete_client(self):
    # you can delete -> delete
    try:
      query = Charge.select().where((Charge.client_id_number == self.handle_client) & (Charge.branchbankname == self.branch_name))
      cursor = database.execute(query)
    except Exception as e:
      msg = repr(e)
    else:
      print(cursor.description)
      if cursor.description[0][2] is None:
        try:
          BankClient.delete().where(BankClient.client_id_number == self.handle_client).execute()
        except IntegrityError as e:
          msg = repr(e)
        except Exception as e:
          msg = repr(e)
        else:
          msg = 'success'
        finally:
          pass
      else:
        msg = '客户有账户，不允许删除'
    finally:
      print(msg)
    return msg


class AccountOperate(object):
  # return msg, info
  def __init__(self, branch_name, handle_account):
    self.handle_account = handle_account
    self.branch_name = branch_name

  def get_account_info(self):
    # msg, account_info, cheque_or_saving, client_in_account, client_notin_account
    try:
      # query2 = Charge.select(BankClient.client_id_number, BankClient.client_name, Charge.staff_id_number).join(BankClient,
      #   on=(Charge.client_id_number == BankClient.client_id_number)).where(Charge.branchbankname == self.branch_name)
      query1 = Saving.select().where(Saving.account_number == self.handle_account).get()
    except Saving.DoesNotExist as e:
      try:
      # query2 = Charge.select(BankClient.client_id_number, BankClient.client_name, Charge.staff_id_number).join(BankClient,
      #   on=(Charge.client_id_number == BankClient.client_id_number)).where(Charge.branchbankname == self.branch_name)
        query2 = Cheque.select().where(Cheque.account_number == self.handle_account).get()
      except Cheque.DoesNotExist as e:
        msg = '账户信息读取失败'
        cheque_or_saving = 0
        client_in_account = [['', '']]
        client_notin_account = [['']]
        account_info = ['' for i in range(7)]
      except Exception as e:
        msg = repr(e)
        cheque_or_saving = 0
        client_in_account = [['', '']]
        client_notin_account = [['']]
        account_info = ['' for i in range(7)]
      else:
        account_info = [query2.account_number, '支票账户', query2.open_date, query2.remaining_sum, query2.overdraft, '', '']
        cheque_or_saving = 1
        client_in_account = []
        client_notin_account = []
        # SELECT PossessCheque ...
        try:
          query3 = PossessCheque.select().where(PossessCheque.account_number == self.handle_account)
        except PossessCheque.DoesNotExist as e:
          msg = '支票账户信息读取失败'
          cheque_or_saving = 0
          client_in_account.append(['', ''])
          client_notin_account.append([''])
        except Exception as e:
          msg = repr(e)
          cheque_or_saving = 0
          client_in_account.append(['', ''])
          client_notin_account.append([''])
        else:
          for _client in query3:
            client_in_account.append([_client.client_id_number, _client.last_visit_cheque_date])
          try:
            query4 = BankClient.select().where(BankClient.client_id_number.not_in([_client.client_id_number for _client in query3]))
          except BankClient.DoesNotExist as e:
            msg = 'success'
            client_notin_account.append([''])
          except Exception as e:
            msg = repr(e)
            client_notin_account.append([''])
          else:
            for _client2 in query4:
              client_notin_account.append([_client2.client_id_number, ''])
            msg = 'success'
        # SELECT BankClient ... NOT IN
    except Exception as e:
      msg = repr(e)
      cheque_or_saving = 0
      client_in_account = [['', '']]
      client_notin_account = [['']]
      account_info = ['' for i in range(7)]
    else:
      account_info = [query1.account_number, '储蓄账户', query1.open_date, query1.remaining_sum, '', query1.interest_rate, query1.currency]
      cheque_or_saving = -1
      client_in_account = []
      client_notin_account = []
      # SELECT PossessCheque ...
      try:
        query3 = PossessSaving.select().where(PossessSaving.account_number == self.handle_account)
      except PossessSaving.DoesNotExist as e:
        msg = '储蓄账户信息读取失败'
        cheque_or_saving = 0
        client_in_account.append(['', ''])
        client_notin_account.append([''])
      except Exception as e:
        msg = repr(e)
        cheque_or_saving = 0
        client_in_account.append(['', ''])
        client_notin_account.append([''])
      else:
        for _client in query3:
          client_in_account.append([_client.client_id_number, _client.last_visit_saving_date])
        try:
          query4 = BankClient.select().where(BankClient.client_id_number.not_in([_client.client_id_number for _client in query3]))
        except BankClient.DoesNotExist as e:
          msg = 'success'
          client_notin_account.append([''])
        except Exception as e:
          msg = repr(e)
          client_notin_account.append([''])
        else:
          for _client in query4:
            client_notin_account.append([_client.client_id_number, ''])
          msg = 'success'
    finally:
      print(msg)
    print('test',client_in_account, client_notin_account)
    return msg, account_info, cheque_or_saving, client_in_account, client_notin_account

  def insert_account_info(self, remaining_sum, client_in_account, account_number, open_date, cheque_or_saving, interest_rate, currency, overdraft):
    # necessary info complete and valid -> add
    # you cannot use self.handle_client
    # ignore unnecessary info, opendate = visitdate
    # check: one cheque and one saving for one client in one branch
    # Cheque/Saving PossessCheque/PossessSaving random: Charge
    if cheque_or_saving == 'saving':
      if not str(interest_rate).replace('.','0').isdigit() or not str(remaining_sum).replace('.','0').isdigit():
        msg = '储蓄账户信息不合法'
      else:
        # Saving
        try:
          saving_item = Saving.create(account_number=account_number, branch_bank_name=self.branch_name, currency=currency,
                interest_rate=interest_rate, open_date=open_date, remaining_sum=remaining_sum)
        except Exception as e:
          msg = repr(e)
        else:
          # PossessSaving
          try:
            for _client in client_in_account:
              possess_item = PossessSaving.create(account_number=account_number, client_id_number=_client, last_visit_saving_date=open_date)
          except IntegrityError as e:
            saving_item.delete_instance()
            msg = '数据插入出错'
            print(repr(e))
          except Exception as e:
            saving_item.delete_instance()
            msg = repr(e)
          else:
            # Charge
            try:
              possess_charge = {}
              for _client2 in client_in_account:
                try:
                  query1 = Charge.select().where((Charge.branchbankname == self.branch_name) & (Charge.client_id_number == _client2) &
                      (Charge.loan_or_account == 0)).get()
                except Exception as e:
                  saving_item.delete_instance()
                  msg = repr(e)
                else:
                # previous account
                  charge_item = Charge.create(branchbankname=self.branch_name, client_id_number=_client2, staff_id_number=query1.staff_id_number,
                        loan_or_account=2, cheque_or_saving=2)
                  possess_charge[_client2] = charge_item
            except IntegrityError as e:
              for _client3 in possess_charge.keys():
                possess_charge[_client3].delete_instance()
              saving_item.delete_instance()
              msg = '唯一键检查出错'
              print(repr(e))
            except Exception as e:
              for _client4 in possess_charge.keys():
                possess_charge[_client4].delete_instance()
              saving_item.delete_instance()
              msg = repr(e)
              print(repr(e))
            else:
              try:
                query3 = BankName.select().where(BankName.branch_bank_name == self.branch_name).get()
                query3.assets += float(remaining_sum)
                query3.save()
              except Exception as e:
                for _client4 in possess_charge.keys():
                  possess_charge[_client4].delete_instance()
                saving_item.delete_instance()
                msg = repr(e)
                print(repr(e))
              else:
                msg = 'success'
        finally:
          print('insert_saving_info: ' + msg)
      return msg
    else:
      if not str(overdraft).replace('.','0').isdigit() or not str(remaining_sum).replace('.','0').isdigit():
        msg = '支票账户信息不合法'
      else:
        # Saving
        try:
          cheque_item = Cheque.create(account_number=account_number, branch_bank_name=self.branch_name, overdraft=overdraft,
                open_date=open_date, remaining_sum=remaining_sum)
        except Exception as e:
          msg = repr(e)
        else:
          # PossessSaving
          try:
            for _client in client_in_account:
              possess_item = PossessCheque.create(account_number=account_number, client_id_number=_client, last_visit_cheque_date=open_date)
          except IntegrityError as e:
            cheque_item.delete_instance()
            msg = '数据插入出错'
            print(repr(e))
          except Exception as e:
            cheque_item.delete_instance()
            msg = repr(e)
          else:
            # Charge
            try:
              possess_charge = {}
              for _client2 in client_in_account:
                try:
                  query1 = Charge.select().where((Charge.branchbankname == self.branch_name) & (Charge.client_id_number == _client2) &
                      (Charge.loan_or_account == 0)).get()
                except Exception as e:
                  cheque_item.delete_instance()
                  msg = repr(e)
                else:
                  charge_item = Charge.create(branchbankname=self.branch_name, client_id_number=_client2, staff_id_number=query1.staff_id_number,
                        loan_or_account=2, cheque_or_saving=1)
                  possess_charge[_client2] = charge_item
            except IntegrityError as e:
              for _client3 in possess_charge.keys():
                possess_charge[_client3].delete_instance()
              cheque_item.delete_instance()
              msg = '唯一键检查出错'
              print(repr(e))
            except Exception as e:
              for _client4 in possess_charge.keys():
                possess_charge[_client4].delete_instance()
              cheque_item.delete_instance()
              msg = repr(e)
            else:
              try:
                query3 = BankName.select().where(BankName.branch_bank_name == self.branch_name).get()
                query3.assets += float(remaining_sum)
                query3.save()
              except Exception as e:
                for _client4 in possess_charge.keys():
                  possess_charge[_client4].delete_instance()
                cheque_item.delete_instance()
                msg = repr(e)
              else:
                msg = 'success'
        finally:
          print('insert_cheque_info: ' + msg)
      return msg

  def change_account_info(self, remaining_sum, client_in_account, visit_date, interest_rate, overdraft):
    # not none and valid -> change
        # not none and valid -> change
    print( remaining_sum, client_in_account, visit_date, interest_rate, overdraft)
    try:
      # query2 = Charge.select(BankClient.client_id_number, BankClient.client_name, Charge.staff_id_number).join(BankClient,
      #   on=(Charge.client_id_number == BankClient.client_id_number)).where(Charge.branchbankname == self.branch_name)
      query1 = Saving.select().where(Saving.account_number == self.handle_account).get()
    except Saving.DoesNotExist as e:
      try:
      # query2 = Charge.select(BankClient.client_id_number, BankClient.client_name, Charge.staff_id_number).join(BankClient,
      #   on=(Charge.client_id_number == BankClient.client_id_number)).where(Charge.branchbankname == self.branch_name)
        query2 = Cheque.select().where(Cheque.account_number == self.handle_account).get()
      except Exception as e:
        msg = repr(e)
      else:
        msg = 'success'
        if str(remaining_sum).replace('.', '0').isdigit() and remaining_sum != '':
          diff = query2.remaining_sum - float(remaining_sum)
          query2.remaining_sum = float(remaining_sum)
          try:
            query2.save()
            query3 = BankName.select().where(BankName.branch_bank_name == self.branch_name).get()
            query3.assets -= float(diff)
            query3.save()
          except Exception as e:
            msg = repr(e)
            print(repr(e))
          else:
            msg = 'success'
        if str(overdraft).replace('.','0').isdigit() and overdraft != '':
          query2.overdraft = float(overdraft)
          try:
            query2.save()
          except Exception as e:
            msg = repr(e)
        i = 0
        for _client in client_in_account:
          if _client != '' and visit_date[i] != '':
            try:
              query4 = PossessCheque.select().where((PossessCheque.client_id_number == _client) & (PossessCheque.account_number == self.handle_account)).get()
            except Exception as e:
              pass
            else:
              query4.last_visit_cheque_date = visit_date[i]
              query4.save()
          i = i + 1
    except Exception as e:
      msg = repr(e)
    else:
      msg = 'success'
      # just modify valid info, not raise exception, check whether saved by yourself
      if str(remaining_sum).replace('.', '0').isdigit() and remaining_sum != '':
        diff = query1.remaining_sum - float(remaining_sum)
        query1.remaining_sum = float(remaining_sum)
        try:
          query1.save()
          query3 = BankName.select().where(BankName.branch_bank_name == self.branch_name).get()
          query3.assets -= float(diff)
          query3.save()
        except Exception as e:
          msg = repr(e)
          print(repr(e))
        else:
          msg = 'success'
      if str(overdraft).replace('.','0').isdigit() and overdraft != '':
        query1.overdraft = float(overdraft)
        try:
          query1.save()
        except Exception as e:
          msg = repr(e)
      i = 0
      for _client in client_in_account:
        if _client != '' and visit_date[i] != '':
          try:
            query4 = PossessSaving.select().where((PossessSaving.client_id_number == _client) & (PossessSaving.account_number == self.handle_account)).get()
          except Exception as e:
            pass
          else:
            query4.last_visit_saving_date = visit_date[i]
            query4.save()
        i = i + 1
    finally:
      print(msg)
    return msg

  def delete_account(self):
    # you can delete -> delete
    try:
      query1 = Saving.select().where(Saving.account_number == self.handle_account).get()
      # cursor1 = database.execute(query1)
    except Saving.DoesNotExist as e:
      try:
        query2 = Cheque.select().where(Cheque.account_number == self.handle_account).get()
        # cursor2 = database.execute(query2)
      except Exception as e:
        msg = repr(e)
      else:
        try:
          # delete cheque
          these_client = PossessCheque.select().where(PossessCheque.account_number == self.handle_account)
          cursor4 = database.execute(these_client)
          try:
            query4 = BankName.select().where(BankName.branch_bank_name == self.branch_name).get()
            query4.assets -= float(query2.remaining_sum)
            query4.save()
          except Exception as e:
            msg = repr(e)
          else:
            Cheque.delete().where(Cheque.account_number == self.handle_account).execute()
        except Exception as e:
          msg = repr(e)
          print(msg)
        else:
          try:
            # if no cheque of this client exists, delete from charge
            for (account_number, client_id_number, last_visit_cheque_date) in cursor4:
              print(account_number, client_id_number, last_visit_cheque_date)
              try:
                query3 = PossessCheque.select().where((PossessCheque.account_number != self.handle_account) & (PossessCheque.client_id_number == client_id_number)).get()
              except PossessCheque.DoesNotExist as e:
                try:
                  q = Charge.delete().where((Charge.client_id_number == client_id_number) & (Charge.branchbankname == self.branch_name) & (Charge.cheque_or_saving == 1)).execute()
                except Exception as e:
                  msg = repr(e)
              except Exception as e:
                msg = repr(e)
              else:
                pass
            # query = Charge.select().where()
            # cursor = database.execute(query)
          except Exception as e:
            msg = repr(e)
          else:
            msg = 'success'
    except Exception as e:
      msg = repr(e)
    else:
      try:
        # delete saving
        these_client = PossessSaving.select().where(PossessSaving.account_number == self.handle_account)
        cursor4 = database.execute(these_client)
        try:
          query4 = BankName.select().where(BankName.branch_bank_name == self.branch_name).get()
          query4.assets -= float(query1.remaining_sum)
          query4.save()
        except Exception as e:
          msg = repr(e)
        else:
          Saving.delete().where(Saving.account_number == self.handle_account).execute()
      except Exception as e:
        msg = repr(e)
      else:
        try:
          # if no cheque of this client exists, delete from charge
          for (account_number, client_id_number, last_visit_saving_date) in cursor4:
            print(account_number, client_id_number, last_visit_saving_date)
            try:
              query3 = PossessSaving.select().where((PossessSaving.account_number != self.handle_account) & (PossessSaving.client_id_number == client_id_number)).get()
            except PossessSaving.DoesNotExist as e:
              try:
                q = Charge.delete().where((Charge.client_id_number == client_id_number) & (Charge.branchbankname == self.branch_name) & (Charge.cheque_or_saving == 2)).execute()
              except Exception as e:
                msg = repr(e)
            except Exception as e:
              msg = repr(e)
            else:
              pass
          # query = Charge.select().where()
          # cursor = database.execute(query)
        except Exception as e:
          msg = repr(e)
        else:
          msg = 'success'
    finally:
      print(msg)
    return msg


class LoanOperate(object):
  # return msg, info
  def __init__(self, branch_name, handle_loan):
    self.handle_loan = handle_loan
    self.branch_name = branch_name

  def get_loan_info(self):
    # return: msg, loan_info, client_in_loan, loan_payments
    try:
      # query2 = Charge.select(BankClient.client_id_number, BankClient.client_name, Charge.staff_id_number).join(BankClient,
      #   on=(Charge.client_id_number == BankClient.client_id_number)).where(Charge.branchbankname == self.branch_name)
      query2 = (Payments.select().where(Payments.loan_number == self.handle_loan))
      query = Loan.select().where(Loan.loan_number == self.handle_loan).get()
    except Exception as e:
      msg = repr(e)
      loan_info = ['' for i in range(3)]
      client_in_loan = []
      loan_payments = ['', '', '']
    else:
      print(query,query2[:])
      loan_info = [query.loan_number, query2.count(), query.issue_overall_amount]
      print(loan_info)
      msg = 'success'
      loan_payments = []
      for row in query2:
        loan_payments.append([row.pay_date, row.pay_amount, 'NO' if row.pay_date.__ge__(date.today()) else 'YES'])
      client_in_loan = []
      try:
        query3 = (Lend.select().where(Lend.loan_number == self.handle_loan))
      except Exception as e:
        msg = repr(e)
      else:
        for row in query3:
          client_in_loan.append(row.client_id_number)
    finally:
      print(msg)
    return msg, loan_info, client_in_loan, loan_payments

  def insert_loan_info(self, loan_number, overall_issue_amount, overall_issue_time, add_loan_client, payments_date, payments_amount):
    # necessary info complete and valid -> add
    # you cannot use self.handle_client
    # ignore unnecessary info, opendate = visitdate
    # check: one cheque and one saving for one client in one branch
    # loan lend payments charge
    if not overall_issue_time.isdigit():
      msg = '贷款信息不符1'
    else:
      overall_issue_time = int(overall_issue_time)
    if overall_issue_time < 1 or not str(overall_issue_amount).replace('.', '0').isdigit() or len(payments_amount) != overall_issue_time or sum([float(payments_amount[i]) for i in range(overall_issue_time)]) != float(overall_issue_amount) or not all([str(x).replace('.', '0').isdigit() for x in payments_amount]):
      print(overall_issue_time, str(overall_issue_amount).replace('.', '0').isdigit())
      print(len(payments_amount) != overall_issue_time)
      print(sum([float(payments_amount[i]) for i in range(overall_issue_time)]) != float(overall_issue_amount) )
      print(all([str(x).replace('.', '0').isdigit() for x in payments_amount]))
      msg = '贷款信息不符'
    else:
      issue_now_amount = sum([float(payments_amount[i]) if datetime.date(datetime.strptime(payments_date[i], '%Y-%m-%d')).__le__(date.today()) else 0 for i in range(overall_issue_time)])
      try:
        loan_item = Loan.create(branch_bank_name=self.branch_name, issue_now_amount=issue_now_amount, issue_overall_amount=float(overall_issue_amount), loan_number=loan_number)
      except Exception as e:
        msg = repr(e)
      else:
      # lend
        try:
          for _client in add_loan_client:
            lend_item = Lend.create(loan_number=loan_number, client_id_number=_client)
        except IntegrityError as e:
          loan_item.delete_instance()
          msg = '数据插入出错'
          print(repr(e))
        except Exception as e:
          loan_item.delete_instance()
          msg = repr(e)
        else:
        # payments
          try:
            for i in range(overall_issue_time):
              payments_item = Payments.create(loan_number=loan_number,pay_amount=float(payments_amount[i]),pay_date=payments_date[i])
          except Exception as e:
            loan_item.delete_instance()
            msg = repr(e)
          else:
            try:
              possess_charge = {}
              for _client2 in add_loan_client:
                try:
                  query1 = Charge.select().where((Charge.branchbankname == self.branch_name) & (Charge.client_id_number == _client2) &
                      (Charge.loan_or_account == 0)).get()
                except Exception as e:
                  loan_item.delete_instance()
                  msg = repr(e)
                else:
                # previous account
                  charge_item = Charge.create(branchbankname=self.branch_name, client_id_number=_client2, staff_id_number=query1.staff_id_number,
                        loan_or_account=1, cheque_or_saving=3)
                  possess_charge[_client2] = charge_item
            except IntegrityError as e:
              for _client3 in possess_charge.keys():
                possess_charge[_client3].delete_instance()
              loan_item.delete_instance()
              msg = '唯一键检查出错'
              print(repr(e))
            except Exception as e:
              for _client4 in possess_charge.keys():
                possess_charge[_client4].delete_instance()
              loan_item.delete_instance()
              msg = repr(e)
              print(repr(e))
            else:
              try:
                query3 = BankName.select().where(BankName.branch_bank_name == self.branch_name).get()
                query3.assets -= issue_now_amount
                query3.save()
              except Exception as e:
                for _client4 in possess_charge.keys():
                  possess_charge[_client4].delete_instance()
                loan_item.delete_instance()
                msg = repr(e)
                print(repr(e))
              else:
                msg = 'success'
      finally:
        print('insert_saving_info: ' + msg)
      print(msg)
    return msg

  def delete_loan(self):
    # you can delete -> delete
    try:
      these_client = Lend.select().where(Lend.loan_number == self.handle_loan)
      cursor4 = database.execute(these_client)
      this_loan = Loan.select().where(Loan.loan_number == self.handle_loan).get()
    except Exception as e:
      msg = repr(e)
    else:
      if this_loan.issue_now_amount == this_loan.issue_overall_amount:
        try:
          Loan.delete().where(Loan.loan_number == self.handle_loan).execute()
        except Exception as e:
          msg = repr(e)
        else:
          msg = 'success'
          for (client_id_number, loan_number) in cursor4:
            print(client_id_number, loan_number)
        # try:
        #   query3 = Lend.select().where((Lend.loan_number != self.handle_loan) & (Lend.client_id_number == client_id_number)).get()
        # except Lend.DoesNotExist as e:
            try:
              q = Charge.delete().where((Charge.client_id_number == client_id_number) & (Charge.branchbankname == self.branch_name) & (Charge.loan_or_account == 1)).execute()
            except Exception as e:
              msg = repr(e)
        # except Exception as e:
        #   msg = repr(e)
        # else:
        #   pass
      else:
        msg = '不允许删除'
    finally:
      print(msg)
    return msg


class Overall(object):
  # return msg, brief info
  def __init__(self, branch_name):
    self.branch_name = branch_name

  def get_overall_bank(self):
    banks = []
    try:
      query = BankName.select()
    except Exception as e:
      msg = repr(e)
    else:
      for branch in query:
        banks.append([branch.branch_bank_name, branch.bank_city, branch.assets])
      msg = 'success'
    finally:
      print(msg)
    return msg, banks

  def get_overall_client(self):
    client = []
    try:
      query = BankClient.select()
    except Exception as e:
      msg = repr(e)
    else:
      for _client in query:
        client.append([_client.client_name, _client.client_id_number, _client.contactor_phone])
      msg = 'success'
    finally:
      print(msg)
    return msg, client

  def get_overall_account(self):
    account = []
    try:
      query1 = Cheque.select()
      query2 = Saving.select()
    except Exception as e:
      msg = repr(e)
    else:
      for chequeA in query1:
        account.append([chequeA.branch_bank_name, chequeA.account_number, '支票'])
      for savingA in query2:
        account.append([savingA.branch_bank_name, savingA.account_number, '储蓄'])
      msg = 'success'
    finally:
      print(msg)
    return msg, account

  def get_overall_loan(self):
    loan = []
    try:
      query = Loan.select()
    except Exception as e:
      msg = repr(e)
    else:
      for _loan in query:
        loan.append(['未开始发放' if _loan.issue_now_amount == 0 else ('发放中' if _loan.issue_now_amount < _loan.issue_overall_amount else '已全部发放'),
          _loan.loan_number, _loan.branch_bank_name])
      msg = 'success'
    finally:
      print(msg)
    return msg, loan


def generate_dateframe(start_time, branch_name, sta_select):
  end_time = date.today()
  timetrial = {'M':pd.Series(pd.period_range(start=(datetime.date(datetime.strptime(start_time, '%Y-%m-%d'))-timedelta(days=31)), freq='M', periods=12)),
          'Q': pd.Series(pd.period_range(start=(datetime.date(datetime.strptime(start_time, '%Y-%m-%d'))-timedelta(days=91)), freq='Q', periods=12)),
          'Y':pd.Series(pd.period_range(start=(datetime.date(datetime.strptime(start_time, '%Y-%m-%d'))-timedelta(days=365)), freq='Y', periods=4))}
  # a = .iloc[i].strftime('%Y-%m-%d')
  # b = datetime.date(datetime.strptime(a, '%Y-%m-%d'))
  # select between
  index = timetrial[sta_select]
  msg = 'success'
  saving_amount = []
  cheque_amount = []
  loan_amount = []
  overall_amount = []
  business = []
  for i in range(len(index)-1):
    time_select = (datetime.date(datetime.strptime(index.iloc[i].strftime('%Y-%m-%d'), '%Y-%m-%d')), datetime.date(datetime.strptime(index.iloc[i + 1].strftime('%Y-%m-%d'), '%Y-%m-%d')))
    new_cheque = [0, 0]
    new_saving = [0, 0]
    new_loan = [0, 0]
    try:
      query3 = Payments.select().where((Payments.pay_date >= time_select[0]) & (Payments.pay_date < time_select[1]))
    except Payments.DoesNotExist as e:
      msg = 'success'
    except Exception as e:
      msg = repr(e)
    else:
      for _loan in query3:
        new_loan[0] += 1
        new_loan[1] -= _loan.pay_amount
      # business.append(new_cheque[0]+new_saving[0]+new_loan[0])
    try:
      query1 = Cheque.select().where((Cheque.open_date >= time_select[0]) & (Cheque.open_date < time_select[1]))
    except Cheque.DoesNotExist as e:
      msg = 'success'
    except Exception as e:
      msg = repr(e)
    else:
      for _cheque in query1:
        new_cheque[0] += 1
        new_cheque[1] += _cheque.remaining_sum
    try:
      query2 = Saving.select().where((Saving.open_date >= time_select[0]) & (Saving.open_date < time_select[1]))
    except Saving.DoesNotExist as e:
      msg = 'success'
    except Exception as e:
      msg = repr(e)
    else:
      for _saving in query2:
        new_saving[0] += 1
        new_saving[1] += _saving.remaining_sum
    saving_amount.append(new_saving[1])
    cheque_amount.append(new_cheque[1])
    loan_amount.append(new_loan[1])
    overall_amount.append(new_cheque[1] + new_loan[1] + new_saving[1])
    business.append(new_cheque[0] + new_loan[0] + new_saving[0])

  rep = pd.DataFrame({'PERIOD':index.head(len(index)-1),'SAVING': saving_amount, 'CHEQUE': cheque_amount, 'LOAN': loan_amount, 'ASSETS': overall_amount, 'BUSINESS': business}, index=index.head(len(index)-1))
  print(rep)
  pdp.ProfileReport(rep).to_file(output_file="./templates/statistic.html")
  return msg