
from pyDes import *
import os
from random import randrange


class DESCipherAlgorithm: 
    """
    Classe pra encriptar e decriptar arquivos usando DES e 3DES via pyDes.
    """
     
    # Padronização dos params da classe
    def __init__(self, key, algorithm="DES", iv="\0\0\0\0\0\0\0\0"):
        self.algorithm = algorithm.upper()
        self.key = key
        self.iv = iv
        
        #Verifica o tamanho do vetor de inicializacao, caso seja diferente de 8, levantar excecao
        if len(self.iv) != 8:
            raise ValueError("\nIV precisa ter 8 bytes!!")

        # Config do algoritmo DES
        if self.algorithm == 'DES':
            if len(self.key) != 8:
                raise ValueError("\nA chave do DES precisa ter 8 bytes!!")
            self.cipher = des(self.key, CBC, self.iv, pad=None, padmode=PAD_PKCS5)
        
        # Config do algoritmo 3DES
        elif self.algorithm == '3DES':
            if len(self.key) not in (16, 24):
                raise ValueError("\nA chave para o 3DES precisa ter 16/24 bytes!!")
            self.cipher = triple_des(self.key, CBC, self.iv, pad=None, padmode=PAD_PKCS5)
        else:
            raise ValueError("\nEscolha entre as opções: DES ou 3DES")
        
    ######################################################################################################

    #Método de encriptação do arquivo
    def encrypt_file(self, input_path, output_path):

        # Se o arquivo nao existir, levantar excecao
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"\nO arquivo '{input_path}' não foi encontrado!!")
        
        #Ler arquivo de origem
        with open(input_path, 'rb') as f_in:
            file_data = f_in.read()
        
        #Criptografar o arquivo de origem
        encrypted_data = self.cipher.encrypt(file_data)
        
        #Escrever arquivo descriptografado no diretorio de destino
        with open(output_path, 'wb') as f_out:
            f_out.write(encrypted_data)
            
        print(f"\nEncriptação e salvamento do arquivo '{input_path}' bem sucedida no arquivo '{output_path}'!!")
    

    ######################################################################################################
    
    #Método de desencriptação do arquivo
    def decrypt_file(self, input_path, output_path):

        # Se o arquivo nao existir, levantar excecao
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Arquivo não encontrado: '{input_path}'!!")

        #Ler arquivo de origem
        with open(input_path, 'rb') as f_in:
            encrypted_data = f_in.read()
        
        #Tentar descriptografar arquivo de origem, levantar exceção caso ocorra erro
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
        except ValueError as e:
            raise ValueError("\nFalha na decriptação!! Verifique a chave, o IV ou o arquivo!!")
        
        #Escrever arquivo descriptografado no diretorio de destino
        with open(output_path, 'wb') as f_out:
            f_out.write(decrypted_data)
            
        print(f"\nDesencriptação e salvamento do arquivo '{input_path}' bem sucedida no arquivo '{output_path}'")


if __name__ == "__main__":

    #Setando os arquivos para a operação do script
    current_file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    msg = os.path.join(current_file_path, "des_implementation", "message.txt") #Arquivo padrão
    enc_msg = os.path.join(current_file_path, "des_implementation", "encrypted_message.txt") #Arquivo encriptado
    rec_msg = os.path.join(current_file_path, "des_implementation", "recovered_message.txt") #Arquivo descriptografado
    
    #Valor do vetor de inicialização padrão
    pattern_iv = b"00000000" # 8 bytes de IV

    #Criando arquivo de teste
    with open(msg, mode="w", encoding="utf-8") as f:
        f.write("Lorem Ipsum. Testing script. 123456.")

######################################################################################################

    #------ EXEMPLO COM DES ------
    print("\n------ EXEMPLO COM DES  ------")
    key_des = os.urandom(8)  # DES precisa de exatos 8 bytes de chave
    print(f"\n(DISCLAIMER: Para fins educativos o script mostra a chave)\nExibindo chave de 8 bytes utilizada, guarde-a em um lugar seguro!: ", key_des)

    # Instancia a classe
    cipher_des = DESCipherAlgorithm(key=key_des, algorithm='DES', iv=pattern_iv)

    #Executa as operações de encriptacao/desencriptacao
    cipher_des.encrypt_file(msg, enc_msg)
    cipher_des.decrypt_file(enc_msg, rec_msg)


# ######################################################################################################

    # # #  ------ EXEMPLO COM 3DES  ------
    # print("\n------ EXEMPLO COM 3DES  ------")
    # key_size = randrange(16, 24, 8) # 3DES precisa de 16/24 bytes pra compor a chave de encriptaca
    # key_3des = os.urandom(key_size)

    # print(f"\n(DISCLAIMER: Para fins educativos o script mostra a chave)\nExibindo chave de tamanho {key_size} bytes utilizada. Guarde-a em um lugar seguro! : ", key_3des) 
    
    # # Instancia a classe
    # cipher_3des = DESCipherAlgorithm(key=key_3des, algorithm='3DES', iv=pattern_iv)
    
    # # Executa as operações de encriptacao/desencriptacao
    # cipher_3des.encrypt_file(msg, enc_msg)
    # cipher_3des.decrypt_file(enc_msg, rec_msg)

    
 