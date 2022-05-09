import os, pickle, socket, sys

BUFFER_SIZE = 1024

def list_cache_requisicao(s, requeisicao):
    s.send(requeisicao.encode())
    files_cache = s.recv(BUFFER_SIZE)
    print(pickle.loads(files_cache))

def file_requisicao(diretorio, s, requisicao):
    os.chdir(diretorio)
    s.send(requisicao.encode())

    with open(requisicao, 'wb') as file:
        have = True
        while True:
            data = s.recv(BUFFER_SIZE)
            if(data == b'Arquivo Inexistente'):
                print('Arquivo Inexistente')
                os.remove(requisicao)
                have = False
                break
            if not data:
                break
            file.write(data)
    file.close()
    if(have):
        print(f'Arquivo {requisicao} salvo com sucesso')
    s.close()

if __name__ == "__main__":
    
    HOST = sys.argv[1]
    PORT = sys.argv[2]
    requisicao = sys.argv[3]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, int(PORT)))

    if(requisicao == 'list'):
        list_cache_requisicao(s, requisicao)
    else:
        DIRETORIO = sys.argv[4]
        file_requisicao(DIRETORIO, s, requisicao)
