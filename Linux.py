import paramiko
from time import *
import os
# 该类连接远程主机
class Linux(object):

    def __init__(self, ip, user, pwd, timeout=30):
        self.ip = ip
        self.user = user
        self.pwd = pwd
        self.timeout = timeout
        self.tran = ''
        self.chuan = ''
        self.try_times = 3

    # 该方法连接远程主机
    def connect(self):
        try:
            connect = paramiko.SSHClient()
            connect.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            connect.connect(hostname=self.ip, port=22, username=self.user, password=self.pwd)
            self.tran = paramiko.Transport(sock=(self.ip, 22))
            self.tran.connect(username=self.user, password=self.pwd)
            self.chuan = self.tran.open_session()
            self.chuan.settimeout(self.timeout)
            self.chuan.get_pty()
            self.chuan.invoke_shell()
            print('连接{0}成功'.format(self.ip))
            return connect
        except Exception as e:
            if self.try_times != 0:
                print('连接{0}失败,进行重试!'.format(self.ip))
                self.try_times -= 1
            else:
                print('重试3次失败,程序结束')
                exit(1)

    # 连接关闭
    def close(self):
        self.chuan.close()
        self.tran.close()

    # 发送要执行的命令
    def send(self, cmd):
        cmd += '\r'
        result = ''
        self.chuan.send(cmd)
        # 回显很长的命令可能执行较久，通过循环分批次取回回显,执行成功返回true,失败返回false
        while True:
            sleep(3)
            ret = self.chuan.recv(65535)
            ret = ret.decode('utf-8')
            result += ret
            return result

    def Java(self, host): #完整的Java环境安装
        connect = host.connect()
        result = host.send('cd /')
        print(result)
        found = input('创建存储环境的文件夹:')
        result = host.send('mkdir ' + found)
        print(result)
        file_name_one = ''
        sftp = paramiko.SFTPClient.from_transport(self.tran)
        for root, dirs, files in os.walk(os.getcwd()):
            print(files)  # 当前路径下所有非目录子文件
            for file_list in files:
                if 'jdk' in file_list:
                    file_name_one += file_list
                    print(os.path.abspath(file_list))
                    break
        sftp.put(file_list, '/' + found + '/' + file_name_one)
        command_one = ['cd ' + found, 'tar -zxvf ' + file_name_one, 'rm -rf ' + file_name_one, 'find /' + found + ' -name jdk']
        for i in command_one:
            sleep(3)
            result = host.send(i)
            print(result)
        file_name_two = ''
        folder = result.replace('find /' + found + ' -name jdk', '').replace('/', '').replace(found, '').strip()
        for i in folder:
            c = len(file_name_two)
            if c != 0:
                if i == 'j':
                    print(file_name_two)
                    break
            file_name_two += i
        sleep(2)
        ambient_value = connect.open_sftp()
        ambient_add = ambient_value.open('/etc/profile','a+')
        print('#java',file=ambient_add)
        print('export JAVA_HOME=/'+found+'/'+file_name_two+'',file=ambient_add)
        print('export CLASSPATH=.:${JAVA_HOME}/jre/lib/rt.jar:${JAVA_HOME}/lib/dt.jar:${JAVA_HOME}/lib/tools.jar',file=ambient_add)
        print('export PATH=$PATH:${JAVA_HOME}/bin',file=ambient_add)
        sleep(2)
        command_two = ['cd /','source /etc/profile','java -version']
        for i in command_two:
            sleep(0.5)
            result = host.send(i)
            print(result)
        if 'Java HotSpot' in result:
            print('Java环境安装完成')
        else:
            print('安装失败')

    def MySQL(self,host):
        connect = host.connect()
        file_name_one = ''
        sftp = paramiko.SFTPClient.from_transport(self.tran)
        for root, dirs, files in os.walk(os.getcwd()):
            print(files)  # 当前路径下所有非目录子文件
            for file_list in files:
                if 'mysql' in file_list:
                    file_name_one += file_list
                    print(os.path.abspath(file_list))
                    break
        sftp.put(file_list, '/usr/local/' + file_name_one)
        command_one = ['cd /', 'cd /usr/local', 'groupadd mysql', 'useradd -r -g mysql mysql', 'tar -zxvf ' + file_name_one,
             'mv ' + file_name_one.replace('.tar.gz', '') + ' mysql', 'mkdir /usr/local/mysql/data',
             'chown -R mysql:mysql /usr/local/mysql', 'chmod -R 755 /usr/local/mysql', 'cd mysql/bin/',
             './mysqld --initialize --user=mysql --datadir=/usr/local/mysql/data --basedir=/usr/local/mysql']
        for i in command_one:
            result = host.send(i)
            print(result)
        # 获取数据库初始化密码
        init_pwd = result[::-1]
        print(init_pwd)
        pwd = ''
        for i in init_pwd:
            if i == ':':
                print('获取成功', pwd)
                break
            pwd += i
        print(pwd[::-1].strip())
        print(host.send('rm -rf etc/my.cnf'))
        ambient_value = connect.open_sftp()
        ambient_add = ambient_value.open('/etc/my.cnf', 'a+')
        content = ['[mysqld]', 'datadir=/usr/local/mysql/data', 'port=3306',
              'sql_mode=NO_ENGINE_SUBSTITUTION,STRICT_TRANS_TABLES', 'symbolic-links=0', 'max_connections=600',
              'innodb_file_per_table=1', 'lower_case_table_names=1', 'character_set_server=utf8']
        for i in content:
            print(i, file=ambient_add)
        command_two = ['/usr/local/mysql/support-files/mysql.server start',
             'ln -s /usr/local/mysql/support-files/mysql.server /etc/init.d/mysql',
             'ln -s /usr/local/mysql/bin/mysql /usr/bin/mysql', 'service mysql restart', 'mysql -u root -p',
             pwd[::-1].strip(), "set password for root@localhost = password('root');", 'use mysql;',
             "update user set user.Host='%' where user.User='root';", 'flush privileges;']
        for i in command_two:
            print(host.send(i))
        print('rm -rf '+file_name_one)
        sleep(3)

if __name__ == '__main__':
    pass

#自动安装完成。。。。上传机制需要改进，现在的上传机制是本地虚拟机，云服务器的没测试过

