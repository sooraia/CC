# CC-TP2
Trabalho prático de Comunicações por Computador

* Sofia Freitas (a106798)
* Soraia Pereira (a106806)

# Setup na topologia
A topologia da rede está definida no ficheiro [`config/Topologia.xml`](config/Topologia.xml).
As seguintes instruções explicam como inicializar o sistema após abrir a topologia no emulador Core.

Abrir terminal com:
```
docker exec -it core bash
```
E executar script de inicialização:
```
./cc-tp2/setup.sh start
```
Para parar, executar:
```
./cc-tp2/setup.sh stop
```
## Interface Ground Control

Para aceder à interface web do Ground Control:
* Abrir um browser num bash do host ground-control
* Aceder ao endereço: http://localhost:8000

## Execução manual
Alternativamente, pode-se executar manualmente cada componente.

Na nave-mãe:
```
cd cc-tp2
bash config/mother_route_setup.sh  #Configurar rotas
python -m mother # flag -l opcional para criar ficheiros com os logs do Mission Link em /tmp
```

Nos rovers:
```
cd cc-tp2
python -m rover # flag -l opcional para criar ficheiros com os logs do Mission Link em /tmp
```

No ground-control:
```
cd cc-tp2/ground
python -m http.server 8000
```
