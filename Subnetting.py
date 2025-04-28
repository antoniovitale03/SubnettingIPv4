import math, ipaddress, random, sys
class Subnetting:
    def __init__(self, response):
        self.response = response
        self.num_subnets, self.indirizzamento, self.address_type = self.get_data()
        self.alfabeto = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    def get_data(self): #ottengo i dati iniziali
        num_subnet = int(input("Numero di sottoreti da configurare: "))
        indirizzamento = int(input("Classless[0] - Classful[1]"))
        address_type = int(input("Vuoi inserire manualmente l'indirizzo di rete di partenza (1) o ne vuoi generare uno casuale(0) ?"))
        return num_subnet, indirizzamento, address_type

    def run(self): #eseguo subnetting con o senza vlsm in base alla risposta dell'utente
        if self.response == 0:
            self.run_no_vlsm()
        elif self.response == 1:
            self.run_vlsm()
        else: sys.exit("Input errato.")

    def run_no_vlsm(self):
        num_host = int(input("Numero medio di host per sottorete: "))
        n_bit_subnet = math.ceil(math.log2(self.num_subnets))  # numero di bit minimo da associare al subnet-id   (vincolo 1)
        n_bit_host = math.ceil(math.log2(num_host + 2))  # numero di bit minimo da asscoaire all'host id  (+2 per rete e broadcast)   (vincolo 2)
        netmask = 32 - (n_bit_subnet + n_bit_host)  # la netmask dell'indirizzo di partenza che rispetta i due vincoli minimi contemporaneamente

        if self.indirizzamento == 0:
            self.classless_no_vlsm(self.num_subnets, n_bit_host, self.address_type, netmask)
        elif self.indirizzamento == 1:
            self.classful_no_vlsm(self.num_subnets, n_bit_subnet, n_bit_host, self.address_type, netmask)
        else: sys.exit("input errato. ")
    
    def run_vlsm(self):
        vlsm_table = {} #inizio la tabella vlsm (dizionario)
        # inizializzo la tabella inserendo il numero di host per ogni rete e ordino le reti in maniera decrescente per numero di host
        for i in range(self.num_subnets):
            rete = self.alfabeto[i]
            n_host = int(input(f"Numero di host nella rete {rete}: "))
            vlsm_table[rete] = [n_host]
        vlsm_table = dict(sorted(vlsm_table.items(), key=lambda item: item[1], reverse=True))   #grazie ChatGPT
        vincolo, vlsm_table = self.create_table_vlsm(vlsm_table)

        if self.indirizzamento == 0:
            self.classless_vlsm(vincolo, self.address_type, vlsm_table)
        elif self.indirizzamento == 1:
            self.classful_vlsm(vincolo, self.address_type, vlsm_table)
        else: sys.exit("Input errato")

    def create_table_vlsm(self, table):  # completa la tabella con numero minimo di bit, numero di indirizzi e netmask per ogni sottorete e calcolo anche il vincolo
        vincolo = 0
        for value in table.values():
            n_min_bit = math.ceil(math.log2(value[0] + 2))  # +2 perchè aggiungo anche rete e broadcast
            n_indirizzi = 2 ** n_min_bit
            value.append(n_min_bit)
            value.append(n_indirizzi)
            value.append(32 - n_min_bit) #netmask della sottorete
            vincolo += n_indirizzi
        return vincolo, table

    def subnetting_no_vlsm(self, num_subnet, network_ip, subnet_mask):
        subnets = list(network_ip.subnets(new_prefix=subnet_mask))  # genero le sottoreti con una certa subnet_mask partendo dalla rete principale
        i = 0
        for i in range(num_subnet):
            rete = self.alfabeto[i]
            subnet = subnets[i]
            print(f"Net {rete}: {subnet}")
            broadcast = subnets[i].broadcast_address
            print(f"Broadcast {rete}: {broadcast}/{subnet_mask}")
            print(f"Hosts {rete}: {subnet.network_address + 1}/{subnet_mask} - {broadcast - 1}/{subnet_mask}\n")  # subnets[i].hosts() è più dispendioso in termini di computazione

    def subnetting_vlsm(self, network_ip, dict):
        subnet_addr = network_ip.network_address
        for key in dict.keys():
            key = str(key)
            subnet_mask = dict[key][3]
            print(f"Net {key}: {subnet_addr}/{subnet_mask}")
            net = ipaddress.IPv4Network(f"{subnet_addr}/{subnet_mask}")
            broadcast = net.broadcast_address
            print(f"Broadcast {key}: {broadcast}/{subnet_mask}")
            print(f"Hosts {key}: {subnet_addr + 1}/{subnet_mask} - {broadcast - 1}/{subnet_mask}\n")  # subnets[i].hosts() è più dispendioso in termini di computazione
            subnet_addr = broadcast + 1

    def generate_random_network_classless(self, netmask):
        def regenerate_rand_net():
            ip_addr = [random.randint(0, 1) for i in range(netmask)] + [0] * (32 - netmask)
            # Dividiamo ip_lista in 4 liste da 8 (i 4 campi dell'indirizzo IP)
            ip_lista = [ip_addr[i:i + 8] for i in range(0, len(ip_addr), 8)]
            net = []
            for i in range(4):
                binario = ''.join(map(str, ip_lista[i]))  # trasforma la lista di numeri in un'unica stringa  [1, 0, 1] = "101"
                decimale = int(binario, 2)  # Convertiamo la stringa binaria in decimale
                net.append(decimale)
            if net[0] == 0 or net[0] == 127: #indirizzi speciali
                regenerate_rand_net()
            return net
        net = regenerate_rand_net()
        network_ip = ipaddress.IPv4Network(f"{net[0]}.{net[1]}.{net[2]}.{net[3]}/{netmask}")
        return network_ip

    def generate_random_network_classful(self, netmask):
        network_ip = 0
        match netmask:
            case 8:
                network_ip = f"{random.randint(1, 126)}.0.0.0/8"
            case 16:
                network_ip = f"{random.randint(128, 191)}.{random.randint(0, 255)}.0.0/16"
            case 24:
                network_ip = f"{random.randint(192, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.0/24"
        network_ip = ipaddress.IPv4Network(network_ip)
        return network_ip

    def find_netmask_no_vlsm(self, netmask):  # usato in no vlsm classful, approssima la netmask che rispetta entrambi i vincoli in una delle tre comuni delle classi A(/8),B(/16),C(/24)
        if netmask < 8:
            sys.exit("Netmask troppo piccola")
        elif netmask < 16:
            print("Indirizzo di partenza di classe A")
            return 8, "A"
        elif netmask < 24:
            print("Indirizzo di partenza di classe B")
            return 16, "B"
        else:
            print("Indirizzo di partenza di classe C")  #quando netmask < 32
            return 24, "C"

    def find_netmask_vlsm(self, vincolo): #usato in vlsm classful, trova la netmask di rete corretta sulla base del vincolo
        #calcolo il numero di bit riservato agli indirizzi sulla base della classe
        C = 2 ** 8
        B = 2 ** 16
        #A = 2 ** 24
        if vincolo < C:
            print("Indirizzo di partenza di classe C")
            return 24, "C"
        elif vincolo < B:
            print("Indirizzo di partenza di classe B")
            return 16, "B"
        else: #vincolo < A
            print("Indirizzo di partenza di classe A")
            return 8, "A"

    def check_address_netmask(self, network_ip, class_address, netmask): # controllo se l'IP della rete e la netmask corrispondono alla classe di appartenenza
        campo1 = int(network_ip.split("/")[0].split(".")[0])
        campo2 = int(network_ip.split("/")[0].split(".")[1])
        campo3 = int(network_ip.split("/")[0].split(".")[2])
        campo4 = int(network_ip.split("/")[0].split(".")[3])
        netmask_utente = int(network_ip.split("/")[1])  # netmask inserita dall'utente nell'indirizzo
        response = 0
        match class_address:
            case "A":
                if 0 < campo1 < 127 and campo2 == 0 and campo3 == 0 and campo4 == 0 and netmask_utente == netmask:
                    response = 1
            case "B":
                if 128 < campo1 < 191 and campo3 == 0 and campo4 == 0 and netmask_utente == netmask:
                    response = 1
            case "C":
                if 191 < campo1 < 223 and campo4 == 0 and netmask_utente == netmask:
                    response = 1
        return netmask_utente, response

    def choose_subnet_mask(self, netmask, n_bit_subnet, n_bit_host):
        netmask_dict = {}
        x = netmask + n_bit_subnet  # x = netmask da scegliere
        y = x - netmask  # y = bit subnet
        z = netmask - n_bit_subnet  # z = bit host
        while z >= n_bit_host:
            netmask_dict[x] = [y, z]
            x += 1
            y += 1
            z -= 1
        for key, value in netmask_dict.items():
            print(f"Netmask: /{key}, bit-subnet: {value[0]}, bit-host: {value[1]}")
        choice = int(input("Scegli una tra queste netmask: "))
        return choice

    def classless_no_vlsm(self, num_subnet, n_bit_host, address_type, max_netmask):
        subnet_mask = 32 - n_bit_host
        if address_type == 1:
            ip = input("Indirizzo di partenza(ricorda di indicare la netmask): ")
            network_ip = ipaddress.IPv4Network(ip)
            if network_ip.prefixlen > max_netmask:  # network_ip.prefix_len è la netmask dell'indirizzo di partenza
                print(f"Ricorda di usare una netmask minore o uguale di {max_netmask}")
            self.subnetting_no_vlsm(num_subnet, network_ip, subnet_mask)
        elif address_type == 0:
            network_ip = self.generate_random_network_classless(max_netmask)
            print(f"Indirizzo casuale generato: {network_ip}")
            self.subnetting_no_vlsm(num_subnet, network_ip, subnet_mask)

    def classful_no_vlsm(self, num_subnet, n_bit_subnet, n_bit_host, address_type, netmask):
        netmask, class_address = self.find_netmask_no_vlsm(netmask)
        if address_type == 1:
            network_ip = input(f"Indirizzo di partenza(ricorda di indicare la netmask corretta per la classe {class_address}): ")
            netmask, response = self.check_address_netmask(network_ip, class_address, netmask)
            if response == 1:
                network_ip = ipaddress.IPv4Network(network_ip)
                subnet_mask = self.choose_subnet_mask(netmask, n_bit_subnet, n_bit_host)
                self.subnetting_no_vlsm(num_subnet, network_ip, subnet_mask)
        elif address_type == 0:
            network_ip = self.generate_random_network_classful(netmask)
            print(f"Indirizzo casuale generato: {network_ip}")
            subnet_mask = self.choose_subnet_mask(netmask, n_bit_subnet, n_bit_host)
            self.subnetting_no_vlsm(num_subnet, network_ip, subnet_mask)

    def classless_vlsm(self, vincolo, address_type, table):
        n_bit_host = math.ceil(math.log2(vincolo))
        max_netmask = 32 - n_bit_host
        if address_type == 1:
            ip = input("Indirizzo di partenza(ricorda di indicare la netmask): ")
            network_ip = ipaddress.IPv4Network(ip)
            if network_ip.prefixlen > max_netmask:
                print(f"Ricorda di usare una netmask minore o uguale di {max_netmask}")
            self.subnetting_vlsm(network_ip, table)
        elif address_type == 0:
            network_ip = self.generate_random_network_classless(max_netmask)
            print(f"Indirizzo casuale generato: {network_ip}")
            self.subnetting_vlsm(network_ip, table)

    def classful_vlsm(self, vincolo, address_type, table):
        netmask, class_address = self.find_netmask_vlsm(vincolo)  # sulla base del vincolo trovato, indica la classe e la netmask dell'indirizzo di partenza
        if address_type == 1:
            network_ip = input(f"Indirizzo di partenza(ricorda di indicare la netmask corretta per la classe {class_address}): ")
            netmask, response = self.check_address_netmask(network_ip, class_address, netmask)
            if response == 1:
                network_ip = ipaddress.IPv4Network(network_ip)
                self.subnetting_vlsm(network_ip, table)
        elif address_type == 0:
            network_ip = self.generate_random_network_classful(netmask)
            print(f"Indirizzo casuale generato: {network_ip}")
            self.subnetting_vlsm(network_ip, table)

