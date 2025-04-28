import math, ipaddress, random, main
class Subnetting:
    def __init__(self, response):
        self.response = response
        self.num_subnet, self.indirizzamento, self.address_type = self.get_data()
        self.alfabeto = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    def get_data(self):
        num_subnet = int(input("Numero di sottoreti da configurare: "))
        indirizzamento = int(input("Classless[0] - Classful[1]"))
        address_type = int(input("Vuoi inserire manualmente l'indirizzo di rete di partenza (1) o ne vuoi generare uno casuale(0) ?"))
        return num_subnet, indirizzamento, address_type

    def main_no_vlsm(self):
        num_host = int(input("Numero di host per sottorete: "))
        n_bit_subnet = math.ceil(math.log2(self.num_subnet))  # numero di bit minimo da associare al subnet-id   (vincolo 1)
        n_bit_host = math.ceil(math.log2(num_host + 2))  # numero di bit minimo da asscoaire all'host id  (+2 per rete e broadcast)   (vincolo 2)
        netmask = 32 - (n_bit_subnet + n_bit_host)  # la netmask dell'indirizzo di partenza che rispetta i due vincoli minimi contemporaneamente
        if self.indirizzamento == 0:
            self.classless_no_vlsm(self.num_subnet, n_bit_host, self.address_type, netmask)
        elif self.indirizzamento == 1:
            self.classful_no_vlsm(self.num_subnet, n_bit_subnet, n_bit_host, self.address_type, netmask)

    def main_vlsm(self):
        global dict
        uo_dict = {}
        # inizializzo il dizionario con gli host e lo ordino in maniera decrescente per numero di host
        for i in range(self.num_subnet):
            lettera = self.alfabeto[i]
            n_host = int(input(f"Numero di host nella rete {lettera}: "))
            uo_dict[lettera] = [n_host]
        dict_sorted = dict(sorted(uo_dict.items(), key=lambda item: item[1], reverse=True))
        dict = dict_sorted
        vincolo, dict = self.create_table_vlsm(dict)
        if self.indirizzamento == 0:
            self.classless_vlsm(vincolo, self.address_type, dict)
        elif self.indirizzamento == 1:
            self.classful_vlsm(vincolo, self.address_type, dict)

    def create_table_vlsm(self, dict):  # completa la tabella con numero minimo di bit, numero di indirizzi e netmask per ogni sottorete e calcolo anche il vincolo
        vincolo = 0
        for value in dict.values():
            n_min_bit = math.ceil(math.log2(value[0] + 2))  # +2 perchè aggiungo anche rete e broadcast
            n_indirizzi = 2 ** n_min_bit
            value.append(n_min_bit)
            value.append(n_indirizzi)
            value.append(32 - n_min_bit)
            vincolo += n_indirizzi
        return vincolo, dict

    def subnetting_no_vlsm(self, num_subnet, network_ip, subnet_mask):
        subnets = list(network_ip.subnets(new_prefix=subnet_mask))  # genero le sottoreti con una certa subnet_mask
        i = 0
        for i in range(num_subnet):
            lettera = self.alfabeto[i]
            subnet = subnets[i]
            print(f"Net {lettera}: {subnet}")
            broadcast = subnets[i].broadcast_address
            print(f"Broadcast {lettera}: {broadcast}/{subnet_mask}")
            print(
                f"Hosts {lettera}: {subnet.network_address + 1}/{subnet_mask} - {broadcast - 1}/{subnet_mask}\n")  # subnets[i].hosts() è più dispendioso in termini di computazione

    def subnetting_vlsm(self, network_ip, dict):
        subnet_addr = network_ip.network_address
        for key in dict.keys():
            key = str(key)
            subnet_mask = dict[key][3]
            print(f"Net {key}: {subnet_addr}/{subnet_mask}")
            net = ipaddress.IPv4Network(f"{subnet_addr}/{subnet_mask}")
            broadcast = net.broadcast_address
            print(f"Broadcast {key}: {broadcast}/{subnet_mask}")
            print(
                f"Hosts {key}: {subnet_addr + 1}/{subnet_mask} - {broadcast - 1}/{subnet_mask}\n")  # subnets[i].hosts() è più dispendioso in termini di computazione
            subnet_addr = broadcast + 1

    def generate_random_network_classless(self, netmask):
        ip_addr = [random.randint(0, 1) for i in range(netmask)] + [0] * (32 - netmask)
        # Dividiamo ip_lista in 4 liste da 8 (i 4 campi dell'indirizzo IP)
        ip_lista = [ip_addr[i:i + 8] for i in range(0, len(ip_addr), 8)]
        ip_rete = []
        for i in range(4):
            binario = ''.join(
                map(str, ip_lista[i]))  # trasforma la lista di numeri in un'unica stringa  [1, 0, 1] = "101"
            decimale = int(binario, 2)  # Convertiamo la stringa binaria in decimale
            ip_rete.append(decimale)
        network_ip = ipaddress.IPv4Network(f"{ip_rete[0]}.{ip_rete[1]}.{ip_rete[2]}.{ip_rete[3]}/{netmask}")
        return network_ip

    def generate_random_network_classful(self, netmask):
        network_ip = 0
        match netmask:
            case 8:
                campo = str(random.randint(1, 126))
                network_ip = ipaddress.IPv4Network(f"{campo}.0.0.0/{netmask}")
            case 16:
                campo1 = str(random.randint(128, 191))
                campo2 = str(random.randint(0, 255))
                network_ip = ipaddress.IPv4Network(f"{campo1}.{campo2}.0.0/{netmask}")
            case 24:
                campo1 = str(random.randint(192, 223))
                campo2 = str(random.randint(0, 255))
                network_ip = ipaddress.IPv4Network(f"{campo1}.{campo2}.{campo2}.0/{netmask}")
        return network_ip

    def find_netmask_no_vlsm(self, netmask):  # usato in no vlsm classful, approssima la netmask che rispetta entrambi i vincoli in una delle tre comuni delle classi A(/8),B(/16),C(/24)
        if netmask < 8:
            return 0
        elif 8 <= netmask < 16:
            print("Indirizzo di partenza di classe A")
            return 8, "A"
        elif 16 <= netmask < 24:
            print("Indirizzo di partenza di classe B")
            return 16, "B"
        else:
            print("Indirizzo di partenza di classe C")
            return 24, "C"

    def find_netmask_vlsm(self, vincolo): #usato in vlsm classful, trova la netmask di rete corretta sulla base del vincolo
        C = 2 ** 8  # numero di bit riservati agli indirizzi
        B = 2 ** 16
        A = 2 ** 24
        n_bit = [C, B, A]
        for value in n_bit:
            if vincolo <= value:
                vincolo = value
                break
        if vincolo == C:
            print("Indirizzo di partenza di classe C")
            return 24, "C"
        elif vincolo == B:
            print("Indirizzo di partenza di classe B")
            return 16, "B"
        elif vincolo == A:
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

    def choice_subnet_mask(self, netmask, n_bit_subnet, n_bit_host):
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
                subnet_mask = self.choice_subnet_mask(netmask, n_bit_subnet, n_bit_host)
                self.subnetting_no_vlsm(num_subnet, network_ip, subnet_mask)
        elif address_type == 0:
            network_ip = self.generate_random_network_classful(netmask)
            print(f"Indirizzo casuale generato: {network_ip}")
            subnet_mask = self.choice_subnet_mask(netmask, n_bit_subnet, n_bit_host)
            self.subnetting_no_vlsm(num_subnet, network_ip, subnet_mask)

    def classless_vlsm(self, vincolo, address_type, dict):
        n_bit_host = math.ceil(math.log2(vincolo))
        max_netmask = 32 - n_bit_host
        if address_type == 1:
            ip = input("Indirizzo di partenza(ricorda di indicare la netmask): ")
            network_ip = ipaddress.IPv4Network(ip)
            if network_ip.prefixlen > max_netmask:
                print(f"Ricorda di usare una netmask minore o uguale di {max_netmask}")
            self.subnetting_vlsm(network_ip, dict)
        elif address_type == 0:
            network_ip = self.generate_random_network_classless(max_netmask)
            print(f"Indirizzo casuale generato: {network_ip}")
            self.subnetting_vlsm(network_ip, dict)

    def classful_vlsm(self, vincolo, address_type, dict):
        netmask, class_address = self.find_netmask_vlsm(vincolo)  # sulla base del vincolo trovato, indica la classe e la netmask dell'indirizzo di partenza
        if address_type == 1:
            network_ip = input(f"Indirizzo di partenza(ricorda di indicare la netmask corretta per la classe {class_address}): ")
            netmask, response = self.check_address_netmask(network_ip, class_address, netmask)
            if response == 1:
                network_ip = ipaddress.IPv4Network(network_ip)
                self.subnetting_vlsm(network_ip, dict)
        elif address_type == 0:
            network_ip = self.generate_random_network_classful(netmask)
            print(f"Indirizzo casuale generato: {network_ip}")
            self.subnetting_vlsm(network_ip, dict)

    def run(self):
        if self.response == 0:
            self.main_no_vlsm()
        elif self.response == 1:
            self.main_vlsm()