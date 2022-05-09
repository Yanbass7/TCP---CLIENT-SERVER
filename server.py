import os, pickle, socket, sys, threading


MB = 64
MAX_CACHE_SIZE = MB*(1024*1024)

BUFFER_SIZE = 1024

CACHE_SIZE = 0

CACHE = { }
# -----------------

def remove_element_cache(tamanho_file):
   remove_tamanho = 0
   key_remove = ''
   count = 0
   for key in CACHE:
      file = CACHE.get(key)
      atual_key = key
      tamanho_atual = file['tamanho']
      if(file['tamanho'] >= tamanho_file):
         remove_tamanho = tamanho_atual
         key_remove = atual_key
         break
      else:
         if(remove_tamanho >= count):
            count = tamanho_atual
            remove_tamanho = count
            key_remove = atual_key
   CACHE.pop(key_remove)
   return (CACHE_SIZE - remove_tamanho)

def get_cache_files():
   list = []
   for key in CACHE.keys(): 
      list.append(key) 
   return list

def client_connect(diretorio, conn, addr, lock):
   global CACHE
   global CACHE_SIZE
   
   os.chdir(diretorio)

   requisicao = conn.recv(BUFFER_SIZE).decode()
   
   print(f'Cliente {addr} arquivo requerido {requisicao}')

   if(requisicao == 'list'):
      conn.send(pickle.dumps(get_cache_files()))
      conn.close()
      print('Solicitação da lista de cache enviada para o cliente')
   
   else:
      lock.acquire()
      if(CACHE.get(str(requisicao))):
         print(f'Acerto de cache. Arquivo {requisicao} enviado para o cliente.')
         payload_file = CACHE.get(str(requisicao))
         data = pickle.loads(payload_file['data'])
         conn.send(data)
         conn.close()
   
      else:
         if(os.path.isfile(requisicao)):        
            with open(requisicao, 'rb') as file:
               file_tamanho = os.path.getsize(requisicao)
               payload_file = file.read()
               if(file_tamanho <= MAX_CACHE_SIZE):

                  payload_to_cache = b''
                  while(payload_file):
                     conn.send(payload_file)
                     payload_to_cache += payload_file
                     payload_file = file.read(BUFFER_SIZE)
                  
                  payload_serialize = pickle.dumps(payload_to_cache)
                  while(CACHE_SIZE+file_tamanho > MAX_CACHE_SIZE):
                     CACHE_SIZE = remove_element_cache(file_tamanho)
                  
                  to_cache = {str(requisicao): {'tamanho': file_tamanho, 'data': payload_serialize}}
                  CACHE_SIZE += file_tamanho
                  CACHE.update(to_cache)
                  
               else:
                  while(payload_file):
                     conn.send(payload_file)
                     payload_file = file.read(BUFFER_SIZE)
            file.close()
            conn.close()
            print(f'Arquivo {requisicao} enviado para o cliente')
         
         else:
            conn.send(b'Arquivo inexistente')
            conn.close()
            print(f'Arquivo {requisicao} inexistente')
   
   lock.release()

if __name__ == "__main__":

   HOST = 'localhost'
   PORT = sys.argv[1]
   DIRETORIO = sys.argv[2]

   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   s.bind((HOST, int(PORT)))

   while True:
      s.listen()
      conn, addr = s.accept()
      lock = threading.Semaphore()
      new_client = threading.Thread(target=client_connect, args=(DIRETORIO, conn, addr, lock))
      new_client.start()
   
   s.close()
