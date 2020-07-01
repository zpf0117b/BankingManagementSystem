from peewee import *

database = MySQLDatabase('lab3', **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': 'localhost', 'port': 3306, 'user': 'root', 'password': '2017678'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class BankClient(BaseModel):
    client_address = CharField(column_name='CLIENT_ADDRESS', null=True)
    client_contact = CharField(column_name='CLIENT_CONTACT')
    client_id_number = CharField(column_name='CLIENT_ID_NUMBER', primary_key=True)
    client_name = CharField(column_name='CLIENT_NAME')
    contactor_email = CharField(column_name='CONTACTOR_EMAIL', null=True)
    contactor_name = CharField(column_name='CONTACTOR_NAME')
    contactor_phone = TextField(column_name='CONTACTOR_PHONE')
    relationship = CharField(column_name='RELATIONSHIP', null=True)

    class Meta:
        table_name = 'bank_client'

class BankName(BaseModel):
    assets = FloatField(column_name='ASSETS')
    bank_city = CharField(column_name='BANK_CITY')
    branch_bank_name = CharField(column_name='BRANCH_BANK_NAME', primary_key=True)

    class Meta:
        table_name = 'bank_name'

class Staff(BaseModel):
    branch_bank_name = ForeignKeyField(column_name='BRANCH_BANK_NAME', field='branch_bank_name', model=BankName)
    staff_address = CharField(column_name='STAFF_ADDRESS', null=True)
    staff_id_number = CharField(column_name='STAFF_ID_NUMBER', primary_key=True)
    staff_name = CharField(column_name='STAFF_NAME')
    staff_phone = CharField(column_name='STAFF_PHONE')
    staff_startdate = DateField(column_name='STAFF_STARTDATE')
    sta_staff_id_number = ForeignKeyField(column_name='STA_STAFF_ID_NUMBER', field='staff_id_number', model='self', null=True)

    class Meta:
        table_name = 'staff'

class Charge(BaseModel):
    branchbankname = ForeignKeyField(column_name='BRANCHBANKNAME', field='branch_bank_name', model=BankName)
    cheque_or_saving = IntegerField(column_name='CHEQUE_OR_SAVING')
    client_id_number = ForeignKeyField(column_name='CLIENT_ID_NUMBER', field='client_id_number', model=BankClient)
    loan_or_account = IntegerField(column_name='LOAN_OR_ACCOUNT')
    staff_id_number = ForeignKeyField(column_name='STAFF_ID_NUMBER', field='staff_id_number', model=Staff)

    class Meta:
        table_name = 'charge'
        indexes = (
            (('client_id_number', 'branchbankname', 'cheque_or_saving'), True),
            (('client_id_number', 'staff_id_number', 'loan_or_account', 'cheque_or_saving'), True),
        )
        primary_key = CompositeKey('cheque_or_saving', 'client_id_number', 'loan_or_account', 'staff_id_number')

class Cheque(BaseModel):
    account_number = CharField(column_name='ACCOUNT_NUMBER', primary_key=True)
    branch_bank_name = ForeignKeyField(column_name='BRANCH_BANK_NAME', field='branch_bank_name', model=BankName)
    open_date = DateField(column_name='OPEN_DATE')
    overdraft = FloatField(column_name='OVERDRAFT')
    remaining_sum = FloatField(column_name='REMAINING_SUM')

    class Meta:
        table_name = 'cheque'

class Loan(BaseModel):
    branch_bank_name = ForeignKeyField(column_name='BRANCH_BANK_NAME', field='branch_bank_name', model=BankName)
    issue_now_amount = FloatField(column_name='ISSUE_NOW_AMOUNT')
    issue_overall_amount = FloatField(column_name='ISSUE_OVERALL_AMOUNT')
    loan_number = CharField(column_name='LOAN_NUMBER', primary_key=True)

    class Meta:
        table_name = 'loan'

class Lend(BaseModel):
    client_id_number = ForeignKeyField(column_name='CLIENT_ID_NUMBER', field='client_id_number', model=BankClient)
    loan_number = ForeignKeyField(column_name='LOAN_NUMBER', field='loan_number', model=Loan)

    class Meta:
        table_name = 'lend'
        indexes = (
            (('loan_number', 'client_id_number'), True),
        )
        primary_key = CompositeKey('client_id_number', 'loan_number')

class Payments(BaseModel):
    loan_number = ForeignKeyField(column_name='LOAN_NUMBER', field='loan_number', model=Loan)
    pay_amount = FloatField(column_name='PAY_AMOUNT')
    pay_date = DateField(column_name='PAY_DATE')

    class Meta:
        table_name = 'payments'
        indexes = (
            (('loan_number', 'pay_date', 'pay_amount'), True),
        )
        primary_key = CompositeKey('loan_number', 'pay_amount', 'pay_date')

class PossessCheque(BaseModel):
    account_number = ForeignKeyField(column_name='ACCOUNT_NUMBER', field='account_number', model=Cheque)
    client_id_number = ForeignKeyField(column_name='CLIENT_ID_NUMBER', field='client_id_number', model=BankClient)
    last_visit_cheque_date = DateField(column_name='LAST_VISIT_CHEQUE_DATE', null=True)

    class Meta:
        table_name = 'possess_cheque'
        indexes = (
            (('account_number', 'client_id_number'), True),
        )
        primary_key = CompositeKey('account_number', 'client_id_number')

class Saving(BaseModel):
    account_number = CharField(column_name='ACCOUNT_NUMBER', primary_key=True)
    branch_bank_name = ForeignKeyField(column_name='BRANCH_BANK_NAME', field='branch_bank_name', model=BankName)
    currency = CharField(column_name='CURRENCY')
    interest_rate = FloatField(column_name='INTEREST_RATE', null=True)
    open_date = DateField(column_name='OPEN_DATE')
    remaining_sum = FloatField(column_name='REMAINING_SUM')

    class Meta:
        table_name = 'saving'

class PossessSaving(BaseModel):
    account_number = ForeignKeyField(column_name='ACCOUNT_NUMBER', field='account_number', model=Saving)
    client_id_number = ForeignKeyField(column_name='CLIENT_ID_NUMBER', field='client_id_number', model=BankClient)
    last_visit_saving_date = DateField(column_name='LAST_VISIT_SAVING_DATE', null=True)

    class Meta:
        table_name = 'possess_saving'
        indexes = (
            (('client_id_number', 'account_number'), True),
        )
        primary_key = CompositeKey('account_number', 'client_id_number')

