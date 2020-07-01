/*==============================================================*/
/* DBMS name:      MySQL 5.0                                    */
/* Created on:     6/26/2020 11:49:02 PM                        */
/*==============================================================*/
drop database if exists lab3;
create database lab3;
use lab3;


/*==============================================================*/
/* Table: BANK_CLIENT                                           */
/*==============================================================*/
create table BANK_CLIENT
(
   CLIENT_ID_NUMBER     char(12) not null  comment '',
   CLIENT_NAME          varchar(128) not null  comment '',
   CLIENT_CONTACT       char(11) not null  comment '',
   CLIENT_ADDRESS       varchar(1024)  comment '',
   CONTACTOR_NAME       varchar(128) not null  comment '',
   CONTACTOR_PHONE      longtext not null  comment '',
   CONTACTOR_EMAIL      varchar(128)  comment '',
   RELATIONSHIP         varchar(64)  comment '',
   primary key (CLIENT_ID_NUMBER)
)
charset = UTF8MB4;

/*==============================================================*/
/* Table: BANK_NAME                                             */
/*==============================================================*/
create table BANK_NAME
(
   BANK_CITY            varchar(128) not null  comment '',
   BRANCH_BANK_NAME     varchar(128) not null  comment '',
   ASSETS               float not null  comment '',
   primary key (BRANCH_BANK_NAME)
)
charset = UTF8MB4;

/*==============================================================*/
/* Table: CHARGE                                                */
/*==============================================================*/
create table CHARGE
(
   CLIENT_ID_NUMBER     char(12) not null  comment '',
   STAFF_ID_NUMBER      char(12) not null  comment '',
   BRANCHBANKNAME       varchar(128) not null  comment '',
   LOAN_OR_ACCOUNT      int not null  comment '',
   CHEQUE_OR_SAVING     int not null  comment '',
   primary key (CLIENT_ID_NUMBER, STAFF_ID_NUMBER, LOAN_OR_ACCOUNT, CHEQUE_OR_SAVING),
   unique key UK_BBN_CHARGE_BRANCH (CLIENT_ID_NUMBER, BRANCHBANKNAME, CHEQUE_OR_SAVING)
)
charset = UTF8MB4;

alter table CHARGE comment '0 in charge of account,1 in charge of load';

/*==============================================================*/
/* Table: CHEQUE                                                */
/*==============================================================*/
create table CHEQUE
(
   ACCOUNT_NUMBER       char(12) not null  comment '',
   BRANCH_BANK_NAME     varchar(128) not null  comment '',
   REMAINING_SUM        float not null  comment '',
   OPEN_DATE            date not null  comment '',
   OVERDRAFT            float not null  comment '',
   primary key (ACCOUNT_NUMBER)
)
charset = UTF8MB4;

/*==============================================================*/
/* Table: LEND                                                  */
/*==============================================================*/
create table LEND
(
   LOAN_NUMBER          char(12) not null  comment '',
   CLIENT_ID_NUMBER     char(12) not null  comment '',
   primary key (LOAN_NUMBER, CLIENT_ID_NUMBER)
)
charset = UTF8MB4;

/*==============================================================*/
/* Table: LOAN                                                  */
/*==============================================================*/
create table LOAN
(
   LOAN_NUMBER          char(12) not null  comment '',
   BRANCH_BANK_NAME     varchar(128) not null  comment '',
   ISSUE_OVERALL_AMOUNT float not null  comment '',
   ISSUE_NOW_AMOUNT     float not null  comment '',
   primary key (LOAN_NUMBER)
)
charset = UTF8MB4;

/*==============================================================*/
/* Table: PAYMENTS                                              */
/*==============================================================*/
create table PAYMENTS
(
   LOAN_NUMBER          char(12) not null  comment '',
   PAY_DATE             date not null  comment '',
   PAY_AMOUNT           float not null  comment '',
   primary key (LOAN_NUMBER, PAY_DATE, PAY_AMOUNT)
)
charset = UTF8MB4;

/*==============================================================*/
/* Table: POSSESS_CHEQUE                                        */
/*==============================================================*/
create table POSSESS_CHEQUE
(
   ACCOUNT_NUMBER       char(12) not null  comment '',
   CLIENT_ID_NUMBER     char(12) not null  comment '',
   LAST_VISIT_CHEQUE_DATE date  comment '',
   primary key (ACCOUNT_NUMBER, CLIENT_ID_NUMBER)
)
charset = UTF8MB4;

/*==============================================================*/
/* Table: POSSESS_SAVING                                        */
/*==============================================================*/
create table POSSESS_SAVING
(
   CLIENT_ID_NUMBER     char(12) not null  comment '',
   ACCOUNT_NUMBER       char(12) not null  comment '',
   LAST_VISIT_SAVING_DATE date  comment '',
   primary key (CLIENT_ID_NUMBER, ACCOUNT_NUMBER)
)
charset = UTF8MB4;

/*==============================================================*/
/* Table: SAVING                                                */
/*==============================================================*/
create table SAVING
(
   ACCOUNT_NUMBER       char(12) not null  comment '',
   BRANCH_BANK_NAME     varchar(128) not null  comment '',
   REMAINING_SUM        float not null  comment '',
   OPEN_DATE            date not null  comment '',
   INTEREST_RATE        float  comment '',
   CURRENCY             varchar(16) not null  comment '',
   primary key (ACCOUNT_NUMBER)
)
charset = UTF8MB4;

/*==============================================================*/
/* Table: STAFF                                                 */
/*==============================================================*/
create table STAFF
(
   STAFF_ID_NUMBER      char(12) not null  comment '',
   STA_STAFF_ID_NUMBER  char(12)  comment '',
   BRANCH_BANK_NAME     varchar(128) not null  comment '',
   STAFF_NAME           varchar(128) not null  comment '',
   STAFF_PHONE          char(11) not null  comment '',
   STAFF_ADDRESS        varchar(1024)  comment '',
   STAFF_STARTDATE      date not null  comment '',
   primary key (STAFF_ID_NUMBER)
)
charset = UTF8MB4;

alter table CHARGE add constraint FK_CHARGE_CHARGE_BANK_CLI foreign key (CLIENT_ID_NUMBER)
      references BANK_CLIENT (CLIENT_ID_NUMBER) on delete cascade;

alter table CHARGE add constraint FK_CHARGE_CHARGE2_STAFF foreign key (STAFF_ID_NUMBER)
      references STAFF (STAFF_ID_NUMBER);

alter table CHARGE add constraint FK_CHARGE_REFERENCE_BANK_NAM foreign key (BRANCHBANKNAME)
      references BANK_NAME (BRANCH_BANK_NAME);

alter table CHEQUE add constraint FK_CHEQUE_OPENCHEQU_BANK_NAM foreign key (BRANCH_BANK_NAME)
      references BANK_NAME (BRANCH_BANK_NAME);

alter table LEND add constraint FK_LEND_LEND_LOAN foreign key (LOAN_NUMBER)
      references LOAN (LOAN_NUMBER) on delete cascade;

alter table LEND add constraint FK_LEND_LEND2_BANK_CLI foreign key (CLIENT_ID_NUMBER)
      references BANK_CLIENT (CLIENT_ID_NUMBER) on delete cascade;

alter table LOAN add constraint FK_LOAN_ISSUE_BANK_NAM foreign key (BRANCH_BANK_NAME)
      references BANK_NAME (BRANCH_BANK_NAME);

alter table PAYMENTS add constraint FK_PAYMENTS_PAYSUCCES_LOAN foreign key (LOAN_NUMBER)
      references LOAN (LOAN_NUMBER) on delete cascade;

alter table POSSESS_CHEQUE add constraint FK_POSSESS__POSSESS_C_CHEQUE foreign key (ACCOUNT_NUMBER)
      references CHEQUE (ACCOUNT_NUMBER) on delete cascade;

alter table POSSESS_CHEQUE add constraint FK_POSSESS__POSSESS_C_BANK_CLI foreign key (CLIENT_ID_NUMBER)
      references BANK_CLIENT (CLIENT_ID_NUMBER) on delete cascade;

alter table POSSESS_SAVING add constraint FK_POSSESS__POSSESS_S_BANK_CLI foreign key (CLIENT_ID_NUMBER)
      references BANK_CLIENT (CLIENT_ID_NUMBER) on delete cascade;

alter table POSSESS_SAVING add constraint FK_POSSESS__POSSESS_S_SAVING foreign key (ACCOUNT_NUMBER)
      references SAVING (ACCOUNT_NUMBER) on delete cascade;

alter table SAVING add constraint FK_SAVING_OPENSAVIN_BANK_NAM foreign key (BRANCH_BANK_NAME)
      references BANK_NAME (BRANCH_BANK_NAME);

alter table STAFF add constraint FK_STAFF_MANAGER_STAFF foreign key (STA_STAFF_ID_NUMBER)
      references STAFF (STAFF_ID_NUMBER);

alter table STAFF add constraint FK_STAFF_WORK_BANK_NAM foreign key (BRANCH_BANK_NAME)
      references BANK_NAME (BRANCH_BANK_NAME);
      
insert into BANK_NAME (BANK_CITY, BRANCH_BANK_NAME, ASSETS) values
('北京','北京支行',10000000),
('上海','上海支行',10000000),
('合肥','合肥一支行',10000000),
('合肥','合肥二支行',10000000);

insert into STAFF (STAFF_ID_NUMBER,STA_STAFF_ID_NUMBER, BRANCH_BANK_NAME, STAFF_ADDRESS, STAFF_NAME,STAFF_PHONE,STAFF_STARTDATE) values
('ID000000','ID000000', '北京支行', '北京市A街A路A号', '吧啊啊', '86000000000', str_to_date('08/09/2008', '%m/%d/%Y')),
('ID000001','ID000000', '北京支行', '北京市A街A路B号', '把阿炳', '86000000001', str_to_date('08/09/2008', '%m/%d/%Y')),
('ID000002','ID000000', '北京支行', '北京市A街A路C号', '吧啊擦', '86000000002', str_to_date('08/10/2008', '%m/%d/%Y')),
('ID001100','ID001100', '北京支行', '北京市A街B路A号', '巴巴', '86001100000', str_to_date('08/19/2008', '%m/%d/%Y')),
('ID001101','ID001100', '北京支行', '北京市A街B路B号', '八部半', '86001100001', str_to_date('12/09/2008', '%m/%d/%Y')),
('ID110000','ID110000', '上海支行', '上海市A街A路A号', '撒啊啊', '86110000000', str_to_date('11/09/2008', '%m/%d/%Y')),
('ID110001','ID110000', '上海支行', '上海市A街A路B号', 'Saab', '86110000001', str_to_date('02/09/2009', '%m/%d/%Y')),
('ID111100','ID111100', '上海支行', '上海市A街B路A号', '撒把', '86111100000', str_to_date('08/09/2009', '%m/%d/%Y')),
('ID111101','ID111100', '上海支行', '上海市A街B路B号', '萨博吧', '86111100001', str_to_date('10/10/2009', '%m/%d/%Y')),
('ID220000','ID220000', '合肥一支行', '合肥市A街A路A号', '哈啊啊', '86220000000', str_to_date('12/09/2009', '%m/%d/%Y')),
('ID220001','ID220000', '合肥一支行', '合肥市A街A路B号', '哈啊不', '86220000001', str_to_date('01/09/2009', '%m/%d/%Y')),
('ID221100','ID221100', '合肥一支行', '合肥市A街B路A号', '哈巴', '86221100000', str_to_date('02/10/2009', '%m/%d/%Y')),
('ID221101','ID221100', '合肥一支行', '合肥市A街B路B号', '哈比比', '86221100001', str_to_date('08/29/2010', '%m/%d/%Y')),
('ID222200','ID222200', '合肥一支行', '合肥市A街C路A号', '哈擦', '86222200000', str_to_date('06/05/2010', '%m/%d/%Y')),
('ID222201','ID222200', '合肥一支行', '合肥市A街C路B号', '哈擦不', '86222200001', str_to_date('01/04/2011', '%m/%d/%Y')),
('ID330000','ID330000', '合肥二支行', '合肥市B街A路A号', '好吧啊', '86330000000', str_to_date('07/02/2011', '%m/%d/%Y')),
('ID330001','ID330000', '合肥二支行', '合肥市B街A路B号', '海拔表', '86330000001', str_to_date('08/25/2012', '%m/%d/%Y')),
('ID330002','ID330000', '合肥二支行', '合肥市B街A路C号', '后拔出', '86330000002', str_to_date('09/03/2012', '%m/%d/%Y'))