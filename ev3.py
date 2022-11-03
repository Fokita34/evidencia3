#LIBRERIAS DE PYTHON
from collections import namedtuple
import datetime
import pandas as pd
import random
import sys
import sqlite3
import openpyxl
from sqlite3 import Error

evento = {}
open_first = False
try:
    d = open("database/BaseReserva.sqlite3",'r')
    d.close()
except FileNotFoundError:

    print("\n *** No se encontró ningun respaldo de Base de datos. Se tomará como primer inicio del programa. ***\n")
    input("\nEnter para continuar\n")
    open_first = True
finally:
    try:
        #ESTO ES PARA GENERAR UNA BASE DE DATOS EN CASO DE QUE NO HAYA UNA, Y VERIFICA SI YA ESTA HECHA PARA NO REPETIRLO#
        with sqlite3.connect("database/BaseReserva.sqlite3") as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS SALA (clave_sala INTEGER PRIMARY KEY, nombre TEXT NOT NULL, espacios INTEGER NOT NULL);")
            cursor.execute("CREATE TABLE IF NOT EXISTS CLIENTE (clave_cliente INTEGER PRIMARY KEY, nombre_cliente TEXT NOT NULL);")
            cursor.execute("CREATE TABLE IF NOT EXISTS TURNO (descripcion TEXT PRIMARY KEY, clave_turno TEXT NOT NULL);")
            cursor.execute("""CREATE TABLE IF NOT EXISTS RESERVACION (
                            folio INTEGER,
                            fecha_de_reserva TEXT NOT NULL,
                            nombre_evento TEXT NOT NULL,
                            cliente INTEGER NOT NULL,
                            sala INTEGER NOT NULL,
                            turno TEXT NOT NULL,
                            CONSTRAINT clave_pk PRIMARY KEY(folio,sala,turno),
                            FOREIGN KEY(sala) REFERENCES SALA(clave_sala),
                            FOREIGN KEY(turno) REFERENCES TURNO(descripcion),
                            FOREIGN KEY(cliente) REFERENCES CLIENTE(clave_cliente));""")
                            #AQUI TERMINA DE GENERARLA#
    except Error as e:
        print(e)
    else:
        if open_first:
            print("¡Base de datos generada con exito!\n")
#MENU PARA HACER LA INTERFAZ DEL SISTEMA DECLARADO CON NUMEROS PARA FACILITAR EL ACCESO#
while True:
    print("* " * 80)
    print(" Sistema de renta de espacios para Coworking ".center(100, " "))
    print("1. Reservaciones.")
    print("2. Reportes.")
    print("3. Registrar una Sala.")
    print("4. Registrar un Cliente.")
    print("\n0. Exit\n")
    print(" * " * 80)
    menu_op = int(input("Ingresa el numero con la opcion deseada: "))
#SI INGRESAMOS LA TECLA 1, ACCEDE AL MENU DE RESERVACIONES, DONDE PODEMOS HACER LO ESCRITO#
    if menu_op == 1:
        while True:
            print(f'\n{" Reservaciones ".center(80, "-")}\n')
            print("1. Registro de nueva reservación.")
            print("2. Modificar reservas.")
            print("3. Consulta de fechas disponibles.")
            print("4. Eliminar una reservación.")
            print("\n0. Volver al Menú Principal.\n")
            print(" -" * 50)
            submenu_op = int(input("Ingresa el numero con la opcion deseada: "))

#REGISTRAMOS NUEVA RESERVACION, PERO YA TENIENDO Y SALA REGISTRADO, SI NO, NO ES POSIBLE#
            if submenu_op == 1:
                print(" -" * 40)
                print(f'\n{"---- Realizar nueva reservacion ----".center(40, " ")}\n')
            
                print("***** Para realizar la reservacion se debe autenticar el cliente ****")
                print("\n0. Volver\n")
                try:
                    while True:
                        buscar_cliente = int(input("Ingrese la Clave del Cliente: "))
                        if buscar_cliente == 0:
                            break
                        with sqlite3.connect("database/BaseReserva.sqlite3") as conn:
                            cursor = conn.cursor()
                            evento['cliente'] = buscar_cliente
                            cursor.execute(f"SELECT clave_cliente, nombre_cliente FROM CLIENTE WHERE clave_cliente = :cliente", evento)
                            cliente_resultado = cursor.fetchall()
                            
                            if cliente_resultado:
                                print("Ejemplo: 24/12/2022 ")
                                fecha = input("Fecha a reservar (DD/MM/YYYY): ")
                                fecha_de_reserva = datetime.datetime.strptime(fecha, "%d/%m/%Y").date()
                                fecha_limite_reserva = fecha_de_reserva - datetime.timedelta(days=+2)
                                
                                if datetime.date.today() <= fecha_limite_reserva:
                                    print(f'\n{"/" * 41}')
                                    for clave, nombre in cliente_resultado:
                                        print(f"Clave: {clave}")
                                        print(f"Nombre del Cliente: {nombre}")
                                    print(f"Fecha a reservar: {fecha_de_reserva}\n")
                                    
                                    cursor.execute(f"""SELECT * FROM SALA;""")
                                    salas = cursor.fetchall()
                                    
                                    
                                    if not salas:
                                        print("No existen salas registradas en la base de datos")
                                    else:
                                        evento['fecha'] = fecha_de_reserva.strftime('%Y-%m-%d')
                                        cursor.execute(f"""SELECT DISTINCT S.clave_sala, S.nombre, S.espacios
                                                       FROM SALA as S, TURNO AS T
                                                       WHERE NOT EXISTS (SELECT * FROM RESERVACION AS R WHERE S.clave_sala = R.sala
                                                       AND T.descripcion = R.turno AND fecha_de_reserva = :fecha);""",evento)
                                        salas_disponibles = cursor.fetchall()
                                        
                                        print(f'{"Clave":<5} | {"Nombre de la Sala":<20} | {"espacios":<8} |')
                                        print(f'\n{"-" * 41}')
                                        for clave_sala, nombre, espacios in salas_disponibles:
                                            print(f'{clave_sala:<5} | {nombre:<20} | {espacios:<8} |')
                                        
                                        evento['sala'] = int(input("\nIngrese la CLAVE de la sala a escoger: "))
                                        cursor.execute(f"""SELECT T.clave_turno ,T.descripcion
                                                           FROM TURNO AS T
                                                           WHERE NOT EXISTS (SELECT * FROM RESERVACION AS R
                                                           WHERE T.descripcion = R.turno AND R.sala = :sala
                                                           AND fecha_de_reserva = :fecha);""",evento)
                                        turnos = cursor.fetchall()
                                        
                                        print(f'\n{" Turnos Disponibles ".center(80, "+")}\n')
                                        for clave_sala, descripcion in turnos:
                                            print(f'{clave_sala} - {descripcion}')
                                        
                                        
                                        while True:
                                            evento['turno'] = input("\nTeclea la letra del turno deseado: ").upper()
                                            cursor.execute(f"""SELECT turno FROM RESERVACION
                                                               WHERE sala = :sala AND fecha_de_reserva = :fecha
                                                               AND turno = (SELECT DESCRIPCION FROM TURNO WHERE clave_turno = :turno);""",evento)
                                            turno_ocupado = cursor.fetchall()
                                            if turno_ocupado:
                                               print("\n *** El Turno deseado esta ocupado, Porfavor escoja otro ***\n")
                                            else:
                                                cursor.execute("SELECT descripcion FROM TURNO WHERE clave_turno = :turno",evento)
                                                for t in cursor.fetchall():
                                                    evento['turno'] = t[0]
                                                break
                                        
                                        evento['nombre_evento'] = input("Nombre del Evento a crear: ")
                                        evento['folio'] = random.randint(10000,20000)
                                        cursor.execute(f"INSERT INTO RESERVACION VALUES(:folio,:fecha,:nombre_evento,:cliente,:sala,:turno);", evento)
                                        print("\nLa reservación se realizó con exito!\n")
                                        print(f"--- Folio de Reservación: {evento['folio']}")
                                        input("\nEnter para continuar\n")
                                        break 
                                else:
                                    print("\nERROR. La reservación de una sala se debe realizar minimo con 2 días de anticipación\n")  
                            else:
                                print("\n***** La clave asociada con el cliente NO se encuentra ***** | Por favor ingrese otra clave\n")
                except Error as e:
                    print(e)
                except Exception:
                    print(f"Ha ocurrido un problema: {sys.exc_info()[0]}")
                else:
                    print("*"*80)
                    
#COMO NUMERO 2, TENEMOS EL MODIFICAR LA RESERVACION EN CASO DE QUE EL CLIENTE REQUIERA MODIFICAR SU FECHA, ETC#
            if submenu_op == 2:
                print("- " * 41)
                print(f'\n{"---- Modificar descripción de una reservacion ----".center(80, " ")}\n')
                print("0. Regresar\n")
                while True:
                    folio_consulta = int(input("Ingrese el folio de la reservacion: "))
                    if folio_consulta == 0:
                        break
                    else:
                        print("-" * 80)
                        try:
                            with sqlite3.connect("database/BaseReserva.sqlite3") as conn:
                                cursor = conn.cursor()
                                cursor.execute(f"SELECT nombre_evento FROM RESERVACION WHERE folio = {folio_consulta}")
                                folio_encontrado = cursor.fetchall()
                                if folio_encontrado:
                                    for nombre_evento in folio_encontrado:
                                        print(f'\nNombre del Evento: {nombre_evento[0]}\n')
                                    nuevo_nombre = input("Ingrese la Nueva descripcion del evento: ")
                                    update = {'nombre_evento': nuevo_nombre, 'folio' : folio_consulta}
                                    cursor.execute(f"UPDATE RESERVACION SET nombre_evento = :nombre_evento WHERE folio = :folio", update)
                                    print("\nCambios Efectuados con Exito!\n")
                                else:
                                    print("No existe ninguna reservacion con ese Folio") 
                        except Error as e:
                            print(e)
                        except Exception:
                            print(f"Ha ocurrido un error: {sys.exc_info()[0]}")
                        else:
                            
                            input("\nEnter para continuar\n")
                            break
#COMO NUMERO 3, PODEMOS CONSULTAR LAS FECHAS DISPONIBLES QUE NO ESTAN RESESRVADAS LAS SALAS,
# PARA ASI FACILITAR EL HACER UNA RESERVA, OBVIO BASANDONOS EN UN HORARIO A TIEMPO REAL DE LA COMPUTADORA, PARA PDOER FACILITAR EL USO DE ESTE SISTEMA#

            if submenu_op == 3:
                print("- " * 41)
                print(f'\n{"---- Consultar Disponibilidad Salas por fecha ----".center(80, " ")}\n')
                print("0. Regresar\n")
                while True:
                    fecha_str = input("\nIngrese la fecha (DD/MM/YYYY): ")
                    if fecha_str == '0':
                        break
                    else:
                        try:
                            with sqlite3.connect("database/BaseReserva.sqlite3") as conn:
                                cursor = conn.cursor()
                                consultar_fecha = datetime.datetime.strptime(fecha_str, "%d/%m/%Y").date()
                                consultar_fecha = consultar_fecha.strftime('%Y-%m-%d')
                                cursor.execute(f"""SELECT S.clave_sala, S.nombre, T.DESCRIPCION
                                                FROM SALA as S, TURNO AS T
                                                WHERE NOT EXISTS (SELECT * FROM RESERVACION AS R WHERE S.clave_sala = R.sala 
                                                AND T.DESCRIPCION = R.TURNO and fecha_de_reserva = ?);""",(consultar_fecha,))
                                salas_accesibles = cursor.fetchall()
                        except Error as e:
                            print(e)
                        except Exception:
                            print(f"Ha ocurrido un error: {sys.exc_info()[0]}")
                        else:
                            #MENCIONA QUE SALAS REGISTRADAS ESTAN DISPONIBLE ESE DIA#
                            print("_" * 43)
                            print(f"\nSalas Disponibles para renta el {consultar_fecha}\n")
                            print(f'{"Clave".center(5," "):<5} | {"SALA".center(20," "):<20} | {"TURNO".center(10," "):<10} |')
                            print("-" * 43)
                            for clave_sala, nombre, espacios in salas_accesibles:
                                print(f'{clave_sala:<5} | {nombre:<20} | {espacios:<8} |')
                            fecha_str = input("\n¿Consultar otra fecha? [S/N]: ").upper()
                            if fecha_str == 'N': break

                             #SI DESESAMOS ELIMINAR UNA RESERVACION, TECLEAMOS EL NUMERO 4, EL CUAL CON EL FOLIO ENLAZADO, SERA MUCHO MAS FACIL ELIMINARLA#

            if submenu_op == 4:
                print("- " * 41)
                print(f'\n{"**Eliminar una reservación** ".center(80, " ")}\n')
                print("0. Regresar\n")
                while True:
                    folio_consulta = int(input("Ingrese el folio de la reservacion: "))
                    if folio_consulta == 0:
                        break
                    else:
                        print("-" * 80)
                        try:
                            with sqlite3.connect("database/BaseReserva.sqlite3") as conn:
                                cursor = conn.cursor()
                                cursor.execute(f"""SELECT R.folio, R.fecha_de_reserva, R.nombre_evento, R.cliente, C.nombre_cliente, R.sala , S.nombre, R.turno
                                                   FROM RESERVACION AS R
                                                   INNER JOIN CLIENTE AS C ON R.cliente = C.clave_cliente
                                                   INNER JOIN SALA AS S ON R.sala = S.clave_sala WHERE folio = {folio_consulta};""")
                                reserva = cursor.fetchall()

                                if reserva:
                                    for folio, fecha_de_reserva, nombre_evento, cliente, nombre_cliente, sala, nombre_sala, turno in reserva:
                                        fecha_de_reserva = datetime.datetime.strptime(fecha_de_reserva, "%Y-%m-%d").date()
                                        fecha_limite_reserva = fecha_de_reserva - datetime.timedelta(days=+3)
                                        if datetime.date.today() <= fecha_limite_reserva:
                                            print(f'\nFolio: {folio}')
                                            print(f'Fecha de Reservación: {fecha_de_reserva}\n')
                                            print(f'Nombre del Evento: {nombre_evento}\n')
                                            print(f'Nombre del Cliente: {nombre_cliente:<8} | Clave: {cliente}\n')
                                            print(f'{"Clave".center(5," "):<5} | {"SALA".center(20," "):<20} | {"TURNO".center(10," "):<10} |')
                                            print("-" * 43)
                                            print(f'{sala:<5} | {nombre_sala:<20} | {turno:<10} |')
                                            print('\n***** WARNING *****\n¡Esta accion no se puede deshacer!')
                                            delete = input("¿Seguro que deseas eliminar esta reservación? [S/N]: ").upper()
                                            if delete == 'S':
                                                cursor.execute(f"DELETE FROM RESERVACION WHERE folio = {folio};")
                                                print("\nLa reservacion fue Eliminada con exito!\n")
                                        else:
                                            print("Esta reservación ya NO puede ser elimanada, solo se pueden eliminar con 3 dias de anticipación ")
                                else:
                                    print("No existe ninguna reservacion con ese Folio") 
                        except Error as e:
                            print(e)
                        except Exception:
                            print(f"Ha ocurrido un error: {sys.exc_info()[0]}")
                        else:
                            break
            if submenu_op == 0:
                break
                #SI TECLEAMOS EL NUMERO 2, PODEMOS ACCEDER A LOS REPORTES, PARA EXPORTAR LA BASE DE DATOS A UN ARCHIVO EXCEL, EL CUAL NOS FACILITARA EL ACCESO DE LOS DATOS QUE SE ESTEN MANEJANDO#
    elif menu_op == 2:
        while True:
            print(f'\n{" Reportes ".center(80, "-")}\n')
            print("1. Reporte de reservaciones para una fecha.")
            print("2. Exportar reporte tabular (Excel).")
            print("\n0. Volver al Menú Principal\n")
            print(" -" * 40)
            submenu_op = int(input("Ingresa el número con la opción: \n"))
            
            
            if submenu_op == 1:
                print(" -" * 40)
                print(f'\n{" Reporte de Reservaciones para una fecha ".center(80, "-")}\n')
                print("0. Regresar\n")
                try:
                    while True:
                        fecha_str = input("Ingrese la fecha deseada: ")
                        if fecha_str == '0':
                            break
                        else:
                            consultar_fecha = datetime.datetime.strptime(fecha_str, "%d/%m/%Y").date()
                            with sqlite3.connect("database/BaseReserva.sqlite3") as conn:
                                cursor = conn.cursor()
                                cursor.execute(f"""SELECT R.folio, R.sala, C.nombre_cliente, R.nombre_evento, R.turno
                                                   FROM RESERVACION AS R
                                                   INNER JOIN CLIENTE AS C ON R.cliente = C.clave_cliente
                                                   WHERE R.fecha_de_reserva = ?;""",(consultar_fecha,))
                                reservaciones = cursor.fetchall()
                                if reservaciones:
                                    print(f"\n                 --- Reporte de Reservaciones para el día {consultar_fecha} ---       \n")
                                    print(f'{"Folio".center(5," ")} | {"Sala".center(10," ")} | {"Cliente".center(20," ")} | {"Evento".center(30," ")} | {"Turno".center(10," ")} |')
                                    print("-" * 90)
                                    for folio, sala, nombre_cliente, nombre_evento, turno in reservaciones:
                                        print(f'{folio} | {sala:<10} | {nombre_cliente:<20} | {nombre_evento:<30} | {turno:<10} |')
                                    input("\nEnter para continuar\n")
                                    break
                                else:
                                    print("\n***** No existen reservaciones con la fecha ingresada *****\n")
                except Error as e:
                    print(e)
                except Exception:
                    print(f"Ha ocurrido un error: {sys.exc_info()[0]}")
    
            if submenu_op == 2:
                folios = []
                fechas = []
                salas = []
                clientes = []
                eventos = []
                turnos = []
                try:
                    with sqlite3.connect("database/BaseReserva.sqlite3") as conn:
                        cursor = conn.cursor()
                        cursor.execute(f"""SELECT R.folio, R.fecha_de_reserva, S.nombre, C.nombre_cliente, R.nombre_evento, R.turno
                                           FROM RESERVACION AS R
                                           INNER JOIN CLIENTE AS C ON R.cliente = C.clave_cliente
                                           INNER JOIN SALA AS S ON R.sala = S.clave_sala;""")
                        reserva = cursor.fetchall()
                except Error as e:
                    print(e)
                except Exception:
                    print(f"Ha ocurrido un problema: {sys.exc_info()[0]}")
                else:
                    for folio, fecha_de_reserva, nombre_sala, nombre_cliente, nombre_evento, turno in reserva:
                        folios.append(folio)
                        fechas.append(fecha_de_reserva)
                        salas.append(nombre_sala)
                        clientes.append(nombre_cliente)
                        eventos.append(nombre_evento)
                        turnos.append(turno)
                    e = {"FOLIO":folios,"FECHA":fechas ,"SALA":salas, "CLIENTE":clientes, "EVENTO":eventos, "TURNO":turnos}
                    try:
                        df = pd.DataFrame(e)
                        df.to_excel('ReporteReservas.xlsx',index=False)
                    except Error as e:
                        print(e)
                    except Exception:
                        print(" *** ERROR *** Ocurrio un problema para exportar el archivo")
                        input("\nEnter para continuar\n")
                    else:
                        print(f"\nSe ha generado un archivo XLSX en la ruta actual")
                        input("\nEnter para continuar\n")
            if submenu_op == 0:
                break
           #ESTO ES PARA CREAR EL REGISTRO DE UNA SALA, EL CUAL ES REQUERIDO PARA LA RESERVACION DEL CLIENTE, LA EXPORTACION Y LA CREACION DEL REPORTE# 
    elif menu_op == 3:
        print(f'\n{" Registrar una Sala ".center(80, "-")}\n')
        while True:
            clave_sala = {'nombre_sala': input("Ingrese el nombre de la Sala: ")}
            if len(clave_sala['nombre_sala']) == 0 and clave_sala['nombre_sala'].strip() == '':
                print("Este campo no puede omitirse\n")
            else:
                break
        while True:
            clave_sala['espacios'] = input("Ingrese el espacios total para la Sala: ")
            if len(clave_sala['espacios']) == 0 and clave_sala['espacios'].strip() == '':
                print("El espacios no puede estar vacio\n")
            elif int(clave_sala['espacios']) <= 0:
                print("El numero debe ser mayor a 0\n")
            else:
                break
        try:
            with sqlite3.connect("database/BaseReserva.sqlite3") as conn:
                cursor = conn.cursor()
                while True:
                    clave_sala['id'] = random.randint(100,200)
                    cursor.execute(f"SELECT clave_sala FROM SALA WHERE clave_sala = :id;",clave_sala)
                    sala_ocupada = cursor.fetchall()
                    if not sala_ocupada:
                        cursor.execute(f"INSERT INTO SALA VALUES(:id,:nombre_sala,:espacios);",clave_sala)
                        break
        except Error as e:
            print(e)
        except Exception:
            print(f"Ha ocurrido un error: {sys.exc_info()[0]}")
        else:
            print("-" * 80)
            print("\nSala declarada con exito!\n")
            print(f"--- Clave de la Sala: {clave_sala['id']}")
            input("\nEnter para continuar\n")
    
    #REGISTRAR UN CLIENTE PARA PODER DAR EL NUMERO DE FOLIO PARA ACCEDER A LA RESERVACION#
    elif menu_op == 4:
        print(f'\n{" Registrar un Cliente ".center(80, "-")}\n')
        while True:
            clave_cliente = {'nombre_cliente' : input("Ingrese el nombre del Cliente: ")}
            if len(clave_cliente['nombre_cliente']) == 0 and clave_cliente['nombre_cliente'].strip() == '':
                print("Este campo no puede quedar vacio\n")
            else:
                break
        try:
            with sqlite3.connect("database/BaseReserva.sqlite3") as conn:
                cursor = conn.cursor()
                while True:
                    clave_cliente['id'] = random.randint(100,200)
                    cursor.execute(f"SELECT clave_cliente FROM CLIENTE WHERE clave_cliente = :id;",clave_cliente)
                    cliente_ocupado = cursor.fetchall()
                    if not cliente_ocupado:
                        cursor.execute(f"INSERT INTO CLIENTE VALUES(:id,:nombre_cliente);",clave_cliente)
                        break
        except Error as e:
            print(e)
        except Exception:
            print(f"Ha ocurrido un error: {sys.exc_info()[0]}")
        else:
            print("-" * 80)
            print("\nCliente registrado con exito!\n")
            print(f"--- Clave del Cliente: {clave_cliente['id']}")
            input("\nEnter para continuar\n")
            
    elif menu_op == 0:
        break