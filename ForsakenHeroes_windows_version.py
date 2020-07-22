from tkinter import *
import collections
import winsound
import random
import pickle
import sys

# Author: Dragos Petrut Marin

dirx_rev = [1, 0, -1, 0, 1, 1, -1, -1]
diry_rev = [0, -1, 0, 1, 1, -1, 1, -1]

dirx = [-1, 0, 1, 0, -1, -1, 1, 1]
diry = [0, 1, 0, -1, -1, 1, -1, 1]
klist = [0, 1, 2, 3, 4, 5, 6, 7]

targetLocation = []
heroLocation = []
nth = 0

# Delete an item (enemy or wall)


def deleteMonster(item):
    global nothingnessPNG, player

    pos = canvas.coords(item)
    grid[int(pos[0])][int(pos[1])] = 0
    # Replace current image on (x, y) with "nothingness" (i.e. black square)
    canvas.create_image(pos[0], pos[1], image=nothingnessPNG)

    for mob in monster:
        if (mob.killed == 0):
            canvas.tag_raise(mob)
    canvas.tag_raise(player.player)


def deleteTarget(item):
    global nothingnessPNG, player

    pos = canvas.coords(item)
    # Replace current image on (x, y) with "nothingness" (i.e. black square)
    canvas.create_image(pos[0], pos[1], image=nothingnessPNG)

    for mob in monster:
        if (mob.killed == 0):
            canvas.tag_raise(mob)
    canvas.tag_raise(player.player)


def deleteWall(item):
    global nothingnessPNG, player

    pos = canvas.coords(item)
    # Replace current image on (x, y) with "nothingness" (i.e. black square)
    canvas.create_image(pos[0], pos[1], image=nothingnessPNG)

    for mob in monster:
        if (mob.killed == 0):
            canvas.tag_raise(mob)
    canvas.tag_raise(player.player)

# Improve readability


def typeGrid(x, y):
    return grid[int(x)][int(y)]


def isBlocked(x, y):
    return block[int(x)][int(y)]


def getManhattanDistance(x, y):
    global heroLocation
    return abs(x - heroLocation[0]) + abs(y - heroLocation[1])

# sorted(monster, key = sortManhattanDistance)


def sortManhattanDistance(monst):
    global heroLocation

    pos = canvas.coords(monst.enemy)
    return abs(pos[0] - heroLocation[0]) + abs(pos[1] - heroLocation[1])

# Check if (x, y) could lead to a better distance


def afterMove(x, y):
    global playerSize

    best = getManhattanDistance(x, y)
    for k in range(8):
        nx = int(x + dirx[k] * playerSize)
        ny = int(y + diry[k] * playerSize)
        distance = getManhattanDistance(nx, ny)
        if(grid[nx][ny] == 0 and block[nx][ny] == 0 and best > distance):
            return 1
    return 0


def notImmovable():
    global player

    pos = canvas.coords(player.player)
    block[int(pos[0])][int(pos[1])] = 0

# Updates Hero's current position


def updatePos():
    global player, heroLocation

    heroLocation = canvas.coords(player.player)
    block[int(heroLocation[0])][int(heroLocation[1])] = 1


def undoPreviousMove():
    global player, playerSize

    choice = -1
    # undo the previous move action
    if (direction == "left"):
        notImmovable()
        canvas.move(player.player, playerSize, 0)
        choice = 2
    elif (direction == "right"):
        notImmovable()
        canvas.move(player.player, -playerSize, 0)
        choice = 0
    elif (direction == "up"):
        notImmovable()
        canvas.move(player.player, 0, playerSize)
        choice = 1
    elif (direction == "down"):
        notImmovable()
        canvas.move(player.player, 0, -playerSize)
        choice = 3

    # Record the move
    playerEvents.append([realTime, choice])
    updatePos()


# Use OOP to define the attributes and behavior of a "monster" object
class Monster:
    def __init__(self, health, damage, killed, random, index, enemy):
        self.health = health
        self.damage = damage
        self.killed = killed
        self.random = random
        self.index = index
        self.enemy = enemy

    def getDistanceFromHero(self):
        pos = canvas.coords(self.enemy)
        return getManhattanDistance(pos[0], pos[1])

    def move(self):
        global realTime, heroLocation, playerSize

        canvas.tag_raise(self.enemy)

        pos = canvas.coords(self.enemy)
        grid[int(pos[0])][int(pos[1])] = 0

        choice = -1
        best = getManhattanDistance(pos[0], pos[1])
        for k in range(8):
            if(self.random == 1):
                k = 7 - k
            nx = int(pos[0] + dirx[k] * playerSize)
            ny = int(pos[1] + diry[k] * playerSize)
            distance = getManhattanDistance(nx, ny)

            if (grid[nx][ny] == 0 and block[nx][ny] == 0):
                if (best > distance):
                    best = distance
                    choice = k
                elif (best == distance and afterMove(nx, ny)):
                    choice = k

        if (choice != -1):
            canvas.move(
                self.enemy,
                dirx[choice] *
                playerSize,
                diry[choice] *
                playerSize)
        pos = canvas.coords(self.enemy)
        grid[int(pos[0])][int(pos[1])] = self.index

        # Record the move
        monsterEvents[self.index % 8].append([realTime, choice])

    def undo(self):
        global realTime

        while(1):
            pos = canvas.coords(self.enemy)
            idx = grid[int(pos[0])][int(pos[1])]

            if (len(monsterEvents[idx % 8]) == 0):
                break
            event = monsterEvents[idx % 8].pop()

            if (event[0] != realTime):
                monsterEvents[idx % 8].append(event)
                break
            else:
                choice = event[1]
                if (choice != -1):
                    canvas.move(
                        self.enemy,
                        dirx_rev[choice] *
                        playerSize,
                        diry_rev[choice] *
                        playerSize)

            grid[int(pos[0])][int(pos[1])] = 0
            pos = canvas.coords(self.enemy)
            grid[int(pos[0])][int(pos[1])] = idx


# Use OOP to define the attributes and behavior of a "hero" object
# Also make a child class for each type of hero
class Hero:
    def __init__(self, health, damage, power, player):
        self.health = health
        self.damage = damage
        self.power = power
        self.player = player

    def immovable(self):
        global heroLocation

        pos = canvas.coords(self.player)
        block[int(pos[0])][int(pos[1])] = 1
        heroLocation = canvas.coords(self.player)

    # move player left, right, up, down if it doesn't leave the grid
    def move(self):
        global past_dir, heroLocation

        choice = -1
        pos = canvas.coords(self.player)
        block[int(pos[0])][int(pos[1])] = 0
        if direction == "left" and past_dir != "left" and block[int(
                pos[0] - playerSize)][int(pos[1])] != 1:
            canvas.move(self.player, -playerSize, 0)
            past_dir = "left"
            choice = 0

        elif direction == "right" and past_dir != "right":
            if block[int(pos[0] + playerSize)][int(pos[1])] != 1:
                canvas.move(self.player, playerSize, 0)
                past_dir = "right"
                choice = 2

        elif direction == "up" and past_dir != "up":
            if block[int(pos[0])][int(pos[1] - playerSize)] != 1:
                canvas.move(self.player, 0, -playerSize)
                past_dir = "up"
                choice = 3

        elif direction == "down" and past_dir != "down":
            if block[int(pos[0])][int(pos[1] + playerSize)] != 1:
                canvas.move(self.player, 0, playerSize)
                past_dir = "down"
                choice = 1

        canvas.tag_raise(self.player)
        updatePos()

        # Record the move
        playerEvents.append([realTime, choice])

    def collision(self):
        global target, targets_left, alive, chrono, realTime, stopPower

        pos = canvas.coords(self.player)

        # check collision with a target
        mytarget = canvas.coords(target)
        if mytarget[0] == pos[0] and mytarget[1] == pos[1]:
            # Record deletion of a target
            targetEvents.append(
                [0, realTime - 1, int(mytarget[0]), int(mytarget[1])])

            targets_left = targets_left - 1
            deleteTarget(target)

            if(targets_left > 0):
                placeTarget()

            # Record creation of a target
            mytarget = canvas.coords(target)
            targetEvents.append(
                [1, realTime, int(mytarget[0]), int(mytarget[1])])

        # check collision with a wall of the labyrinth
        if wall[int(pos[0])][int(pos[1])] > 0:

            if (chrono == stopPower):
                # Only for King Crimson
                wall[int(pos[0])][int(pos[1])] = 0
            else:
                wall[int(pos[0])][int(pos[1])] = wall[int(
                    pos[0])][int(pos[1])] - self.damage
                # Record hitting of wall
                wallEvents.append([realTime - 1, int(pos[0]), int(pos[1])])

            if (wall[int(pos[0])][int(pos[1])] <= 0):
                deleteWall(barrier[shape[int(pos[0])][int(pos[1])]])
            else:
                undoPreviousMove()

        pos = canvas.coords(player.player)

        # check collision with a monster
        idx = typeGrid(pos[0], pos[1])
        if idx > 0:
            mob = monster[idx - 1]

            mob.health = mob.health - self.damage
            if (chrono == stopPower):
                # Only for King Crimson
                mob.health = 0
            if (mob.health <= 0):
                # Record deletion of a monster
                monsterHit.append(
                    [0, realTime - 1, int(pos[0]), int(pos[1]), idx])

                mob.killed = 1
                alive = alive - 1
                deleteMonster(mob.enemy)
            else:
                undoPreviousMove()

    def undo(self):
        global realTime

        while(1):
            if (len(playerEvents) == 0):
                break

            pos = canvas.coords(self.player)
            block[int(pos[0])][int(pos[1])] = 0

            event = playerEvents.pop()
            if (event[0] != realTime):
                playerEvents.append(event)
                break
            else:
                choice = event[1]
                if (choice != -1):
                    canvas.move(
                        self.player,
                        dirx_rev[choice] *
                        playerSize,
                        diry_rev[choice] *
                        playerSize)

            canvas.tag_raise(self.player)
            updatePos()


class StarPlatinum(Hero):

    def __init__(
        self,
        health,
        damage,
        power,
        player): super().__init__(
        health,
        damage,
        power,
        player)

    def immovable(self): super().immovable()

    def move(self): super().move()

    def collision(self): super().collision()

    def firstEffect(self): winsound.PlaySound(
        'timeStop.wav', winsound.SND_ALIAS | winsound.SND_ASYNC)

    def secondEffect(self): winsound.PlaySound(
        'timeStart.wav', winsound.SND_ALIAS | winsound.SND_ASYNC)


class KingCrimson(Hero):

    def __init__(
        self,
        health,
        damage,
        power,
        player): super().__init__(
        health,
        damage,
        power,
        player)

    def immovable(self): super().immovable()

    def move(self): super().move()

    def collision(self): super().collision()

    def firstEffect(self): winsound.PlaySound(
        'timeErase.wav', winsound.SND_ALIAS | winsound.SND_ASYNC)

    def secondEffect(self): winsound.PlaySound(
        'timeLeap.wav', winsound.SND_ALIAS | winsound.SND_ASYNC)


class Mandom(Hero):

    def __init__(
        self,
        health,
        damage,
        power,
        player): super().__init__(
        health,
        damage,
        power,
        player)

    def immovable(self): super().immovable()

    def move(self): super().move()

    def collision(self): super().collision()

    def firstEffect(self): winsound.PlaySound(
        'timeWillRevert.wav', winsound.SND_ALIAS | winsound.SND_ASYNC)

    def secondEffect(self): winsound.PlaySound(
        'timeWasReverted.wav',
        winsound.SND_ALIAS | winsound.SND_ASYNC)


class CrazyDiamond(Hero):

    def __init__(
        self,
        health,
        damage,
        power,
        player): super().__init__(
        health,
        damage,
        power,
        player)

    def immovable(self): super().immovable()

    def move(self): super().move()

    def collision(self): super().collision()

    def effect(self): winsound.PlaySound(
        'healing.wav', winsound.SND_ALIAS | winsound.SND_ASYNC)


def spaceBar(event):
    global interface, health, player, chrono, notStarted, superPower
    global startPower, stopPower, beginX, beginY, heroLocation, powerful
    global pause, pausedTime, boss, bossTime, inMenu, resumeTime

    if (boss == 1 or bossTime > 0):
        return
    if (pause == 1 or pausedTime > 0):
        return
    if (inMenu == 1 or resumeTime > 0):
        return
    if (notStarted == 1):
        return

    # Time Manipulation
    if (isinstance(player, KingCrimson) or isinstance(
            player, StarPlatinum) or isinstance(player, Mandom)):
        if (superPower == 0 and player.power > 0):
            canvas.itemconfig(interface, fill="blue")
            player.firstEffect()
            superPower = 1
            startPower = chrono
            stopPower = chrono + 10 * player.power
            beginX = heroLocation[0]
            beginY = heroLocation[1]

            if (powerful == 1):
                stopPower = 2 ** 30
        elif (superPower == 1 and chrono - startPower >= 10):
            canvas.itemconfig(interface, fill="maroon")
            player.secondEffect()
            superPower = 0
            startPower = 0
            stopPower = chrono

    if (isinstance(player, CrazyDiamond)):
        if (player.power > 0 and health != player.health):
            player.effect()

            stopPower = chrono
            if (powerful == 0):
                player.power = player.power - 1
            if (health + 10 > player.health):
                health = player.health
            else:
                health = health + 10


def cheatPass(event):
    global passLevel
    passLevel = 1


def cheatHealth(event):
    global immune
    immune = 1 - immune


def cheatPower(event):
    global powerful, startPower, stopPower
    powerful = 1 - powerful


def leftKey(event):
    global direction, past_dir
    past_dir = ""
    direction = "left"


def rightKey(event):
    global direction, past_dir
    past_dir = ""
    direction = "right"


def upKey(event):
    global direction, past_dir
    past_dir = ""
    direction = "up"


def downKey(event):
    global direction, past_dir
    past_dir = ""
    direction = "down"


def returnKey(event):
    global STOP
    STOP = 1 - STOP


def pauseKey(event):
    global pause, pausedTime, inMenu, boss

    if (boss == 1 or inMenu == 1):
        return

    pause = 1 - pause
    if (pause == 1):
        pausedTime = 40


def bossKey(event):
    global boss, bossTime, hideGame, hidePNG, width, height, level, notStarted
    global epitah, epitah_window, pause, pausedTime, inMenu, resumeTime

    boss = 1 - boss
    if (boss == 1):
        window.title("Mozilla Firefox")
        epitah = Button(window, image=hidePNG, command=None, anchor=W)
        epitah.configure(width=width, activebackground="maroon", relief=FLAT)
        epitah_window = canvas.create_window(0, 0, anchor=NW, window=epitah)

        winsound.PlaySound(None, winsound.SND_ALIAS | winsound.SND_ASYNC)
        music = 0
    else:
        if (notStarted == 0):
            pause = 1
            pausedTime = 40

        canvas.delete(epitah_window)
        window.title("My Game")


def goToIntroMenu():
    global goIntro
    goIntro = 1


def willSaveSession():
    global willSave, saveSession_window
    willSave = 1

    size = 250
    canvas.delete(saveSession_window)
    saveSession = Button(window, image=gameSavedPNG, command=None, anchor=W)
    saveSession.configure(width=400, activebackground="maroon", relief=FLAT)
    saveSession_window = canvas.create_window(
        width / 2 - 400 / 2,
        height / 2 + size - 450,
        anchor=NW,
        window=saveSession)


def escapeKey(event):
    global fastMenu, width, height, littleMenu, inMenu, resumeTime, pause
    global boss, quitGame_window, quitGame, mainMenu_window, mainMenu
    global saveSession_window, saveSession, pre

    if (boss == 1 or pre == 1):
        return

    size = 250
    fastMenu = 1 - fastMenu
    if (fastMenu == 1):
        inMenu = 1

        littleMenu = canvas.create_rectangle(
            width / 2 - size,
            height / 2 - size,
            width / 2 + size,
            height / 2 + size,
            fill="maroon",
            outline="maroon")

        # Save Game
        saveSession = Button(
            window,
            image=savePNG,
            command=lambda: willSaveSession(),
            anchor=W)
        saveSession.configure(
            width=400,
            activebackground="maroon",
            relief=FLAT)
        saveSession_window = canvas.create_window(
            width / 2 - 400 / 2,
            height / 2 + size - 450,
            anchor=NW,
            window=saveSession)

        # Go back to Intro Menu
        mainMenu = Button(
            window,
            image=mainMenuPNG,
            command=lambda: goToIntroMenu(),
            anchor=W)
        mainMenu.configure(width=400, activebackground="maroon", relief=FLAT)
        mainMenu_window = canvas.create_window(
            width / 2 - 400 / 2,
            height / 2 + size - 300,
            anchor=NW,
            window=mainMenu)

        # Quit Game
        quitGame = Button(
            window,
            image=quitPNG,
            command=lambda: exitGame(),
            anchor=W)
        quitGame.configure(width=400, activebackground="maroon", relief=FLAT)
        quitGame_window = canvas.create_window(
            width / 2 - 400 / 2,
            height / 2 + size - 150,
            anchor=NW,
            window=quitGame)
    else:
        inMenu = 0
        canvas.delete(littleMenu)
        canvas.delete(saveSession_window)
        canvas.delete(mainMenu_window)
        canvas.delete(quitGame_window)


def Update3():
    global t3, time3PNG

    time3PNG = PhotoImage(file="startTime3.png")
    t3 = canvas.create_image(
        width / 2,
        height / 6 + height / 4,
        image=time3PNG)


def Update2():
    global t2, time2PNG

    time2PNG = PhotoImage(file="startTime2.png")
    t2 = canvas.create_image(
        width / 2,
        height / 6 + height / 4,
        image=time2PNG)


def Update1():
    global t1, time1PNG

    time1PNG = PhotoImage(file="startTime1.png")
    t1 = canvas.create_image(
        width / 2,
        height / 6 + height / 4,
        image=time1PNG)


def Go():
    global go, goPNG

    goPNG = PhotoImage(file="go.png")
    go = canvas.create_image(width / 2, height / 6 + height / 4, image=goPNG)


def GamePaused():
    global pausedGame, pausedPNG

    pausedPNG = PhotoImage(file="paused.png")
    pausedGame = canvas.create_image(
        width / 2, height / 6 + height / 4, image=pausedPNG)


def RemovePaused():
    global pausedGame

    canvas.delete(pausedGame)


def Remove123():
    global t1, t2, t3, go

    canvas.delete(t1)
    canvas.delete(t2)
    canvas.delete(t3)
    canvas.delete(go)


def findCoordinates(item):
    pos = canvas.coords(item)
    return pos


def AbilityBar():
    global width, capacity, player, bars, fullBarPNG, emptyBarPNG

    for bar in bars:
        canvas.delete(bar)

    last = width / 7 - 6 * capacity + 160
    for i in range(player.power):
        bars.append(canvas.create_image(last, 60, image=fullBarPNG))
        last = last + 45

    for i in range(capacity - player.power):
        bars.append(canvas.create_image(last, 60, image=emptyBarPNG))
        last = last + 45


def noPower():
    global player, realTime, health, playerSize, immune

    for i in range(len(monster)):
        mob = monster[i]
        if (mob.killed == 1):
            continue
        direction = mob.move()

        if (mob.getDistanceFromHero() == playerSize):
            wait[i] = wait[i] + 1
        if (wait[i] % 6 == 5):
            if (immune == 0):
                health = health - mob.damage
                healthEvents.append([realTime - 1, mob.damage])
        if (health < 0):
            health = 0

        if (isinstance(player, Mandom)):
            pos = canvas.coords(mob.enemy)
            X = int(pos[0])
            Y = int(pos[1])

            idx = grid[X][Y] % 8
            if(len(monsterEvents[idx]) > 120):
                monsterEvents[idx].popleft()


def EraseTime(x, y):
    global player, health, playerSize, heroLocation

    heroLocation[0] = x
    heroLocation[1] = y
    block[x][y] = 1
    for i in range(len(monster)):
        mob = monster[i]
        if (mob.killed == 0):
            mob.move()

    block[x][y] = 0


def ReverseTimeMonsters():
    global player, playerSize, realTime, alive

    for i in range(len(monster)):
        mob = monster[i]
        if (mob.killed == 1):
            continue
        mob.undo()

    while(1):
        if (len(monsterHit) == 0):
            break

        event = monsterHit.pop()
        if (event[1] != realTime):
            monsterHit.append(event)
            break
        elif (event[0] == 0):
            X = event[2]
            Y = event[3]
            idx = event[4]

            monster[idx - 1] = Monster(1,
                                       3,
                                       0,
                                       random.randint(0,
                                                      1),
                                       idx,
                                       canvas.create_image(X,
                                                           Y,
                                                           image=monsterPNG))
            wait[idx - 1] = 0
            grid[X][Y] = idx
            alive = alive + 1

        elif (event[0] == 1):
            idx = event[2]
            mob = monster[idx - 1]

            pos = canvas.coords(mob.enemy)
            monsterToBeSpawned.append([int(pos[0]), int(pos[1]), idx])

            mob.killed = 1
            deleteMonster(mob.enemy)
            alive = alive - 1

    for i in range(len(monster)):
        mob = monster[i]
        if (mob.killed == 1):
            continue
        mob.undo()


def ReverseTimePlayer():
    global player

    player.undo()


def ReverseTimeHealth():
    global player, realTime, health

    while(1):
        if (len(healthEvents) == 0):
            break

        event = healthEvents.pop()
        if (event[0] != realTime):
            healthEvents.append(event)
            break
        else:
            health = health + event[1]


def ReverseTimeWall():
    global player, realTime, wallPNG

    while(1):
        if (len(wallEvents) == 0):
            break

        event = wallEvents.pop()
        if (event[0] != realTime):
            wallEvents.append(event)
            break
        else:
            X = event[1]
            Y = event[2]

            if (wall[X][Y] <= 0):
                canvas.create_image(X, Y, image=wallPNG)
            canvas.tag_raise(player.player)
            wall[X][Y] = wall[X][Y] + player.damage


def ReverseTimeTarget():
    global realTime, target, targetPNG, targets_left

    while(1):
        if (len(targetEvents) == 0):
            break

        event = targetEvents.pop()
        if (event[1] != realTime):
            targetEvents.append(event)
            break
        elif (event[0] == 0):
            X = event[2]
            Y = event[3]

            target = canvas.create_image(X, Y, image=targetPNG)
            targetLocation = canvas.coords(target)
            targets_left = targets_left + 1
        elif (event[0] == 1):
            X = event[2]
            Y = event[3]

            targetToBeSpawned.append([X, Y])
            deleteTarget(target)


def ReverseTimeExplosion():
    global realTime, objexp, exploding, wallPNG, explosionPNG

    while(1):
        if (len(explosionEvents) == 0):
            break

        event = explosionEvents.pop()
        if (event[1] != realTime):
            explosionEvents.append(event)
            break
        elif (event[0] == 0):
            X = event[2]
            Y = event[3]

            canvas.delete(objexp)
            objexp = canvas.create_image(X, Y, image=explosionPNG)
        elif (event[0] == 1):
            X = event[2]
            Y = event[3]

            canvas.delete(objexp)
            objexp = canvas.create_image(X, Y, image=wallPNG)
        elif (event[0] == 2):
            X = event[2]
            Y = event[3]
            ToBeDetonated.append([realTime + 1, X, Y])

            exploding = 0

            canvas.delete(objexp)
            objexp = canvas.create_image(X, Y, image=wallPNG)


def ReverseTimeExplodingTime():
    global realTime, explodingTime

    while(1):
        if (len(explodingTimeEvents) == 0):
            break

        event = explodingTimeEvents.pop()
        if (event[0] != realTime):
            explodingTimeEvents.append(event)
            break
        else:
            explodingTime = event[1]


def ReverseTime():
    global realTime, timeLeft

    while(1):
        if (len(timeEvents) == 0):
            break

        event = timeEvents.pop()
        if (event != realTime):
            timeEvents.append(event)
            break
        else:
            timeLeft = timeLeft + 1


def detonate(A, B):
    global heroLocation, player, health, alive, immune, realTime, chrono

    alreadyHitPlayer = 0
    for distance in range(1, 4):                       # Manhattan Distance
        for i in range(0, distance + 1):
            j = distance - i

            for k in range(4, 8):
                X = int(A + dirx[k] * i * playerSize)
                Y = int(B + diry[k] * j * playerSize)

                if (grid[X][Y] > 0):
                    idx = grid[X][Y]
                    mob = monster[idx - 1]

                    # Record deletion of a monster
                    monsterHit.append([0, realTime, X, Y, idx])

                    mob.killed = 1
                    alive = alive - 1
                    deleteMonster(mob.enemy)

                if (superPower == 1 or alreadyHitPlayer == 1 or (
                        isinstance(player, KingCrimson) and
                        chrono - stopPower <= 5)):
                    continue           # King Crimson
                if (heroLocation[0] == X and heroLocation[1] == Y):
                    alreadyHitPlayer = 1

                    if (immune == 0):
                        health = health - (4 - distance) * 10
                        healthEvents.append(
                            [realTime - 1, (4 - distance) * 10])
                        if (health < 0):
                            health = 0


def wallMightExplode():
    global exploding, explodingTime, explosionLocation, explosionPNG
    global objexp, heroLocation, playerSize, realTime

    if (exploding == 0 and len(ToBeDetonated) > 0):
        event = ToBeDetonated.pop()
        if (event[0] != realTime):
            ToBeDetonated.append(event)
        else:
            X = event[1]
            Y = event[2]

            winsound.PlaySound(
                'explosionBefore.wav',
                winsound.SND_ALIAS | winsound.SND_ASYNC)

            canvas.delete(objexp)
            objexp = canvas.create_image(X, Y, image=explosionPNG)
            explosionLocation = canvas.coords(objexp)
            block[X][Y] = 1
            explodingTime = 0
            exploding = 1

            # Mandom
            explosionEvents.append([2, realTime - 1, X, Y])
        return

    if (exploding == 1 or (0 < explodingTime < 18)):
        explodingTime = explodingTime + 1
        X = int(explosionLocation[0])
        Y = int(explosionLocation[1])

        explodingTimeEvents.append([realTime, explodingTime])

        if (explodingTime == 2):
            canvas.delete(objexp)
            objexp = canvas.create_image(X, Y, image=wallPNG)
            explosionEvents.append([0, realTime - 1, X, Y])
        elif (explodingTime == 3):
            canvas.delete(objexp)
            objexp = canvas.create_image(X, Y, image=explosionPNG)
            explosionEvents.append([1, realTime - 1, X, Y])
        elif (explodingTime == 5):
            canvas.delete(objexp)
            objexp = canvas.create_image(X, Y, image=wallPNG)
            explosionEvents.append([0, realTime - 1, X, Y])
        elif (explodingTime == 7):
            canvas.delete(objexp)
            objexp = canvas.create_image(X, Y, image=explosionPNG)
            explosionEvents.append([1, realTime - 1, X, Y])
        elif (explodingTime == 8):
            canvas.delete(objexp)
            canvas.create_image(X, Y, image=nothingnessPNG)
            explosionEvents.append([0, realTime - 1, X, Y])
            canvas.tag_raise(player.player)
            wall[X][Y] = block[X][Y] = 0
            exploding = 0

            detonate(X, Y)
            winsound.PlaySound(
                'explosionAfter.wav',
                winsound.SND_ALIAS | winsound.SND_ASYNC)
    else:
        for distance in range(1, 3):                       # Manhattan Distance
            for i in range(0, distance + 1):
                j = distance - i

                for k in range(4, 8):
                    X = int(heroLocation[0] + dirx[k] * i * playerSize)
                    Y = int(heroLocation[1] + diry[k] * j * playerSize)

                    if (wall[X][Y] > 0 and grid[X][Y] ==
                            0 and testedExplosion[X][Y] + 30 < realTime):
                        if (random.randint(1, 100) <
                                chanceToExplode):   # it will explode
                            winsound.PlaySound(
                                'explosionBefore.wav',
                                winsound.SND_ALIAS | winsound.SND_ASYNC)
                            objexp = canvas.create_image(
                                X, Y, image=explosionPNG)
                            explosionLocation = canvas.coords(objexp)
                            block[X][Y] = 1
                            explodingTime = 0
                            exploding = 1

                            # Mandom
                            explosionEvents.append([2, realTime - 1, X, Y])

                            return
                        else:
                            testedExplosion[X][Y] = realTime


def SaveGame():
    global monsterToBeSpawned, targetToBeSpawned, ToBeDetonated
    global explodingTimeEvents, explosionEvents, targetEvents
    global playerEvents, healthEvents, wallEvents, timeEvents
    global heroLocation, monsterLocation, wallLocation, monster
    global health, score, scoreText, healthText, targetText
    global timeText, realTime, chrono, targets_left, alive
    global block, grid, wall, shape, testedExplosion, chanceToExplode
    global bars, startPower, stopPower, superPower, capacity, beginX
    global beginY, notStarted, powerful, monsterEvents
    global exploding, explodingTime, explosionLocation, objexp
    global barrier, timeLeft, target, targetLocation, interface
    global level, wait, direction, past_dir, init, monsterHit
    global player, myhero

    for mob in monster:
        monsterLocation.append(canvas.coords(mob.enemy))

    wallLocation = []
    for fence in barrier:
        wallLocation.append(canvas.coords(fence))

    with open('train.pickle', 'wb') as f:
        pickle.dump([monsterToBeSpawned,
                     targetToBeSpawned,
                     ToBeDetonated,
                     explodingTimeEvents,
                     explosionEvents,
                     targetEvents,
                     playerEvents,
                     healthEvents,
                     wallEvents,
                     timeEvents,
                     monsterHit,
                     monsterEvents,
                     heroLocation,
                     monsterLocation,
                     wallLocation,
                     monster,
                     health,
                     score,
                     scoreText,
                     healthText,
                     targetText,
                     timeText,
                     targetLocation,
                     level,
                     past_dir,
                     alive,
                     realTime,
                     chrono,
                     targets_left,
                     grid,
                     wall,
                     shape,
                     testedExplosion,
                     chanceToExplode,
                     bars,
                     startPower,
                     timeLeft,
                     target,
                     direction,
                     init,
                     stopPower,
                     superPower,
                     capacity,
                     beginX,
                     beginY,
                     notStarted,
                     powerful,
                     exploding,
                     explodingTime,
                     explosionLocation,
                     objexp,
                     barrier,
                     wait,
                     player,
                     myhero],
                    f)


def LoadGame():
    global monsterToBeSpawned, targetToBeSpawned, ToBeDetonated, immune
    global explosionEvents, targetEvents, playerEvents, healthEvents
    global timeEvents, monsterHit, monsterEvents, explodingTimeEvents
    global heroLocation, monsterLocation, wallLocation, monster, health, score
    global scoreText, healthText, targetText, timeText, realTime, chrono
    global targets_left, wait, direction, past_dir, alive, init, loading
    global block, grid, wall, shape, testedExplosion, chanceToExplode
    global bars, startPower, stopPower, superPower, capacity, beginX
    global beginY, notStarted, powerful, monsterPNG, level, passLevel
    global exploding, explodingTime, explosionLocation, objexp, barrier
    global timeLeft, target, targetLocation, pause, pausedTime, interface
    global wallEvents, player, myhero

    canvas.delete("all")
    createGrid()

    winsound.PlaySound(None, winsound.SND_ASYNC)

    with open('train.pickle', 'rb') as f:
        [monsterToBeSpawned,
         targetToBeSpawned,
         ToBeDetonated,
         explodingTimeEvents,
         explosionEvents,
         targetEvents,
         playerEvents,
         healthEvents,
         wallEvents,
         timeEvents,
         monsterHit,
         monsterEvents,
         heroLocation,
         monsterLocation,
         wallLocation,
         monster,
         health,
         score,
         scoreText,
         healthText,
         targetText,
         timeText,
         targetLocation,
         level,
         past_dir,
         alive,
         realTime,
         chrono,
         targets_left,
         grid,
         wall,
         shape,
         testedExplosion,
         chanceToExplode,
         bars,
         startPower,
         timeLeft,
         target,
         direction,
         init,
         stopPower,
         superPower,
         capacity,
         beginX,
         beginY,
         notStarted,
         powerful,
         exploding,
         explodingTime,
         explosionLocation,
         objexp,
         barrier,
         wait,
         player,
         myhero] = pickle.load(f)

    for i in range(1, len(barrier)):
        X = int(wallLocation[i][0])
        Y = int(wallLocation[i][1])
        if (wall[X][Y] > 0):
            barrier[i] = canvas.create_image(X, Y, image=wallPNG)

    if (myhero == 1):
        player.player = canvas.create_image(
            heroLocation[0], heroLocation[1], image=starPNG)
    elif (myhero == 2):
        player.player = canvas.create_image(
            heroLocation[0], heroLocation[1], image=mandomPNG)
    elif (myhero == 3):
        player.player = canvas.create_image(
            heroLocation[0], heroLocation[1], image=diamondPNG)
    elif (myhero == 4):
        player.player = canvas.create_image(
            heroLocation[0], heroLocation[1], image=kingPNG)

    player.power = capacity
    target = canvas.create_image(
        targetLocation[0],
        targetLocation[1],
        image=targetPNG)

    for i in range(len(monster)):
        if (monster[i].killed == 0):
            monster[i].enemy = canvas.create_image(
                monsterLocation[i][0], monsterLocation[i][1], image=monsterPNG)

    txt = "SCORE: " + str(score)
    scoreText = canvas.create_text(
        startX + 100,
        60,
        fill="white",
        font="Terminal 20",
        text=txt)

    txt = "HEALTH: " + str(health)
    healthText = canvas.create_text(
        width / 2 + width / 3 + 60,
        60,
        fill="white",
        font="Terminal 20",
        text=txt)

    txt = "TARGETS: " + str(targets_left)
    targetText = canvas.create_text(
        width / 2 + width / 6 + 30,
        60,
        fill="white",
        font="Terminal 20",
        text=txt)

    txt = "TIME: " + str(timeLeft)
    timeText = canvas.create_text(
        width / 2,
        60,
        fill="white",
        font="Terminal 20",
        text=txt)

    if (superPower == 1):
        canvas.itemconfig(interface, fill="blue")

    for mob in monster:
        if (mob.killed == 0):
            canvas.tag_raise(mob)
    canvas.tag_raise(player.player)
    updatePos()

    bindKeys()

    # No cheats at first
    passLevel = 0
    powerful = 0
    immune = 0
    STOP = 0

    bars = []
    pause = 1
    pausedTime = 40

    canvas.pack()
    playLevel()


def endGame():
    global restartPNG, submitScorePNG, mainMenuPNG
    global timeLeft, level, score, capacity, init

    unbindKeys()
    canvas.delete("all")
    canvas.create_rectangle(
        0,
        0,
        width,
        height,
        fill="maroon",
        outline="maroon")

    level = 0
    capacity = init

    canvas.create_image(width / 2, height / 6, image=winPNG)

    score = score + 3000 + 10 * timeLeft
    txt = "SCORE: " + str(score)
    canvas.create_text(
        width / 2,
        height / 3,
        fill="white",
        font="Terminal 35",
        text=txt)

    restartGame = Button(
        window,
        image=restartPNG,
        command=lambda: generateLevel(),
        anchor=W)
    restartGame.configure(width=400, activebackground="maroon", relief=FLAT)
    restartGame_window = canvas.create_window(
        width / 5, 13 * height / 24, anchor=NW, window=restartGame)

    submitCurrScore = Button(
        window,
        image=submitScorePNG,
        command=lambda: submitScoreMenu(),
        anchor=W)
    submitCurrScore.configure(
        width=400,
        activebackground="maroon",
        relief=FLAT)
    submitCurrScore_window = canvas.create_window(
        width - width / 5 - 400,
        13 * height / 24,
        anchor=NW,
        window=submitCurrScore)

    # Go back to Intro Menu
    mainMenu = Button(
        window,
        image=mainMenuPNG,
        command=lambda: introMenu(),
        anchor=W)
    mainMenu.configure(width=400, activebackground="maroon", relief=FLAT)
    mainMenu_window = canvas.create_window(
        width / 2 - 400 / 2,
        height - height / 4,
        anchor=NW,
        window=mainMenu)


def playLevel():
    global nextLevRedPNG, gameOverPNG, player, playerSize, health
    global score, scoreText, healthText, targetText, timeText
    global level, chrono, realTime, heroLocation, notStarted, alive
    global startPower, stopPower, superPower, capacity
    global beginX, beginY, notStarted, powerful, interface
    global pause, pausedTime, bossTime, timeLeft
    global inMenu, resumeTime, goIntro, willSave
    global loading

    global STOP

    notStarted = 0

    if (loading == 1):
        loading = 0
        return

    if (willSave == 1):
        willSave = 0
        SaveGame()

        window.after(100, playLevel)
        return

    if (boss == 1):
        window.after(100, playLevel)
        return

    if (goIntro == 1):
        goIntro = 0
        inMenu = 0
        introMenu()
        return

    if (inMenu == 1):
        window.after(100, playLevel)
        return

    if (pause == 1 or pausedTime > 0):
        if (pause == 1):
            GamePaused()
        else:
            if (pausedTime > 30):
                Update3()
            elif (pausedTime > 20):
                Update2()
            elif (pausedTime > 10):
                Update1()
            elif (pausedTime > 0):
                Go()

        if (pause == 0):
            pausedTime = pausedTime - 1
        if (pausedTime == 0):
            Remove123()
            RemovePaused()

        window.after(100, playLevel)
        return

    # Cheat codes
    if (passLevel == 1):
        if (level % 3 == 0 and level < 12):
            capacity = capacity + 2

        if (level == 19):
            endGame()
            return

        nextLevel = Button(
            window,
            image=nextLevRedPNG,
            command=lambda: betweenLevel(),
            anchor=W)
        nextLevel.configure(width=400, activebackground="maroon", relief=FLAT)
        nextLevel_window = canvas.create_window(
            width / 2 - 400 / 2, height / 3, anchor=NW, window=nextLevel)
        notStarted = 1
        return

    if (powerful == 1):
        player.power = capacity

    # Time Manipulation
    # ~ ~ SAME FOR ALL HEROES ~ ~
    if (alive < 0):
        alive = 0
    while (realTime % (40 - 10 * int((level - 1) / 30)) == 0 and STOP == 0 and
           alive < 4 + int(level / 3) and
           (isinstance(player, KingCrimson) == 1 or
            isinstance(player, CrazyDiamond) == 1 or superPower == 0)):
        spawnMonster()

    if (superPower == 1):
        if (chrono >= stopPower and powerful == 0):
            superPower = 0
            stopPower = chrono
            player.secondEffect()
            canvas.itemconfig(interface, fill="maroon")

        if (superPower == 1 and (chrono - startPower) % 10 == 0):
            player.power = player.power - 1

    if (superPower == 0 and player.power < capacity):
        if ((chrono - stopPower + 1) % 30 == 0):
            player.power = player.power + 1
    # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

    if (isinstance(player, KingCrimson)):
        if (superPower == 1 or chrono - stopPower <= 15):
            EraseTime(int(beginX), int(beginY))
        else:
            noPower()
        wallMightExplode()
        player.move()
        realTime = realTime + 1

    if (isinstance(player, StarPlatinum)):
        if (superPower == 0 and chrono - stopPower > 15):
            noPower()
        if (superPower == 0):
            wallMightExplode()
            realTime = realTime + 1

        player.move()

    if (isinstance(player, Mandom)):
        if (superPower == 1):
            ReverseTimeExplodingTime()
            ReverseTimeExplosion()
            ReverseTimeMonsters()
            ReverseTimeTarget()
            ReverseTimePlayer()
            ReverseTimeHealth()
            ReverseTimeWall()
            ReverseTime()
            realTime = realTime - 1

            for mob in monster:
                if (mob.killed == 0):
                    canvas.tag_raise(mob.enemy)
        else:
            noPower()
            player.move()
            wallMightExplode()
            realTime = realTime + 1

            if (len(ToBeDetonated) > 240):
                ToBeDetonated.popleft()
            if (len(playerEvents) > 240):
                playerEvents.popleft()
            if (len(targetEvents) > 240):
                targetEvents.popleft()
            if (len(healthEvents) > 240):
                healthEvents.popleft()
            if (len(wallEvents) > 240):
                wallEvents.popleft()

    if (isinstance(player, CrazyDiamond)):
        noPower()
        wallMightExplode()
        player.move()
        realTime = realTime + 1

    updatePos()
    AbilityBar()

    if (isinstance(player, StarPlatinum) or isinstance(player, CrazyDiamond)):
        player.collision()
    elif (superPower == 0):
        player.collision()

    if (superPower == 0 or isinstance(player, StarPlatinum) == 0):
        if (realTime % 10 == 0):
            if (superPower == 0 or isinstance(player, Mandom) == 0):
                timeLeft = timeLeft - 1
                timeEvents.append(realTime)

    txt = "TIME: " + str(timeLeft)
    canvas.itemconfigure(timeText, text=txt)

    txt = "SCORE: " + str(score)
    canvas.itemconfigure(scoreText, text=txt)

    txt = "HEALTH: " + str(health)
    canvas.itemconfigure(healthText, text=txt)

    txt = "TARGETS: " + str(targets_left)
    canvas.itemconfigure(targetText, text=txt)

    # Game Over
    if (health == 0 or timeLeft == 0):
        gameOver = Button(
            window,
            image=gameOverPNG,
            command=lambda: gameOverMenu(),
            anchor=W)
        gameOver.configure(width=400, activebackground="maroon", relief=FLAT)
        gameOver_window = canvas.create_window(
            width / 2 - 400 / 2, height / 3, anchor=NW, window=gameOver)
    elif (targets_left > 0):
        window.after(100, playLevel)
    else:
        if (level % 3 == 0 and level < 12):
            capacity = capacity + 2

        if (level == 19):
            endGame()
            return

        nextLevel = Button(
            window,
            image=nextLevRedPNG,
            command=lambda: betweenLevel(),
            anchor=W)
        nextLevel.configure(width=400, activebackground="maroon", relief=FLAT)
        nextLevel_window = canvas.create_window(
            width / 2 - 400 / 2, height / 3, anchor=NW, window=nextLevel)
        notStarted = 1

    chrono = chrono + 1


def gameOverMenu():
    global restartPNG, submitScorePNG, mainMenuPNG
    global timeLeft, level, score, capacity, init

    unbindKeys()
    canvas.delete("all")
    canvas.create_rectangle(
        0,
        0,
        width,
        height,
        fill="maroon",
        outline="maroon")

    level = 0
    capacity = init

    txt = "SCORE: " + str(score)
    canvas.create_text(
        width / 2,
        height / 3,
        fill="white",
        font="Terminal 35",
        text=txt)

    restartGame = Button(
        window,
        image=restartPNG,
        command=lambda: generateLevel(),
        anchor=W)
    restartGame.configure(width=400, activebackground="maroon", relief=FLAT)
    restartGame_window = canvas.create_window(
        width / 5, 13 * height / 24, anchor=NW, window=restartGame)

    submitCurrScore = Button(
        window,
        image=submitScorePNG,
        command=lambda: submitScoreMenu(),
        anchor=W)
    submitCurrScore.configure(
        width=400,
        activebackground="maroon",
        relief=FLAT)
    submitCurrScore_window = canvas.create_window(
        width - width / 5 - 400,
        13 * height / 24,
        anchor=NW,
        window=submitCurrScore)

    # Go back to Intro Menu
    mainMenu = Button(
        window,
        image=mainMenuPNG,
        command=lambda: introMenu(),
        anchor=W)
    mainMenu.configure(width=400, activebackground="maroon", relief=FLAT)
    mainMenu_window = canvas.create_window(
        width / 2 - 400 / 2,
        height - height / 4,
        anchor=NW,
        window=mainMenu)


def betweenLevel():
    global score, nextLevBlackPNG, timeLeft, level, capacity

    unbindKeys()
    canvas.delete("all")

    canvas.create_rectangle(
        0,
        0,
        width,
        height,
        fill="maroon",
        outline="maroon")

    txt = "LEVEL " + str(level) + " COMPLETED"
    canvas.create_text(
        width / 2,
        height / 2,
        fill="white",
        font="Terminal 45",
        text=txt)

    txt = "TIME: " + str(timeLeft)
    canvas.create_text(
        width / 2,
        height / 2 + 100,
        fill="white",
        font="Terminal 35",
        text=txt)

    txt = "SCORE: " + str(score) + " + 3000 + " + str(timeLeft * 10)
    canvas.create_text(
        width / 2,
        height / 2 + 180,
        fill="white",
        font="Terminal 35",
        text=txt)

    score = score + 3000 + 10 * timeLeft
    txt = "NEW SCORE: " + str(score)
    canvas.create_text(
        width / 2,
        height / 2 + 300,
        fill="white",
        font="Terminal 35",
        text=txt)

    canvas.pack()

    nextLevBlackPNG = PhotoImage(file="next_black.png")
    nextLevel = Button(
        window,
        image=nextLevBlackPNG,
        command=lambda: generateLevel(),
        anchor=W)
    nextLevel.configure(width=300, activebackground="maroon", relief=FLAT)
    nextLevel_window = canvas.create_window(
        width / 2 - 300 / 2, height / 3, anchor=NW, window=nextLevel)

# Create the grid where the player can move


def createGrid():
    global interface, playerSize, width, height, cX, cY, startX, startY, block

    interface = canvas.create_rectangle(
        0, 0, width, height, fill="maroon", outline="maroon")
    for i in range(width):
        for j in range(height):
            block[i][j] = 1

    cX = int((width - 2 * startX) / playerSize)
    cY = int((height - 2 * 120) / playerSize)
    canvas.create_rectangle(
        startX - half,
        startY - half,
        startX + playerSize * cX + half,
        startY + playerSize * cY + half,
        fill="black",
        outline="black")
    for i in range(startX, startX + playerSize * cX + 1):
        for j in range(startY, startY + playerSize * cY + 1):
            block[i][j] = 0


def spawnMonster():
    global monsterPNG, monster, cX, cY, heroLocation, realTime, alive

    if (len(monsterToBeSpawned) > 0):
        event = monsterToBeSpawned.pop()
        X = event[0]
        Y = event[1]
        idx = event[2]
        alive = alive + 1

        monster[idx - 1] = Monster(1,
                                   3,
                                   0,
                                   random.randint(0,
                                                  1),
                                   idx,
                                   canvas.create_image(X,
                                                       Y,
                                                       image=monsterPNG))
        monsterHit.append([1, realTime, idx])
        wait[idx - 1] = 0
        grid[X][Y] = idx
        return

    cnt = len(monster)
    while(1):
        X = startX + playerSize * random.randint(0, cX)
        Y = startY + playerSize * random.randint(0, cY)
        if ((X == heroLocation[0] and Y == heroLocation[1]) or (
                wall[int(X)][int(Y)] > 0) or (grid[int(X)][int(Y)] > 0)):
            continue

        cnt = cnt + 1
        alive = alive + 1
        grid[int(X)][int(Y)] = cnt
        monsterHit.append([1, realTime, cnt])
        monster.append(
            Monster(
                1, 3, 0, random.randint(
                    0, 1), cnt, canvas.create_image(
                    X, Y, image=monsterPNG)))
        wait.append(0)
        break


def placeMonsters(level):
    global monsterPNG, monster, cX, cY, heroLocation, wait, alive, realTime

    cnt = 0
    alive = 0
    wait = []
    monster = []
    while (cnt < 4 + int(level / 3)):
        X = startX + playerSize * random.randint(0, cX)
        Y = startY + playerSize * random.randint(0, cY)
        if ((X == heroLocation[0] and Y == heroLocation[1]) or (
                wall[int(X)][int(Y)] > 0) or (grid[int(X)][int(Y)] > 0)):
            continue

        cnt = cnt + 1
        alive = alive + 1
        grid[int(X)][int(Y)] = cnt
        monsterHit.append([1, realTime, cnt])
        monster.append(
            Monster(
                1, 3, 0, random.randint(
                    0, 1), cnt, canvas.create_image(
                    X, Y, image=monsterPNG)))
        wait.append(0)


def placeLabyrinth(level):
    global wallPNG, barrier, cX, cY, heroLocation, targetLocation

    cnt = 0
    barrier = [0]
    while (cnt < 400 + 7 * min(level, 11)):
        X = startX + playerSize * random.randint(0, cX)
        Y = startY + playerSize * random.randint(0, cY)
        if(X == heroLocation[0] and Y == heroLocation[1]):
            continue
        if(X == targetLocation[0] and Y == targetLocation[1]):
            continue

        cnt = cnt + 1
        shape[int(X)][int(Y)] = cnt
        wall[int(X)][int(Y)] = 25 + min(5 * level, 75)
        barrier.append(canvas.create_image(X, Y, image=wallPNG))


def placeTarget():
    global targetPNG, target, targetLocation, cX, cY, realTime

    if (len(targetToBeSpawned) > 0):
        event = targetToBeSpawned.pop()
        X = event[0]
        Y = event[1]
        target = canvas.create_image(X, Y, image=targetPNG)
        targetLocation = canvas.coords(target)
        return

    while(1):
        X = startX + playerSize * random.randint(0, cX)
        Y = startY + playerSize * random.randint(0, cY)
        if (X == heroLocation[0] and Y == heroLocation[1]):
            continue
        if (grid[int(X)][int(Y)]):
            continue
        if (wall[int(X)][int(Y)]):
            continue

        target = canvas.create_image(X, Y, image=targetPNG)
        targetLocation = canvas.coords(target)
        break


def setMatrix():
    global startX, startY, playerSize, cX, cY

    for i in range(startX, startX + playerSize * cX + 1, playerSize):
        for j in range(startY, startY + playerSize * cY + 1, playerSize):
            grid[i][j] = shape[i][j] = wall[i][j] = 0


def delete_status():
    global status_window, preLevel, pre
    global wallsTxt, chanceTxt, dmgTxt

    canvas.delete(status_window)
    canvas.delete(preLevel)
    canvas.delete(chanceTxt)
    canvas.delete(wallsTxt)
    canvas.delete(dmgTxt)
    pre = 0

    playLevel()


def generateLevel():
    global capacity, notStarted, starPNG, kingPNG, diamondPNG
    global startLevelPNG, health, startX, startY, width, player
    global level, chrono, realTime, timeLeft, targets_left, scoreText
    global healthText, targetText, timeText, targetToBeSpawned
    global monsterToBeSpawned, monsterHit, targetEvents, wallEvents
    global playerEvents, monsterEvents, healthEvents
    global explodingTimeEvents, timeEvents, exploding, explodingTime
    global chanceToExplode, capacity, init, superPower, startPower
    global stopPower, passLevel, immune, powerful, loading
    global myhero, STOP, status_window, preLevel, pre
    global wallsTxt, chanceTxt, dmgTxt, score

    winsound.PlaySound(None, winsound.SND_ASYNC)

    canvas.delete("all")
    canvas.pack()

    createGrid()

    for i in range(8):
        monsterEvents[i].clear()
    monsterToBeSpawned.clear()
    targetToBeSpawned.clear()
    ToBeDetonated.clear()
    monsterHit.clear()
    explodingTimeEvents.clear()
    targetEvents.clear()
    healthEvents.clear()
    playerEvents.clear()
    wallEvents.clear()
    timeEvents.clear()

    # Binds Keyboard
    bindKeys()

    # No cheats at first
    passLevel = 0
    powerful = 0
    immune = 0
    STOP = 0

    chrono = 1
    realTime = 1
    level = level + 1
    health = player.health
    if (level < 7): targets_left = 4
    elif (level < 15): targets_left = 5
    else: targets_left = 6

    timeLeft = 15 * targets_left

    if (level == 1):
        capacity = init
        score = 0
    
    chanceToExplode = 3 + 2 * min((level - 1), 11)
    explodingTime = 0
    exploding = 0

    txt = "SCORE: " + str(score)
    scoreText = canvas.create_text(
        startX + 100,
        60,
        fill="white",
        font="Terminal 20",
        text=txt)

    txt = "HEALTH: " + str(health)
    healthText = canvas.create_text(
        width / 2 + width / 3 + 60,
        60,
        fill="white",
        font="Terminal 20",
        text=txt)

    txt = "TARGETS: " + str(targets_left)
    targetText = canvas.create_text(
        width / 2 + width / 6 + 30,
        60,
        fill="white",
        font="Terminal 20",
        text=txt)

    txt = "TIME: " + str(timeLeft)
    timeText = canvas.create_text(
        width / 2,
        60,
        fill="white",
        font="Terminal 20",
        text=txt)

    if (myhero == 1):
        player = StarPlatinum(
            player.health,
            player.damage,
            player.power,
            canvas.create_image(
                width / 2,
                startY,
                image=starPNG))
    elif (myhero == 2):
        player = Mandom(
            player.health,
            player.damage,
            player.power,
            canvas.create_image(
                width / 2,
                startY,
                image=mandomPNG))
    elif (myhero == 3):
        player = CrazyDiamond(
            player.health,
            player.damage,
            player.power,
            canvas.create_image(
                width / 2,
                startY,
                image=diamondPNG))
    elif (myhero == 4):
        player = KingCrimson(
            player.health,
            player.damage,
            player.power,
            canvas.create_image(
                width / 2,
                startY,
                image=kingPNG))

    player.power = capacity
    player.immovable()
    updatePos()

    stopPower = - (2 ** 30)
    startPower = - (2 ** 30)
    superPower = 0

    AbilityBar()

    setMatrix()
    placeTarget()
    placeLabyrinth(level)
    placeMonsters(level)

    notStarted = 1

    if (loading == 1):
        playLevel()
    else:
        size = 150
        preLevel = canvas.create_rectangle(
            width / 2 - size,
            height / 2 - size,
            width / 2 + size,
            height / 2 + size,
            fill="maroon",
            outline="maroon")

        txt = "Walls' resistance: " + str(25 + 5 * level)
        wallsTxt = canvas.create_text(
            width / 2,
            height / 2 - 100,
            fill="white",
            font="Terminal 15",
            text=txt)

        txt = "Chance of explosion: " + str(chanceToExplode) + "%"
        chanceTxt = canvas.create_text(
            width / 2,
            height / 2 - 50,
            fill="white",
            font="Terminal 15",
            text=txt)

        txt = "Your damage: " + str(player.damage)
        dmgTxt = canvas.create_text(
            width / 2,
            height / 2,
            fill="white",
            font="Terminal 15",
            text=txt)

        pre = 1
        status = Button(
            window,
            image=okPNG,
            command=lambda: delete_status(),
            anchor=W)
        status.configure(width=70, activebackground="maroon", relief=FLAT)
        status_window = canvas.create_window(
            width / 2 - 70 / 2,
            height / 2 + size - 100,
            anchor=NW,
            window=status)

    # Maybe a little pause before starting the game?
    '''
    if (loading == 1):
        playLevel()
    else:
        Update3()
        window.after(1000, Update2)
        window.after(2000, Update1)
        window.after(3000, Go)
        window.after(4000, Remove123)
        window.after(4000, playLevel)
    '''


def getKey(item):
    return (-int(item[1]))


def updateLeaderboard(name, score):

    leaderboardFile = open("leaderboard.in", "r")
    line = leaderboardFile.readline()
    scoreboard = [(name, score)]

    while line:
        N = len(line) - 1

        i = 0
        namePlayer = ""
        while (i < N):
            if (line[i] == '+'):
                break
            else:
                namePlayer = namePlayer + line[i]
            i = i + 1

        i = i + 1
        scorePlayer = ""
        while (i < N):
            scorePlayer = scorePlayer + line[i]
            i = i + 1

        scoreboard.append([namePlayer, scorePlayer])
        line = leaderboardFile.readline()

    leaderboardFile.close()
    scoreboard = sorted(scoreboard, key=getKey)

    leaderboardFile = open("leaderboard.in", "w")

    updatedScoreboard = ""
    for playerline in scoreboard:
        updatedScoreboard = updatedScoreboard + \
            playerline[0] + "+" + playerline[1] + "\n"

    leaderboardFile.write(updatedScoreboard)
    leaderboardFile.close()


def successfulSubmit(name, score):

    updateLeaderboard(name, score)
    leaderBoardMenu()


def validateName():
    global enterName, error_name, score

    canvas.bind("<b>", bossKey)
    canvas.focus_set()

    namePlayer = enterName.get()
    if (len(namePlayer) == 0):
        error_name = 1
    elif (len(namePlayer) > 15):
        error_name = 2
    elif ("+" in namePlayer):
        error_name = 3

    if (error_name > 0):
        submitScoreMenu()
    else:
        successfulSubmit(str(namePlayer), str(score))


def submitScoreMenu():
    global submitPNG, score, enterName, error_name

    unbindKeys()
    canvas.delete("all")

    canvas.create_rectangle(
        0,
        0,
        width,
        height,
        fill="maroon",
        outline="maroon")
    canvas.pack()

    txt = "SCORE: "
    canvas.create_text(
        700,
        height / 4,
        fill="white",
        font="Terminal 40",
        text=txt)
    canvas.create_text(
        width - 700,
        height / 4,
        fill="white",
        font="Terminal 40",
        text=str(score))

    txt = "NAME: "
    canvas.create_text(
        700,
        height / 4 + height / 6,
        fill="white",
        font="Terminal 40",
        text=txt)

    enterName = Entry(
        window,
        bg="black",
        fg="white",
        width=15,
        font="Terminal 40")
    canvas.create_window(
        width - 700,
        height / 4 + height / 6,
        window=enterName)

    if (error_name == 1):
        canvas.create_text(
            width / 2,
            height / 2 + 150,
            fill="white",
            font="Terminal 20",
            text="Please enter something")
    elif (error_name == 2):
        canvas.create_text(
            width / 2,
            height / 2 + 150,
            fill="white",
            font="Terminal 20",
            text="Please enter a name less than 15 characters")
    elif (error_name == 3):
        canvas.create_text(
            width / 2,
            height / 2 + 150,
            fill="white",
            font="Terminal 20",
            text="Please enter a name not containing '+'")

    error_name = 0
    submitScore = Button(
        window,
        image=submitPNG,
        command=lambda: validateName(),
        anchor=W)
    submitScore.configure(width=400, activebackground="maroon", relief=FLAT)
    submitScore_window = canvas.create_window(
        width / 2 - 400 / 2,
        height - height / 4,
        anchor=NW,
        window=submitScore)

# Menu to show when game opens


def leaderBoardMenu():
    global leadPNG, leftPNG, rightPNG, mainMenuPNG, rankPNG, namePNG, scorePNG

    unbindKeys()
    canvas.delete("all")

    canvas.create_rectangle(
        0,
        0,
        width,
        height,
        fill="maroon",
        outline="maroon")
    canvas.pack()

    # https://dlpng.com/png/6974854
    leftPNG = PhotoImage(file="left.png")
    canvas.create_image(width / 8, height / 2, image=leftPNG)

    # https://www.fourjay.org/vd/xbooox_za-warudo-png-transparent-png/
    rightPNG = PhotoImage(file="right.png")
    canvas.create_image(width - width / 8, height / 2, image=rightPNG)

    leadPNG = PhotoImage(file="lead.png")
    canvas.create_image(width / 2, 150, image=leadPNG)

    rankPNG = PhotoImage(file="rank.png")
    canvas.create_image(width / 3, 300, image=rankPNG)

    namePNG = PhotoImage(file="name.png")
    canvas.create_image(width / 2, 300, image=namePNG)

    scorePNG = PhotoImage(file="score.png")
    canvas.create_image(width - width / 3, 300, image=scorePNG)

    # Display Leader Board
    leaderboardFile = open("leaderboard.in", "r")
    line = leaderboardFile.readline()

    suffix = ["", "ST", "ND", "RD", "TH", "TH"]
    lastHeight = 400
    scoreBefore = 0
    currRank = 1
    curr = 1

    while (curr <= 5):
        N = len(line) - 1

        i = 0
        namePlayer = ""
        while (i < N):
            if (line[i] == '+'):
                break
            else:
                namePlayer = namePlayer + line[i]
            i = i + 1

        i = i + 1
        scorePlayer = ""
        while (i < N):
            scorePlayer = scorePlayer + line[i]
            i = i + 1

        if (int(scoreBefore) > int(scorePlayer)):
            currRank = curr
        scoreBefore = scorePlayer

        txt = str(currRank) + suffix[currRank]
        canvas.create_text(
            width / 3,
            lastHeight,
            fill="white",
            font="Terminal 25",
            text=txt)

        if (scorePlayer == "0" and len(namePlayer) >= 15):
            canvas.create_text(
                width / 2,
                lastHeight - 3,
                fill="white",
                font="Terminal 25",
                text="?")
            canvas.create_text(
                width - width / 3,
                lastHeight - 3,
                fill="white",
                font="Terminal 25",
                text="?")
        else:
            canvas.create_text(
                width / 2,
                lastHeight - 3,
                fill="white",
                font="Terminal 25",
                text=namePlayer)
            canvas.create_text(
                width - width / 3,
                lastHeight - 3,
                fill="white",
                font="Terminal 25",
                text=scorePlayer)

        curr = curr + 1
        lastHeight = lastHeight + 100
        line = leaderboardFile.readline()

    leaderboardFile.close()

    # Go back to Intro Menu
    mainMenu = Button(
        window,
        image=mainMenuPNG,
        command=lambda: introMenu(),
        anchor=W)
    mainMenu.configure(width=400, activebackground="maroon", relief=FLAT)
    mainMenu_window = canvas.create_window(
        width / 2 - 400 / 2,
        height - height / 5,
        anchor=NW,
        window=mainMenu)


def exitGame():
    winsound.PlaySound(None, winsound.SND_ASYNC)
    quit()


def musicDecide():
    global music

    music = 1 - music
    if (music == 0):
        winsound.PlaySound(None, winsound.SND_ASYNC)
    else:
        winsound.PlaySound(
            'intro.wav',
            winsound.SND_ALIAS | winsound.SND_ASYNC)


def aztecaText():

    txt = "HEALTH: 120"
    canvas.create_text(
        width / 7 + 300,
        150,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "DAMAGE: 25"
    canvas.create_text(
        width / 7 + 300,
        200,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "ABILITY: STOPS TIME"
    canvas.create_text(
        width / 7 + 300,
        250,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "DURATION: 3 seconds"
    canvas.create_text(
        width / 7 + 300,
        300,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "CONFUSING: DAZE ENEMIES"
    canvas.create_text(
        width / 7 + 300,
        350,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "ONLY HE CAN MOVE IN STOPPED TIME"
    canvas.create_text(
        width / 7 + 300,
        400,
        fill="white",
        font="Terminal 15",
        text=txt)


def naneText():
    txt = "HEALTH: 120"
    canvas.create_text(
        width - width / 7 - 350,
        150,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "DAMAGE: 25"
    canvas.create_text(
        width - width / 7 - 350,
        200,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "ABILITY: REWINDS TIME"
    canvas.create_text(
        width - width / 7 - 350,
        250,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "DURATION: 5 seconds"
    canvas.create_text(
        width - width / 7 - 350,
        300,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "EVENTS WILL OCCUR IN THE SAME ORDER"
    canvas.create_text(
        width - width / 7 - 350,
        350,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "AFTER TIME REVERSES"
    canvas.create_text(
        width - width / 7 - 350,
        375,
        fill="white",
        font="Terminal 15",
        text=txt)


def nefiuText():
    txt = "HEALTH: 75"
    canvas.create_text(
        width / 7 + 300,
        height - 400,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "DAMAGE: 20"
    canvas.create_text(
        width / 7 + 300,
        height - 350,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "ABILITY: HEALS HIMSELF (10HP)"
    canvas.create_text(
        width / 7 + 300,
        height - 300,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "CAPACITY: 3 times"
    canvas.create_text(
        width / 7 + 300,
        height - 250,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "MAY USE ALL HIS HEALINGS AT ONCE"
    canvas.create_text(
        width / 7 + 300,
        height - 200,
        fill="white",
        font="Terminal 15",
        text=txt)


def amulyText():
    txt = "HEALTH: 100"
    canvas.create_text(
        width - width / 7 - 350,
        height - 400,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "DAMAGE: 20"
    canvas.create_text(
        width - width / 7 - 350,
        height - 350,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "ABILITY: ERASES TIME"
    canvas.create_text(
        width - width / 7 - 350,
        height - 300,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "DURATION: 5 seconds"
    canvas.create_text(
        width - width / 7 - 350,
        height - 250,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "CONFUSING: DAZE ENEMIES"
    canvas.create_text(
        width - width / 7 - 350,
        height - 200,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "WHATEVER HAPPENED TO HIM IN THAT TIME IS IGNORED"
    canvas.create_text(
        width - width / 7 - 350,
        height - 150,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "ANY OTHER ACTION STILL HAPPENS TO EVERYONE ELSE"
    canvas.create_text(
        width - width / 7 - 350,
        height - 125,
        fill="white",
        font="Terminal 15",
        text=txt)

    txt = "HE MAY MOVE FREELY IN THE ERASED TIME"
    canvas.create_text(
        width - width / 7 - 350,
        height - 100,
        fill="white",
        font="Terminal 15",
        text=txt)


def aztecaChosen():
    global player, init, capacity, width, height, startY, myhero

    canvas.delete("all")
    player = StarPlatinum(
        120, 25, 3, canvas.create_image(
            width / 2, startY, image=starPNG))
    init = capacity = player.power
    myhero = 1

    generateLevel()


def naneChosen():
    global player, init, capacity, width, height, startY, myhero

    canvas.delete("all")
    player = Mandom(
        120,
        25,
        5,
        canvas.create_image(
            width / 2,
            startY,
            image=mandomPNG))
    init = capacity = player.power
    myhero = 2

    generateLevel()


def nefiuChosen():
    global player, init, capacity, width, height, startY, myhero

    canvas.delete("all")
    player = CrazyDiamond(
        75, 20, 3, canvas.create_image(
            width / 2, startY, image=diamondPNG))
    init = capacity = player.power
    myhero = 3

    generateLevel()


def amulyChosen():
    global player, init, capacity, width, height, startY, myhero

    canvas.delete("all")
    player = KingCrimson(
        100, 20, 5, canvas.create_image(
            width / 2, startY, image=kingPNG))
    init = capacity = player.power
    myhero = 4

    generateLevel()


def LeftSide(fixed):
    txt = "Up Arrow"
    canvas.create_text(fixed, 400, fill="white", font="Terminal 22", text=txt)

    txt = "Right Arrow"
    canvas.create_text(fixed, 470, fill="white", font="Terminal 22", text=txt)

    txt = "Down Arrow"
    canvas.create_text(fixed, 540, fill="white", font="Terminal 22", text=txt)

    txt = "Left Arrow"
    canvas.create_text(fixed, 610, fill="white", font="Terminal 22", text=txt)

    txt = "Space"
    canvas.create_text(fixed, 680, fill="white", font="Terminal 22", text=txt)

    txt = "P"
    canvas.create_text(fixed, 750, fill="white", font="Terminal 22", text=txt)

    txt = "B"
    canvas.create_text(fixed, 820, fill="white", font="Terminal 22", text=txt)


def RightSide(fixed):
    txt = "Player goes up"
    canvas.create_text(
        width - fixed,
        400,
        fill="white",
        font="Terminal 22",
        text=txt)

    txt = "Player goes right"
    canvas.create_text(
        width - fixed,
        470,
        fill="white",
        font="Terminal 22",
        text=txt)

    txt = "Player goes down"
    canvas.create_text(
        width - fixed,
        540,
        fill="white",
        font="Terminal 22",
        text=txt)

    txt = "Player goes left"
    canvas.create_text(
        width - fixed,
        610,
        fill="white",
        font="Terminal 22",
        text=txt)

    txt = "Starts/Stops ability"
    canvas.create_text(
        width - fixed,
        680,
        fill="white",
        font="Terminal 22",
        text=txt)

    txt = "Pauses the game"
    canvas.create_text(
        width - fixed,
        750,
        fill="white",
        font="Terminal 22",
        text=txt)

    txt = "Boss Key"
    canvas.create_text(
        width - fixed,
        820,
        fill="white",
        font="Terminal 22",
        text=txt)


def LeftSideCheats(fixed):
    txt = "Digits 1 + 0"
    canvas.create_text(fixed, 500, fill="white", font="Terminal 27", text=txt)

    txt = "Digits 2 + 9"
    canvas.create_text(fixed, 600, fill="white", font="Terminal 27", text=txt)

    txt = "Digits 3 + 8"
    canvas.create_text(fixed, 700, fill="white", font="Terminal 27", text=txt)


def RightSideCheats(fixed):
    txt = "Pass current level instantly"
    canvas.create_text(
        width - fixed,
        500,
        fill="white",
        font="Terminal 27",
        text=txt)

    txt = "Infinite health"
    canvas.create_text(
        width - fixed,
        600,
        fill="white",
        font="Terminal 27",
        text=txt)

    txt = "Infinite ability"
    canvas.create_text(
        width - fixed,
        700,
        fill="white",
        font="Terminal 27",
        text=txt)


def cheatsMenu(event):
    unbindKeys()
    canvas.delete("all")
    canvas.create_rectangle(
        0,
        0,
        width,
        height,
        fill="maroon",
        outline="maroon")
    canvas.pack()

    fixed = 7 * width / 24 + 50
    canvas.create_image(fixed, 250, image=keyPNG)
    canvas.create_image(width - fixed, 250, image=effectPNG)

    LeftSideCheats(fixed)
    RightSideCheats(fixed)

    # Go back to Intro Menu
    mainMenu = Button(
        window,
        image=mainMenuPNG,
        command=lambda: introMenu(),
        anchor=W)
    mainMenu.configure(width=400, activebackground="maroon", relief=FLAT)
    mainMenu_window = canvas.create_window(
        width / 2 - 400 / 2,
        height - height / 6,
        anchor=NW,
        window=mainMenu)


def controlMenu():
    unbindKeys()
    canvas.delete("all")
    canvas.create_rectangle(
        0,
        0,
        width,
        height,
        fill="maroon",
        outline="maroon")
    canvas.pack()

    fixed = 7 * width / 24
    canvas.create_image(fixed, 250, image=keyPNG)
    canvas.create_image(width - fixed, 250, image=effectPNG)

    LeftSide(fixed)
    RightSide(fixed)

    canvas.bind("zyzzmode", cheatsMenu)

    # Go back to Intro Menu
    mainMenu = Button(
        window,
        image=mainMenuPNG,
        command=lambda: introMenu(),
        anchor=W)
    mainMenu.configure(width=400, activebackground="maroon", relief=FLAT)
    mainMenu_window = canvas.create_window(
        width / 2 - 400 / 2,
        height - height / 6,
        anchor=NW,
        window=mainMenu)


def tutorialMenu2():
    unbindKeys()
    canvas.delete("all")
    canvas.create_rectangle(
        0,
        0,
        width,
        height,
        fill="maroon",
        outline="maroon")
    canvas.pack()

    canvas.create_image(width / 2, height / 6, image=example2PNG)

    txt = "1: This is the time left for the player to collect all the targets"
    canvas.create_text(
        width / 2,
        height / 2,
        fill="white",
        font="Terminal 19",
        text=txt)

    txt = "2: This is the number of targets left for"
    txt = txt + " the player to collect and finish the level"
    canvas.create_text(
        width / 2,
        height / 2 + 75,
        fill="white",
        font="Terminal 19",
        text=txt)

    txt = "3: This is the current health of the player"
    canvas.create_text(
        width / 2,
        height / 2 + 150,
        fill="white",
        font="Terminal 19",
        text=txt)

    txt = "4: This is the current score of the player"
    canvas.create_text(
        width / 2,
        height / 2 + 225,
        fill="white",
        font="Terminal 19",
        text=txt)

    txt = "For every level passed: score increases by 3000 points"
    canvas.create_text(
        width / 2,
        height / 2 + 262,
        fill="white",
        font="Terminal 19",
        text=txt)

    txt = "Also: score increases by an additional"
    txt = txt + " of 10 * (number of seconds remained)"
    canvas.create_text(
        width / 2,
        height / 2 + 300,
        fill="white",
        font="Terminal 19",
        text=txt)

    txt = "5: This is the current power remained for"
    txt = txt + " the special ability of the player"
    canvas.create_text(
        width / 2,
        height / 2 + 375,
        fill="white",
        font="Terminal 19",
        text=txt)

    txt = "Every 3 seconds, one bar will regenerate"
    canvas.create_text(
        width / 2,
        height / 2 + 412,
        fill="white",
        font="Terminal 19",
        text=txt)

    txt = "Every 3 levels, the power for the special"
    txt = txt + " ability will increase by 2 bars"
    canvas.create_text(
        width / 2,
        height / 2 + 450,
        fill="white",
        font="Terminal 19",
        text=txt)

    startGame = Button(
        window,
        image=chooseHeroButtonPNG,
        command=lambda: chooseHero(),
        anchor=W)
    startGame.configure(width=400, activebackground="maroon", relief=FLAT)
    startGame_window = canvas.create_window(
        width / 2 - 400 / 2, height / 3, anchor=NW, window=startGame)


def tutorialMenu():
    unbindKeys()
    canvas.delete("all")
    canvas.create_rectangle(
        0,
        0,
        width,
        height,
        fill="maroon",
        outline="maroon")
    canvas.pack()

    canvas.create_image(width / 2, height / 3, image=examplePNG)

    txt = "1: This is the player: a shape which may"
    txt = txt + " be controlled using the arrow keys"
    canvas.create_text(
        width / 2,
        height / 2 + 150,
        fill="white",
        font="Terminal 19",
        text=txt)

    txt = "2: This is a monster, it chases the"
    txt = txt + " player: when it's close, it will drain health"
    canvas.create_text(
        width / 2,
        height / 2 + 225,
        fill="white",
        font="Terminal 19",
        text=txt)

    txt = "3: This is a target, the player has to collect"
    txt = txt + " all the targets to succeed"
    canvas.create_text(
        width / 2,
        height / 2 + 300,
        fill="white",
        font="Terminal 19",
        text=txt)

    txt = "4: This is a wall, the player must destroy it to"
    txt = txt + " pass through, but monsters don't have to (they are agile)"
    canvas.create_text(
        width / 2,
        height / 2 + 375,
        fill="white",
        font="Terminal 19",
        text=txt)

    txt = "5: This is an explosion, do not stand"
    txt = txt + " too close to it (obvious reasons)"
    canvas.create_text(
        width / 2,
        height / 2 + 450,
        fill="white",
        font="Terminal 19",
        text=txt)

    # Go back to Intro Menu
    nxt = Button(
        window,
        image=nextTutorialPNG,
        command=lambda: tutorialMenu2(),
        anchor=W)
    nxt.configure(width=400, activebackground="maroon", relief=FLAT)
    nxt_window = canvas.create_window(
        width - width / 4,
        height / 2 - 200,
        anchor=NW,
        window=nxt)


def chooseHero():
    unbindKeys()
    canvas.delete("all")
    canvas.create_rectangle(
        0,
        0,
        width,
        height,
        fill="maroon",
        outline="maroon")
    canvas.pack()

    canvas.create_image(width / 2, height / 2 - 50, image=chooseHeroPNG)

    aztecaText()
    canvas.create_image(width / 7, 250, image=aztecaPNG)
    azteb = Button(
        window,
        image=aztecabPNG,
        command=lambda: aztecaChosen(),
        anchor=W)
    azteb.configure(width=210, activebackground="maroon", relief=FLAT)
    azteb = canvas.create_window(width / 7 + 200, 50, anchor=NW, window=azteb)

    naneText()
    canvas.create_image(width - width / 7 + 50, 250, image=nanePNG)
    naneb = Button(
        window,
        image=nanebPNG,
        command=lambda: naneChosen(),
        anchor=W)
    naneb.configure(width=210, activebackground="maroon", relief=FLAT)
    naneb = canvas.create_window(
        width - width / 7 - 450,
        50,
        anchor=NW,
        window=naneb)

    nefiuText()
    canvas.create_image(width / 7 - 10, height - 300, image=nefiuPNG)
    nefiub = Button(
        window,
        image=nefiubPNG,
        command=lambda: nefiuChosen(),
        anchor=W)
    nefiub.configure(width=210, activebackground="maroon", relief=FLAT)
    nefiub = canvas.create_window(
        width / 7 + 200,
        height - 500,
        anchor=NW,
        window=nefiub)

    amulyText()
    canvas.create_image(width - width / 7 + 50, height - 300, image=amulyPNG)
    amulyb = Button(
        window,
        image=amulybPNG,
        command=lambda: amulyChosen(),
        anchor=W)
    amulyb.configure(width=210, activebackground="maroon", relief=FLAT)
    amulyb = canvas.create_window(
        width - width / 7 - 450,
        height - 500,
        anchor=NW,
        window=amulyb)

    # Go to Tutorial
    tutorial = Button(
        window,
        image=tutorialPNG,
        command=lambda: tutorialMenu(),
        anchor=W)
    tutorial.configure(width=200, activebackground="maroon", relief=FLAT)
    tutorial_window = canvas.create_window(
        width / 2 - 200 / 2,
        height - height / 3 - 50,
        anchor=NW,
        window=tutorial)

    # Go back to Intro Menu
    mainMenu = Button(
        window,
        image=mainMenuSmallPNG,
        command=lambda: introMenu(),
        anchor=W)
    mainMenu.configure(width=200, activebackground="maroon", relief=FLAT)
    mainMenu_window = canvas.create_window(
        width / 2 - 200 / 2,
        height - height / 4 - 50,
        anchor=NW,
        window=mainMenu)


def introMenu():
    global width, height, startGamePNG, loadGamePNG, quitPNG
    global musicOnOffPNG, diamond, level, score, capacity
    global littleMenu, saveSession_window, mainMenu_window
    global fastMenu, inMenu, pause, pausedTime, music
    global quitGame_window, displayScoreboardPNG

    unbindKeys()
    canvas.delete("all")
    canvas.create_rectangle(
        0,
        0,
        width,
        height,
        fill="maroon",
        outline="maroon")
    canvas.pack()

    fastMenu = inMenu = pause = pausedTime = 0

    level = 0
    score = 0
    canvas.create_image(width / 2, 150, image=titlePNG)

    startGame = Button(
        window,
        image=startGamePNG,
        command=lambda: chooseHero(),
        anchor=W)
    startGame.configure(width=400, activebackground="maroon", relief=FLAT)
    startGame_window = canvas.create_window(
        width / 2 - 400 / 2, height / 3, anchor=NW, window=startGame)

    loadGame = Button(
        window,
        image=loadGamePNG,
        command=lambda: LoadGame(),
        anchor=W)
    loadGame.configure(width=400, activebackground="maroon", relief=FLAT)
    loadGame_window = canvas.create_window(
        width / 2 - 400 / 2,
        height / 3 + 120,
        anchor=NW,
        window=loadGame)

    controls = Button(
        window,
        image=controlsPNG,
        command=lambda: controlMenu(),
        anchor=W)
    controls.configure(width=400, activebackground="maroon", relief=FLAT)
    controls_window = canvas.create_window(
        width / 2 - 400 / 2,
        height / 3 + 240,
        anchor=NW,
        window=controls)

    displayScoreboard = Button(
        window,
        image=displayScoreboardPNG,
        command=lambda: leaderBoardMenu(),
        anchor=W)
    displayScoreboard.configure(
        width=400,
        activebackground="maroon",
        relief=FLAT)
    displayScoreboard_window = canvas.create_window(
        width / 2 - 400 / 2, height / 3 + 360, anchor=NW,
        window=displayScoreboard)

    quitGame = Button(
        window,
        image=quitPNG,
        command=lambda: exitGame(),
        anchor=W)
    quitGame.configure(width=400, activebackground="maroon", relief=FLAT)
    quitGame_window = canvas.create_window(
        width / 2 - 400 / 2,
        height / 3 + 480,
        anchor=NW,
        window=quitGame)

    # Activate/Deactivate Music
    musicGame = Button(
        window,
        image=musicOnOffPNG,
        command=lambda: musicDecide(),
        anchor=W)
    musicGame.configure(width=50, activebackground="maroon", relief=FLAT)
    musicGame_window = canvas.create_window(
        width / 18, height - height / 8, anchor=NW, window=musicGame)


def bindKeys():
    # Cheats here
    canvas.bind("10", cheatPass)         # User passes level
    canvas.bind("29", cheatHealth)       # User has unlimited health
    canvas.bind("38", cheatPower)        # User has unlimited power
    
    canvas.bind("<Left>", leftKey)
    canvas.bind("<Right>", rightKey)
    canvas.bind("<Up>", upKey)
    canvas.bind("<Down>", downKey)
    canvas.bind("<space>", spaceBar)
    canvas.bind("<Escape>", escapeKey)
    canvas.bind("<P>", pauseKey)
    canvas.bind("<p>", pauseKey)
    canvas.bind("<B>", bossKey)
    canvas.bind("<b>", bossKey)
    canvas.focus_set()


def unbindKeys():
    canvas.unbind("1")
    canvas.unbind("2")
    canvas.unbind("3")
    canvas.unbind("<Left>")
    canvas.unbind("<Right>")
    canvas.unbind("<Up>")
    canvas.unbind("<Down>")
    canvas.unbind("<space>")
    canvas.unbind("<Escape>")
    canvas.bind("<P>", pauseKey)
    canvas.bind("<p>", pauseKey)
    canvas.bind("zyzzmode", cheatsMenu)
    canvas.focus_set()


window = Tk()
window.wm_attributes('-fullscreen', 'true')
window.title("My Game")
width = window.winfo_screenwidth()
height = window.winfo_screenheight()
window.geometry('%dx%d+0+0' % (width, height))
canvas = Canvas(window, bg="black", width=width, height=height)

# https://freesound.org/people/Sirkoto51/sounds/414214/
winsound.PlaySound('intro.wav', winsound.SND_ALIAS | winsound.SND_ASYNC)

wait = []
monster = []
barrier = [0]
wallLocation = []
monsterLocation = []

monsterToBeSpawned = collections.deque()
targetToBeSpawned = collections.deque()
ToBeDetonated = collections.deque()
explodingTimeEvents = collections.deque()
explosionEvents = collections.deque()
targetEvents = collections.deque()
playerEvents = collections.deque()
healthEvents = collections.deque()
wallEvents = collections.deque()
timeEvents = collections.deque()
monsterHit = collections.deque()

monsterEvents = []

for i in range(8):
    temp = collections.deque()
    monsterEvents.append(temp)

block = []
for i in range(2000):
    temp = []
    for j in range(2000):
        temp.append(0)
    block.append(temp)

grid = []
for i in range(2000):
    temp = []
    for j in range(2000):
        temp.append(0)
    grid.append(temp)

wall = []
for i in range(2000):
    temp = []
    for j in range(2000):
        temp.append(0)
    wall.append(temp)

shape = []
for i in range(2000):
    temp = []
    for j in range(2000):
        temp.append(0)
    shape.append(temp)

testedExplosion = []
for i in range(2000):
    temp = []
    for j in range(2000):
        temp.append(0)
    testedExplosion.append(temp)


boss = 0
pause = 0
inMenu = 0
bossTime = 0
pausedTime = 0
resumeTime = 0

loading = 0
goIntro = 0
notStarted = 1

error_name = 0
fastMenu = 0
willSave = 0
music = 1
STOP = 0

pre = 0
beginX = 0
beginY = 0
explosionLocation = [0, 0]
objexp = canvas.create_rectangle(0, 0, 1, 1, fill="maroon", outline="maroon")

bars = []
score = 0
chrono = 0
superPower = 0
chanceToExplode = 5
startX = 80
startY = 140
playerSize = 40
half = playerSize / 2
diffX = startX % playerSize
diffY = startY % playerSize
stopPower = - (2 ** 30)
startPower = - (2 ** 30)
direction = "right"
past_dir = "right"

nextLevRedPNG = PhotoImage(file="next_red.png")
gameOverPNG = PhotoImage(file="gameOver.png")
fullBarPNG = PhotoImage(file="fullBar.png")
emptyBarPNG = PhotoImage(file="emptyBar.png")

# Buttons made at: https://dabuttonfactory.com/
# Retro Game Text: http://arcade.photonstorm.com/
chooseHeroButtonPNG = PhotoImage(file="chooseHeroButton.png")
nextTutorialPNG = PhotoImage(file="nextTutorial.png")
examplePNG = PhotoImage(file="example.png")
example2PNG = PhotoImage(file="example2.png")
controlsPNG = PhotoImage(file="controls.png")
submitScorePNG = PhotoImage(file="submitScore.png")
mainMenuSmallPNG = PhotoImage(file="mainMenuSmall.png")
mainMenuPNG = PhotoImage(file="mainMenu.png")
restartPNG = PhotoImage(file="restart.png")
displayScoreboardPNG = PhotoImage(file="scoreboard.png")
startGamePNG = PhotoImage(file="startGame.png")
loadGamePNG = PhotoImage(file="load.png")
submitPNG = PhotoImage(file="submit.png")
titlePNG = PhotoImage(file="title.png")
quitPNG = PhotoImage(file="quit.png")
musicOnOffPNG = PhotoImage(file="musicOnOff.png")
gameSavedPNG = PhotoImage(file="gameSaved.png")
savePNG = PhotoImage(file="save.png")
tutorialPNG = PhotoImage(file="tutorial.png")
effectPNG = PhotoImage(file="effect.png")
cheatsPNG = PhotoImage(file="cheats.png")
keyPNG = PhotoImage(file="key.png")
winPNG = PhotoImage(file="win.png")
okPNG = PhotoImage(file="ok.png")

hidePNG = PhotoImage(file="hide.png")

wallPNG = PhotoImage(file="wall.png")
targetPNG = PhotoImage(file="target.png")
monsterPNG = PhotoImage(file="monster.png")
explosionPNG = PhotoImage(file="explosion.png")
nothingnessPNG = PhotoImage(file="nothingness.png")

chooseHeroPNG = PhotoImage(file="chooseHero.png")

aztecabPNG = PhotoImage(file="aztecab.png")
amulybPNG = PhotoImage(file="amulyb.png")
nefiubPNG = PhotoImage(file="nefiub.png")
nanebPNG = PhotoImage(file="naneb.png")

# https://dlpng.com/png/6484596
aztecaPNG = PhotoImage(file="azteca.png")
# https://www.pngkey.com/maxpic/u2t4q8u2y3e6i1a9/
amulyPNG = PhotoImage(file="amuly.png")
# https://www.pngkey.com/maxpic/u2y3q8o0i1e6a9t4/
nefiuPNG = PhotoImage(file="nefiu.png")
# https://dlpng.com/png/5287933
nanePNG = PhotoImage(file="nane2.png")

starPNG = PhotoImage(file="starPlayer.png")
kingPNG = PhotoImage(file="kingPlayer.png")
diamondPNG = PhotoImage(file="diamondPlayer.png")
mandomPNG = PhotoImage(file="mandomPlayer.png")

player = StarPlatinum(
    120, 25, 3, canvas.create_image(
        width / 2, startY, image=starPNG))
capacity = init = 12
myhero = 1

canvas.bind("<B>", bossKey)
canvas.bind("<b>", bossKey)
canvas.focus_set()


introMenu()
window.mainloop()
