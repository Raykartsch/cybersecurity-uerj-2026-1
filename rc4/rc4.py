class RC4:
    def __init__(self, key):
        """
        Inicializa a classe RC4

        """

        #Instanciando os atributos
        #Verifica se a chave esta em bytes para a utilização do algoritmo. Se nao estiver, realiza a conversão de cada caracter da chave, caso contrario, so converte em lista
        if isinstance(key, str):
            self.key = [ord(character) for character in key]
        else:
            self.key = list(key)

        self.S = list(range(256))

        #Gera o S-Box do KSA
        self.KSA()

        #Recebe a chave gerada pelo PRGA
        self.keystream = self.PRGA()

    def KSA(self):
        """
        Key Scheduling Algorithm (KSA)
        Mistura o array de estado interno 'S'.

        """

        key_length = len(self.key)
        j = 0
        
        for i in range(256):
            j = (j + self.S[i] + self.key[i % key_length]) % 256
            self.S[i], self.S[j] = self.S[j], self.S[i] #Realiza o swap de Si e Sj

    def PRGA(self):
        """
        Pseudo-Random Generation Algorithm (PRGA)
        Retorna um gerador (generator) com o fluxo contínuo de bytes.

        """

        i = 0
        j = 0
        while True:
            i = (i + 1) % 256
            j = (j + self.S[i]) % 256
            self.S[i], self.S[j] = self.S[j], self.S[i] #Realiza o swap de Si e Sj
            t = (self.S[i] + self.S[j]) % 256
            K = self.S[t] #St
            yield K

    def process(self, data):
        """
        Aplica o XOR entre os dados e o keystream contínuo.

        """

        resultado = bytearray()
        
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        for byte in data:
            byte_processado = byte ^ next(self.keystream)
            resultado.append(byte_processado)
            
        return bytes(resultado)


# ==========================================
# TESTANDO A CLASSE RC4
# ==========================================

if __name__ == "__main__":
    key = "chave ultra super secreta nunca divulgada do algoritmo"
    msg = "Teste criptografia aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    
    print("------ ALGORITMO RC4 ------")
    
    #Criptografa a chave
    rc4_encrypt = RC4(key)
    
    #Mensagem criptografada com rc4
    encrypted_msg = rc4_encrypt.process(msg)

    print(f"Mensagem Criptografada (HEX): {encrypted_msg.hex()}")

    # Descriptografando (Sempre instanciar a classe de novo com a chave para descriptografar)
    rc4_decrypt = RC4(key)
    decrypt_msg_bytes = rc4_decrypt.process(encrypted_msg)
    decrypted_msg = decrypt_msg_bytes.decode('utf-8')
    
    print(f"\nMensagem Descriptografada: '{decrypted_msg}'")
    
    #Validação final
    assert msg == decrypted_msg
    print("\n✅ Sucesso! O código rodou liso e suporta dados quebrados em pedaços.")