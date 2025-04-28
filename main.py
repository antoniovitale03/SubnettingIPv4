from Subnetting import Subnetting

response = int(input("Effettuare Subnetting NO VLSM (0) o Subnetting VLSM(1) ?"))
obj = Subnetting(response)
obj.run()