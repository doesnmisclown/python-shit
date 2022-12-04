import random
nothing = 0
clicks = 100
difficult = 0
items_list = ["Камень", "Уголь", "Железо", "Золото", "Алмаз"]
items = dict.fromkeys(items_list,0)
ranges = []
for i in range(len(items_list)):
    if i == 0:
        ranges.append(
            range(
                0,
                random.randint(0, 100),
            )
        )
        continue
    prev = ranges[i - 1]
    ranges.append(
        range(
            max(prev)+1,
            max(prev) + 2 + random.randint(0, 100)*i,
        )
    )

while True:
    print("\033[H\033[J", end="")
    print("Инвентарь:")
    for i in enumerate(items):
        print(f"{i[1]} ({items[i[1]]} шт.)")
    print("Действия:")
    print(f"1. Добывать (осталось {clicks} прочности. Шанс добычи {round(100*1/(difficult+1))}%)(Сложность {difficult})")
    for i in items.keys():
        ix = list(items.keys()).index(i)
        print(f"{ix + 2}. Продать {i} (+{((ix+1)*10)*items[i]})")
    a = input("> ")
    if a == "q":
        exit()
    if a == "1":
        if clicks < difficult:
            for i in enumerate(items.keys()):
                if items[i[1]] > 0:
                    clicks += i[0] * items[i[1]] * 10
                    items[i[1]] = 0
            difficult+=1
            if clicks < difficult:
                #print("\033[H\033[J", end="")
                print("Вы проиграли")
                print("Статистика")
                print(f"Сложность: {difficult}")
                exit()
        #clicks-=difficult+1
        chance = random.randint(0, difficult)
        if chance != 0:
            clicks-=difficult
            nothing+=1
            continue
        else:
            rng_num = random.randint(0, max(ranges[-1]))
            for i in items_list:
                ix = items_list.index(i)
                rng = ranges[len(ranges)-ix-1]
                if rng_num in rng:
                  clicks-= ix+1*difficult+1
                  items[i]+=1
        continue
    _items = list(items.keys())
    if not a.isdigit():
        continue
    a = int(a)
    if a > len(_items):
        continue
    if _items[a - 2] and items[_items[a - 2]] > 0:
        items[_items[a - 2]] -= 1
        clicks += ((a - 2) + 1) * 10
        difficult += 1
