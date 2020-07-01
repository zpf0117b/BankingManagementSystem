### 配置步骤

1. ###### 运行环境配置

   安装virtualenv

   ```
   IF Windows(Administrator identity required):
     pip install virtualenv
   ELIF Ubuntu/MacOS:
     sudo apt-get install virtualenv
   ```

   创建新文件夹，创建Python虚拟环境

   ```
   mkdir newproj
   cd newproj
   virtualenv venv
   ```

   激活虚拟环境

   ```
   IF Windows(Administrator identity required):
     venv\Scripts\activate
   ELIF Ubuntu/MacOS:
     venv/bin/activate
   ```

2. ###### 将bank目录放在newproj目录下，安装依赖包与数据库驱动

   ```
   [place directory 'bank' into /newproj]
   cd bank
   pip install -r requirements.txt
   pip install pymysql
   ```

3. ###### 数据库开启

   打开并测试数据库连接

   将/bank/static/lab3.sql放入数据库中执行，生成数据库lab3

4. ###### 连接程序与数据库

   可使用现有的/bank/database/model.py，但需将其中的[database], [user], [password]更换为自己的数据库、用户名、密码(为保留隐私，这里略去本人的相应信息)

   ```
   database = MySQLDatabase('[database]', **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT','use_unicode': True, 'host': 'localhost', 'port': 3306, 'user': '[user]', 'password': '[password]'})
   ```

   或者可以自行生成并配置(同样需将其中的[database], [user], [password]更换为自己的数据库、用户名、密码)：

   ```
   cd database 
   python -m pwiz -e mysql -H 'localhost' -p 3306 -u '[user]' -P '[password]' [database] > model.py
   [由于生成的.py文件以UTF-16方式编码，因此为了适配大多数应用与浏览器，需找一个强大的编辑器(如VSCode)，将其以UTF-8的方式保存，匹配我们的程序]
   cd ..
   ```

5. ###### 运行

   执行：

   ```
   python app.py
   ```

   程序运行在 http://127.0.0.1:5000/ , 长按CTRL+点击终端中的输出即可访问

6. ###### 结束

   使用完毕后，退出应用

   `CTRL+C`结束运行

   结束应用运行后，关闭数据库连接

   `deactivate`关闭虚拟环境