import paramiko
import logging


logging.basicConfig(format=' %(asctime)s - %(levelname)s - %(message)s', \
                    level = logging.DEBUG,filename = 'q2.logs', filemode = 'a')

def write_in_file(data):
    """Function to write data in file

    Args:
        data (string): Data to be written in file
    """
    logging.info("Executing write_in_file function")
    try:
        with open("external_file.txt","w") as f:
            f.write(data)
    except Exception as e:
        logging.info("Exception in write_in_file: "+str(e))

def login(host,username,password,command):
    """Function to ssh on Server and execute command

    Args:
        host (string): Host to login on
        username (string): Username to login on host
        password (string): Password to login on host
    """
    logging.info("Executing login function for: host:%s, username:%s, password:%s" %(str(host),str(username),str(password)))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, 22, username, password)
        stdin, stdout, stderr = ssh.exec_command(command)
        lines = stdout.readlines()
        lines=' '.join(lines)
        write_in_file(lines)

    except Exception as e:
        logging.info("Exception in login function: %s"%str(e))


def file_transfer_to_server(host,username,password,source,destination):
    """FUnction to transfer file to server

    Args:
        host (string): Host to login on
        username (string): Username to login on host
        password (string): Password to login on host
        source (str): source file path
        destination (str): destination file path
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=22, username=username,password=password)
        sftp = ssh.open_sftp()

        sftp.put(source, destination)
        sftp.close()
        ssh.close()


    except Exception as e:
        logging.info("Error in file_transfer_to_server: "+str(e))

    
## Example Execution

#execution of file transfer function
file_transfer_to_server('192.168.0.1','username','password','/root/q1/test.txt','/root/test/test.txt')

#execution of login function to execute hostname command
login('192.168.0.1','username','password','hostname')