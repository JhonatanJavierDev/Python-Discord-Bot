
#1848824
import discord
import random
import mysql.connector
from discord.ext import commands

# Crear una conexión a la base de datos
try:
    cnx = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="habana",
        autocommit=True
    )
    print("Conexion a la base de datos establecida")
except mysql.connector.Error as err:
    print("No se pudo conectar con la base de datos")
    exit()

# Crear un objeto Intents y habilitar los eventos que necesita tu bot
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.presences = True  # Habilitar la opción de presencia
intents.messages = True   # Habilitar la opción de mensajes
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)




@bot.command()
async def banana(ctx):
    # Generar un número aleatorio entre 3 y 35
    size = random.randint(3, 35)
    
    # Enviar un mensaje al usuario con el tamaño de la banana
    await ctx.send(f"Tu banana mide {size} cm")


@bot.command()
async def ip(ctx):
    ip = "182.184.45.245:7777"
    embed = discord.Embed(title="Nuestra IP", color=0x47049C)
    embed.add_field(name="IP:", value=ip)
    await ctx.send(embed=embed)



@bot.command()
async def pdinero(ctx, nombre_envia: str, pin_envia: str, cantidad_dinero: int, nombre_recibe: str):
    
    # Verificar que el usuario que envía no sea el mismo que el que recibe
    if nombre_envia == nombre_recibe:
        await ctx.send("No puedes enviarte dinero a ti mismo.")
        return

    cursor = cnx.cursor()

    # Ejecutar la consulta SQL para buscar el nombre y PIN en la tabla player
    query = "SELECT * FROM player WHERE name = %s AND user_pin = %s"
    cursor.execute(query, (nombre_envia, pin_envia))
    result = cursor.fetchone()

    # Verificar si se obtuvo algún resultado de la consulta
    if result is None:
        # Si las credenciales no son correctas, enviar un mensaje de error
        await ctx.send("Nombre o PIN incorrecto.")
    else:
        # Verificar que el jugador tenga suficiente dinero para enviar
        cash = result[22]
        if cantidad_dinero > cash:
            await ctx.send(f"No tienes suficiente dinero. Tienes {cash} disponibles.")
        else:
            # Ejecutar la consulta SQL para buscar el nombre del destinatario en la tabla player
            query = "SELECT * FROM player WHERE name = %s"
            cursor.execute(query, (nombre_recibe,))
            destinatario = cursor.fetchone()

            if destinatario is None:
                # Si el destinatario no se encuentra en la tabla, enviar un mensaje de error
                await ctx.send("La persona a la que envías el dinero no está registrada en el servidor.")
            else:
                # Ejecutar la consulta SQL para actualizar la columna cash del que envía
                query = "UPDATE player SET cash = cash - %s WHERE name = %s"
                cursor.execute(query, (cantidad_dinero, nombre_envia))

                # Ejecutar la consulta SQL para actualizar la columna cash del que recibe
                query = "UPDATE player SET cash = cash + %s WHERE name = %s"
                cursor.execute(query, (cantidad_dinero, nombre_recibe))

                cnx.commit()

                # Enviar un mensaje de confirmación al usuario
                await ctx.send(f"Se han enviado {cantidad_dinero} de dinero de {nombre_envia} a {nombre_recibe}")

    # Cerrar el cursor
    cursor.close()


@bot.command()
async def dargemas(ctx, nombre_apellido: str, cantidad_gemas: int):
    # Verificar si el autor del mensaje tiene uno de los roles autorizados y está en el canal permitido
    if not any(role.id in [1082164856683253800, 1082417748019269692] for role in ctx.author.roles):
        await ctx.send("No estás autorizado para usar este comando.")
        return

    if ctx.channel.id != 1082429841820889159:
        await ctx.send("No estás en el canal autorizado para usar este comando.")
        return
    cursor = cnx.cursor()

    # Ejecutar la consulta SQL para buscar el nombre en la tabla player
    query = "SELECT * FROM player WHERE name = %s"
    cursor.execute(query, (nombre_apellido,))
    result = cursor.fetchone()

    # Verificar si se obtuvo algún resultado de la consulta
    if result is None:
        # Si el jugador no está registrado, enviar un mensaje de error
        await ctx.send(f"{nombre_apellido} no está registrado en el servidor, no se pueden entregar gemas a una cuenta inexistente.")
    else:
        # Ejecutar la consulta SQL para actualizar la columna coins
        query = "UPDATE player SET coins = coins + %s WHERE name = %s"
        cursor.execute(query, (cantidad_gemas, nombre_apellido))
        cnx.commit()

        # Enviar un mensaje de confirmación al usuario
        await ctx.send(f"Se han entregado {cantidad_gemas} gemas a {nombre_apellido}")

    # Cerrar el cursor
    cursor.close()


@bot.command()
async def validar(ctx, nombre_apellido: str):
    # Crear un objeto cursor para ejecutar consultas SQL
    cursor = cnx.cursor()
    
    # Ejecutar la consulta SQL para buscar el nombre en la tabla player
    query = "SELECT * FROM player WHERE name = %s"
    cursor.execute(query, (nombre_apellido,))
    result = cursor.fetchone()
    
    # Verificar si se obtuvo algún resultado de la consulta
    if result is None:
        # Si el jugador no está registrado, enviar un mensaje de error
        await ctx.author.send(f" {nombre_apellido} Esta cuenta no está registrada en el servidor, para crear una cuenta ingresa a nuestra IP: 2485.252.525.24:7777 y registra una cuenta en nuestro servidor.")
    else:
        # Si el jugador está registrado, actualizar su apodo y roles
        member = ctx.message.author
        guild = ctx.guild
        
        # Buscar el rol "No verificado" por su ID
        no_verificado = guild.get_role(1081986423244206192)
        
        # Buscar el rol "Verificado" por su ID
        verificado = guild.get_role(1081986489874915391)
        
        # Quitar el rol "No verificado" si el usuario lo tiene
        if no_verificado in member.roles:
            await member.remove_roles(no_verificado)
        
        # Agregar el rol "Verificado"
        await member.add_roles(verificado)
        
        # Cambiar el apodo del usuario al nombre y apellido ingresados
        await member.edit(nick=nombre_apellido)
        
        # Enviar un mensaje de confirmación al usuario
        await ctx.author.send(f"Tu cuenta ha sido verificada, {nombre_apellido}! :white_check_mark:")

@bot.command()
async def pautos(ctx, name: str, pin: str):
    if ctx.channel.id != 1081993572515053650:
        return

    # Crear un diccionario que mapee los IDs de modelo de vehículo a sus nombres
    vehicle_names = {
        400: "Landstalker",
        401: "Bravura",
        402: "Buffalo",
        403: "Linerunner",
        404: "Perennial",
        405: "Sentinel",
        406: "Dumper",
        407: "Firetruck",
        408: "Trashmaster",
        409: "Stretch",
        410: "Manana",
        411: "Infernus",
        412: "Voodoo",
        413: "Pony",
        414: "Mule",
        415: "Cheetah",
        416: "Ambulance",
        417: "Leviathan",
        418: "Moonbeam",
        419: "Esperanto",
        420: "Taxi",
        421: "Washington",
        422: "Bobcat",
        423: "Mr. Whoopee",
        424: "BF Injection",
        425: "Hunter",
        426: "Premier",
        427: "Enforcer",
        428: "Securicar",
        429: "Banshee",
        430: "Predator",
        431: "Bus",
        432: "Rhino",
        433: "Barracks",
        434: "Hotknife",
        435: "Article Trailer",
        436: "Previon",
        437: "Coach Bus",
        438: "Cabbie",
        439: "Stallion",
        440: "Rumpo",
        441: "RC Bandit",
        442: "Romero",
        443: "Packer",
        444: "Monster",
        445: "Admiral",
        446: "Squallo",
        447: "Seasparrow",
        448: "Pizzaboy",
        449: "Tram",
        450: "Article Trailer 2",
        451: "Turismo",
        452: "Speeder",
        453: "Reefer",
        454: "Tropic",
        455: "Flatbed",
        456: "Yankee",
        457: "Caddy Golf",
        458: "Solair",
        459: "Topfun Van (Berkley's RC)",
        460: "Skimmer",
        461: "PCJ-600",
        462: "Faggio",
        463: "Freeway",
        464: "RC Baron",
        465: "RC Raider",
        466: "Glendale",
        467: "Oceanic",
        468: "Sanchez",
        469: "Sparrow",
        470: "Patriot",
        471: "Quad",
        472: "Coastguard",
        473: "Dinghy",
        474: "Hermes",
        475: "Sabre",
        476: "Rustler",
        477: "ZR-350",
        478: "Walton",
        479: "Regina",
        480: "Comet",
        481: "BMX",
        482: "Burrito",
        483: "Camper",
        484: "Marquis",
        485: "Baggage",
        486: "Dozer",
        487: "Maverick",
        488: "SAN News Maverick",
        489: "Rancher",
        490: "FBI Rancher",
        491: "Virgo",
        492: "Greenwood",
        493: "Jetmax",
        494: "Hotring Racer",
        495: "Sandking",
        496: "Blista Compact",
        497: "Police Maverick",
        498: "Boxville",
        499: "Benson",
        500: "Mesa",
        501: "RC Goblin",
        502: "Hotring Racer A",
        503: "Hotring Racer B",
        504: "Bloodring Banger",
        505: "Rancher Lure",
        506: "Super GT",
        507: "Elegant",
        508: "Journey",
        509: "Bike",
        510: "Mountain Bike",
        511: "Beagle",
        512: "Cropduster",
        513: "Stuntplane",
        514: "Tanker",
        515: "Roadtrain",
        516: "Nebula",
        517: "Majestic",
        518: "Buccaneer",
        519: "Shamal",
        520: "Hydra",
        521: "FCR-900",
        522: "NRG-500",
        523: "HPV1000",
        524: "Cement Truck",
        525: "Towtruck",
        526: "Fortune",
        527: "Cadrona",
        528: "FBI Truck",
        529: "Willard",
        530: "Forklift",
        531: "Tractor",
        532: "Combine Harvester",
        533: "Feltzer",
        534: "Remington",
        535: "Slamvan",
        536: "Blade",
        537: "Freight (Train)",
        538: "Brownstreak (Train)",
        539: "Vortex",
        540: "Vincent",
        541: "Bullet",
        542: "Clover",
        543: "Sadler",
        544: "Firetruck LA",
        545: "Hustler",
        546: "Intruder",
        547: "Primo",
        548: "Cargobob",
        549: "Tampa",
        550: "Sunrise",
        551: "Merit",
        552: "Utility Van",
        553: "Nevada",
        554: "Yosemite",
        555: "Windsor",
        556: "Monster A",
        557: "Monster B",
        558: "Uranus",
        559: "Jester",
        560: "Sultan",
        561: "Stratum",
        562: "Elegy",
        563: "Raindance",
        564: "RC Tiger",
        565: "Sport Vehicles",
        566: "Tahoma",
        567: "Savanna",
        568: "Bandito",
        569: "Freight Flat Trailer (Train)",
        570: "Streak Trailer (Train)",
        571: "Kart",
        572: "Mower",
        573: "Dune",
        574: "Sweeper",
        575: "Broadway",
        576: "Tornado",
        577: "AT400",
        578: "DFT-30",
        579: "Huntley",
        580: "Stafford",
        581: "BF-400",
        582: "Newsvan",
        583: "Tug",
        584: "Petrol Trailer",
        585: "Emperor",
        586: "Wayfarer",
        587: "Euros",
        588: "Hotdog",
        589: "Club",
        590: "Freight Box Trailer (Train)",
        591: "Article Trailer 3",
        592: "Andromada",
        593: "Dodo",
        594: "RC Cam",
        595: "Launch",
        596: "Police Car (LSPD)",
        597: "Police Car (SFPD)",
        598: "Police Car (LVPD)",
        599: "Police Ranger",
        600: "Picador",
        601: "S.W.A.T.",
        602: "Alpha",
        603: "Phoenix",
        604: "Glendale Shit",
        605: "Sadler Shit",
        606: "Baggage Trailer A",
        607: "Baggage Traile B",
        608: "Tug Stairs Trailer",
        609: "Tug Stairs Trailer",
        610: "Landstalker"
 
    }
    
    try:
        # Crear un objeto cursor para ejecutar consultas SQL
        cursor = cnx.cursor()

        # Ejecutar la consulta SQL para obtener los datos del jugador
        query = "SELECT id FROM player WHERE name = %s AND user_pin = %s"
        cursor.execute(query, (name, pin))
        result = cursor.fetchone()

        # Verificar si se obtuvo algún resultado de la consulta
        if result is None:
            # Mostrar un mensaje de error si el jugador no está registrado
            await ctx.author.send("Esta cuenta no está registrada o el pin es incorrecto.")
        else:
            # Ejecutar la consulta SQL para obtener los vehículos del jugador
            query = "SELECT modelid FROM pvehicles WHERE id_player = %s"
            cursor.execute(query, (result[0],))
            results = cursor.fetchall()

            # Verificar si se obtuvieron resultados de la consulta
            if len(results) == 0:
                # Mostrar un mensaje de error si el jugador no tiene vehículos
                await ctx.send(f"{name} no tiene vehículos.")
            else:
                # Mostrar los vehículos del jugador
                embed = discord.Embed(title="Vehículos de " + name, color=0x47049C)
                for result in results:
                    vehicle_name = vehicle_names.get(result[0], "Desconocido")
                    embed.add_field(name="\u200b", value=vehicle_name)
                await ctx.send(embed=embed)

        # Eliminar el mensaje del usuario que invocó el comando
        await ctx.message.delete()

    except mysql.connector.Error as err:
        # Mostrar un mensaje de error si ocurre un error al ejecutar la consulta SQL
        await ctx.send(f"Error: {err.msg}")



    finally:
        # Cerrar el cursor
        cursor.close()


@bot.command()
async def inv(ctx, name: str, pin: str):
    if ctx.channel.id != 1081993572515053650:
        return    
    try:
        # Crear un objeto cursor para ejecutar consultas SQL
        cursor = cnx.cursor()

        # Ejecutar la consulta SQL para obtener los datos del jugador
        query = "SELECT * FROM player WHERE name = %s AND user_pin = %s"
        cursor.execute(query, (name, pin))
        result = cursor.fetchone()

        # Verificar si se obtuvo algún resultado de la consulta
        if result is None:
            # Mostrar un mensaje de error si el jugador no está registrado
            await ctx.author.send("Esta cuenta no está registrada o el pin es incorrecto.")
        elif len(result) > 0:         
            # Crear un objeto Embed y mostrar los datos del jugador
            embed = discord.Embed(title="Inventario del Jugador", color=0x47049C)
            estado = "Tienes DNI " if result[45] != 0 else "No tienes DNI"
            embed.add_field(name="DNI", value=estado)   
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="\u200b", value="\u200b")         
            estado = "Tienes GPS " if result[49] == 1 else "No tienes GPS" 
            embed.add_field(name="GPS", value=estado)     
            embed.add_field(name="\u200b", value="\u200b") # Agregar un campo con valores vacíos
            embed.add_field(name="\u200b", value="\u200b") # Agregar un campo con valores vacíos                   
            estado = "Tienes MP3 " if result[53] == 1 else "No tienes MP3"
            embed.add_field(name="MP3", value=estado) 
            embed.add_field(name="\u200b", value="\u200b") # Agregar un campo con valores vacíos
            embed.add_field(name="\u200b", value="\u200b") # Agregar un campo con valores vacíos
            estado = "Tienes Estereo " if result[55] == 1 else "No tienes Estereo"
            embed.add_field(name="Estereo", value=estado) 
            embed.add_field(name="\u200b", value="\u200b") # Agregar un campo con valores vacíos
            embed.add_field(name="\u200b", value="\u200b") # Agregar un campo con valores vacíos                
            embed.add_field(name="Medicamentos ", value=result[61])
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="Marihuana", value=result[62])
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="\u200b", value="\u200b")              
            embed.add_field(name="Crack ", value=result[63])                                            
            await ctx.send(embed=embed)

            # Eliminar el mensaje del usuario que invocó el comando
            await ctx.message.delete()

    except mysql.connector.Error as err:
        # Mostrar un mensaje de error si ocurre un error al ejecutar la consulta SQL
        await ctx.send(f"Error: {err.msg}")

    finally:
        # Cerrar el cursor
        cursor.close()



# Definir el comando cuenta
@bot.command()
async def cuenta(ctx, name: str, pin: str):
    if ctx.channel.id != 1081993572515053650:
        return    
    try:
        # Crear un objeto cursor para ejecutar consultas SQL
        cursor = cnx.cursor()

        # Ejecutar la consulta SQL para obtener los datos del jugador
        query = "SELECT * FROM player WHERE name = %s AND user_pin = %s"
        cursor.execute(query, (name, pin))
        result = cursor.fetchone()

        # Verificar si se obtuvo algún resultado de la consulta
        if result is None:
            # Mostrar un mensaje de error si el jugador no está registrado
            await ctx.author.send("Esta cuenta no está registrada o el pin es incorrecto.")
        elif len(result) > 0:
            vida = result[31]
            chaleco = result[32]
            hambre = result[34]
            sed = result[35]
            # convertir los valores flotantes a enteros
            vida_entero = int(vida)
            chaleco_entero = int(chaleco)                
            hambre_entero = int(hambre)
            sed_entero = int(sed)            
            # Crear un objeto Embed y mostrar los datos del jugador
            embed = discord.Embed(title="Cuenta", color=0x47049C)
            embed.add_field(name="Nombre del usuario", value=result[1])
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="\u200b", value="\u200b")
            estado = "Masculino :man_beard::skin-tone-1: " if result[33] == 1 else "Femenino :woman::skin-tone-1:"
            embed.add_field(name="Género :restroom:", value=estado)   
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="\u200b", value="\u200b")         
            embed.add_field(name="Nivel :chart_with_upwards_trend: ", value=result[11])
            embed.add_field(name="\u200b", value="\u200b") # Agregar un campo con valores vacíos
            embed.add_field(name="\u200b", value="\u200b") # Agregar un campo con valores vacíos            
            embed.add_field(name="Vida :heart: ", value=vida_entero)  
            embed.add_field(name="\u200b", value="\u200b") # Agregar un campo con valores vacíos
            embed.add_field(name="\u200b", value="\u200b") # Agregar un campo con valores vacíos
            embed.add_field(name="Chaleco :shield: ", value=chaleco_entero)  
            embed.add_field(name="\u200b", value="\u200b") # Agregar un campo con valores vacíos
            embed.add_field(name="\u200b", value="\u200b") # Agregar un campo con valores vacíos         
            embed.add_field(name="Hambre :pizza:", value=hambre_entero)
            embed.add_field(name="\u200b", value="\u200b") # Agregar un campo con valores vacíos
            embed.add_field(name="\u200b", value="\u200b") # Agregar un campo con valores vacíos            
            embed.add_field(name="Sed :cup_with_straw: ", value=sed_entero)            
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="\u200b", value="\u200b")         
            embed.add_field(name="Dinero en Mano :dollar: ", value=result[22])
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="\u200b", value="\u200b")  
            embed.add_field(name="Gemas :gem: ", value=result[20])                                            
            await ctx.send(embed=embed)

            # Eliminar el mensaje del usuario que invocó el comando
            await ctx.message.delete()

    except mysql.connector.Error as err:
        # Mostrar un mensaje de error si ocurre un error al ejecutar la consulta SQL
        await ctx.send(f"Error: {err.msg}")

    finally:
        # Cerrar el cursor
        cursor.close()

# Definir la lista de colores válidos para el autocompletado
def valid_colors():
    return ["#ffffff", "#000000", "#ff0000", "#00ff00", "#0000ff"]


# Definir el comando cembed con subcomando color
@bot.command()
async def cembed(ctx, arg1: str = None, *, arg2: str = None):
    # Verificar si el subcomando es "color" o "c"
    if arg1 == 'color' or arg1 == 'c':
        if arg2.startswith('#'):
            arg2 = arg2[1:]
        # Mostrar los colores válidos que comienzan con el prefijo proporcionado
        await ctx.send('\n'.join([color for color in valid_colors() if color.startswith(arg2)]))
    else:
        try:
            # Verificar que el color comience con "#" y tenga 6 caracteres
            if not arg1.startswith('#') or len(arg1) != 7:
                raise ValueError('Color inválido')
            
            # Verificar que el mensaje tenga menos de 2000 caracteres
            if len(arg2) > 2000:
                raise ValueError('El mensaje es demasiado largo')
            
            # Crear el objeto Embed
            embed = discord.Embed(description=arg2, color=discord.Color(int(arg1[1:], 16)))
            
            # Enviar el Embed al canal
            await ctx.send(embed=embed)
        except ValueError as e:
            # Mostrar un mensaje de error y la sintaxis correcta
            await ctx.send(f'{e}\nLa sintaxis correcta para el comando es: /cembed <color ejem #160756> <mensaje>')
            

# Mostrar un mensaje de comando inválido y la sintaxis correcta
@cembed.error
async def cembed_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Comando inválido. La sintaxis correcta para el comando es: /cembed <color ejem #160756> <mensaje>')

# Manejar el error CommandNotFound para que no muestre nada en la consola
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass



# Corre el bot con el token de tu aplicación de Discord
bot.run('MTAyMjE4MDk0NjQ0OTAxMDY4OA.GZ5wBN.9ezJF0LfTdudEOAwQqJ2w4kNiJcLCLcu6Ov6tk')
