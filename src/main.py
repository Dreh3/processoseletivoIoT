from machine import Pin, Timer, SoftI2C
import time

#------ Driver do sensor (implementando apenas a leitura de temperatura necessária) ------
MPU6050_ADDR = 0x68
TEMP_REGISTER = 0x41
_PWR_MGMT_1 = 0x6B

def inteiroDeBytes(x, final="big"):
    y = int.from_bytes(x, final)
    if (y >= 0x8000):
        return -((65535 - y) + 1)
    else:
        return y

class MPU6050:

  def __init__(self, i2c: SoftI2C, addr: MPU6050_ADDR):
    self.i2c = i2c
    self.addr = addr
    self.i2c.writeto_mem(self.addr, _PWR_MGMT_1, bytes([0x00]))
    time.sleep_ms(5)

  def read_data(self, reg, nbytes):
    return self.i2c.readfrom_mem(self.addr, reg, nbytes)

  def read_temperature(self):
    dados = self.read_data(TEMP_REGISTER, 2)
    dados = inteiroDeBytes(dados, "big")
    return (dados / 340) + 36.53

#------                         Variáveis de controle                               ------

PORTA_ABERTA = False
LIMITE_TEMPO = 5000
LIMITE_VARIACAO = 3.0

ESTADO_DE_ERRO_TEMP = False   #variáveis para emitir alerta apenas quando necessário
ESTADO_DE_ERRO_PORTA = False
ERRO = False

#------                      Configurando os periféricos                            ------

btn1 = Pin(14, Pin.IN, Pin.PULL_UP)
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)
mpu = MPU6050(i2c, MPU6050_ADDR)

timer = Timer(0)

#------                                 Funções                                     ------

#Função executada após 5000ms quando o timer é acionado
def limitePortaAberta(timer_obj):
  global PORTA_ABERTA, ESTADO_DE_ERRO_PORTA, ERRO
  if(PORTA_ABERTA):
    ERRO = True
    ESTADO_DE_ERRO_PORTA = True
    print("ALERTA: Porta aberta por muito tempo!")


temperaturaReferencial = mpu.read_temperature()

print("Sistema de Monitoramento Inicializado")

while True:

  time.sleep_ms(100)

  if(btn1.value()==1 and not PORTA_ABERTA):
    PORTA_ABERTA = True
    ESTADO_DE_ERRO_PORTA = True
    timer.init(period=LIMITE_TEMPO, mode=Timer.ONE_SHOT, callback=limitePortaAberta)
  elif(btn1.value()==0 and PORTA_ABERTA):
    timer.deinit()
    PORTA_ABERTA = False
    ESTADO_DE_ERRO_PORTA = False

  if(not PORTA_ABERTA and not ESTADO_DE_ERRO_TEMP):
    temperatura_atual = mpu.read_temperature()
    variacao_termica = temperatura_atual - temperaturaReferencial
    if (variacao_termica >= LIMITE_VARIACAO):
        ESTADO_DE_ERRO_TEMP = True
        ERRO = True
        print("ALERTA: Degradacao termica detectada!")
    else:
        ESTADO_DE_ERRO_TEMP = False
    temperaturaReferencial = temperatura_atual

  if(ERRO and not ESTADO_DE_ERRO_PORTA and not ESTADO_DE_ERRO_TEMP):
    #ERRO = False
    print("Status: Sistema Normalizado.")

  