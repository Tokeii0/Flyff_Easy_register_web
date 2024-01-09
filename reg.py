from flask import Flask, request, render_template
import pyodbc
import hashlib

# Database connection parameters
server = '127.0.0.1'
database = 'ACCOUNT_DBF'
# Connection string with Windows authentication
conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

app = Flask(__name__)

def get_hashed_pw(pw):
    return hashlib.md5(pw.encode()).hexdigest()

def register_account(account, pw):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    try:
        cursor.execute("USE [ACCOUNT_DBF]")

        cursor.execute("""\
        DECLARE @return_value int
        EXEC @return_value = [dbo].[usp_CreateNewAccount]
            @account = N'{}',
            @pw = N'{}'
        SELECT 'Return Value' = @return_value
        UPDATE account_tbl_detail set m_chLoginAuthority = 'Z'
        """.format(account, get_hashed_pw(pw)))

        # Fetch the result
        result = cursor.fetchone()
        
        print("Return Value:", result[0])

    except Exception as e:
        print("Error:", e)

    finally:
        # Close the connection
        cursor.close()
        conn.commit()  # 提交事务并关闭连接
        conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        account = request.form.get('account')
        pw = request.form.get('pw')
        register_account(account, pw)
        return '注册成功！'
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)