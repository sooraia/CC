# CC-TP2
Trabalho prático de Comunicações por Computador

* Sofia Freitas (a106798)
* Soraia Pereira (a106806)

# Setup na topologia
A topologia da rede está definida no ficheiro [`config/Topologia.xml`](config/Topologia.xml).
As seguintes instruções explicam como inicializar o sistema após colocar a diretoria em volume e iniciar uma sessão com a topologia no emulador Core.

Abrir terminal com:
```
docker exec -it core bash
```
Navegar até à diretoria e executar script de inicialização:
```
./setup.sh start
```
Para parar, executar:
```
./setup.sh stop
```
## Interface Ground Control

Para aceder à interface web do Ground Control:
```
firefox ground/index.html
```

## Execução manual
Alternativamente, pode-se executar manualmente cada componente.

Na nave-mãe:
```
bash config/mother_route_setup.sh  #Configurar rotas
python -m mother # flag -l opcional para criar ficheiros com os logs do Mission Link em /tmp
```

Nos rovers:
```
python -m rover # flag -l opcional para criar ficheiros com os logs do Mission Link em /tmp
```