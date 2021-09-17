
from sys import argv, stderr
from socket import socket, getaddrinfo
from socket import AF_INET, SOCK_STREAM, AI_ADDRCONFIG, AI_PASSIVE
from socket import IPPROTO_TCP, SOL_SOCKET, SO_REUSEADDR
from os import fork
from posix import abort
import arquivo


# Os códigos das funções getEnderecoHost, criaSocket, setModo, bindSockwet , escuta e conecta
# foram retirados dos slides do Prof. Alexande Meslin da disciplina


#pega o endereco do Host
def getEnderecoHost(porta):
    enderecoHost=''
    try:
        enderecoHost = getaddrinfo(None, porta, family=AF_INET, type=SOCK_STREAM,
                                   proto=IPPROTO_TCP, flags=AI_ADDRCONFIG | AI_PASSIVE)
    except:
        print("Não obtive informações sobre o servidor (???)", file=stderr)
        abort()
    return enderecoHost

#cria o socket
def criaSocket(enderecoServidor):
    fd = socket(enderecoServidor[0][0], enderecoServidor[0][1])
    if not fd:
        print("Não consegui criar o socket", file=stderr)
        abort()
    return fd

# define modo do socket
def setModo(fd):
    fd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    return

# Da bind no socket
def bindaSocket(fd, porta):
    try:
        fd.bind(('', porta))
    except:
        print("Erro ao dar bind no socket do servidor", porta, file=stderr)
        abort()
    return

#Escuta o que ta chegando na porta
def escuta(fd):
    try:
        fd.listen(0)
    except:
        print("Erro ao começar a escutar a porta", file=stderr)
        abort()
        print("Iniciando o serviço")
        return

#Conecta servidor cliente
def conecta(fd):
    (con, cliente) = fd.accept()
    print("Servidor conectado com", cliente)
    return con

#pega o request e disponibiliza as infomaçoes
def request(con):
    #recebe as informacoes do request
    request = con.recv(4096).decode("utf-8")
    if not request:
        con.close()
        return

    request = request.splitlines()[0]
    method, path, protocol = request.split(" ")

    if(method!="GET"):
    #Se receber um método que nao for GET
        body=""
        statusCode= '501'
        statusMensage="Método não implementado"
    else:
        try:
            if path=='/':
                #caso nao tenha nada sendo pedido depois da barra, abre o index.html
                with open('./view/index.html', 'rb') as f:
                    body = f.read()

            else:
                #caso algo estaja sendo pedido, abre arquivo
                with open(arquivo.dirArq + path[1:],'rb') as f:
                    body = f.read()

            statusCode = "200"
            statusMensage = "OK"

        #se o arquivo nao existe ou nao for achado retorna erro
        except FileNotFoundError:
            with open(arquivo.dirWeb + arquivo.pagErro, 'rb') as f:
                body = f.read()

            statusCode="404"
            statusMensage="Arquivo Não Encontrado"

    header=[f'Content-Length: {len(body)},'
            f'Connection: close']

    #manda o status, mensagem de status e infomracao disponibilizada no body (dos arquivos)
    con.send( (f'HTTP/1.1 {statusCode} {statusMensage}').encode('utf-8') )
    con.send(''.join(header).encode('utf-8'))
    con.send('\n\n'.encode('utf-8'))
    con.send(body)

    print(f'{statusMensage} \n')
    f.close()
    con.close()
    return



def main():
  # recebe os argumentos, se nao for definida a porta poem a do arquivo.port
  if len(argv) > 1:
     host = argv[0]
     port = int(argv[1])
  else:
    host = 'localhost'
    port = arquivo.port


  enderecoHost=getEnderecoHost(port)
  fd= criaSocket(enderecoHost)
  setModo(fd)
  bindaSocket(fd,port)
  print("Servidor pronto em",enderecoHost)
  escuta(fd)
  while(True):
    con = conecta(fd)
    if con == -1:
        continue
    # o fork() vai dividir os processos em processo pai e filho
    pid = fork()
    if pid == 0:
      #processo filho
      while True:
          request(con)
          #con.close()
      #exit()
    else:
    #processo pai
      con.close()
  return

if __name__ == "__main__":
  main()
