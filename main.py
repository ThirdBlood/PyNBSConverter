import pynbs

note_list: dict[int, list[pynbs.Note]] = {}  # 该字典是整首曲子的音符表，第一层是列，第二层是列里面的音符


def detectLayer(length: int, layer: int, now_tick: int) -> bool:
    """
    检测是否为可用层
    :param length: 音符长度
    :param layer: 层数
    :param now_tick: 当前所在tick
    :return: 是否够空间
    """
    ticks = [tick for tick in note_list][-length-1:]  # 预截取
    for tick in ticks:
        note_row = note_list[tick]  # 代表此tick对应的列
        for note in note_row:
            if note.layer == layer:  # 如果layer对应上，则代表音符冲突，这层不能用
                return False
    return True  # 如果一直没有对应，那就能用


def parse(new_song: pynbs.File, tick: int, row: list[pynbs.Note]):
    """
    处理列并转译到新文件
    :param new_song: 新文件对象
    :param tick: 旧文件某个特定音符的tick，要与新文件的对应执行编码tick对齐
    :param row: 列
    :return:
    """
    linec = len(row) + 1  # 加一是因为还有执行编码，实际占用的tick为8倍linec
    keyv = [note.key for note in row]  # 本列的纯音符音高列表
    print(f"正在处理Tick为{tick}的音符列，本列共需用{linec}个编码，编码后占用{linec*8}gt。")
    for layer in range(24):  # 最多24层编码器，不能多了
        if detectLayer(linec, layer, tick):  # 如果这层放得下编码
            delay = tick % 8  # 由于每个编码必须间隔8gt，所以应当有延迟
            tick -= delay  # 先减去延迟
            try:  # 如果列不存在，则创建新列
                note_list[tick]
            except KeyError:
                note_list[tick] = []
            if not delay:  # 填充黄色的无延迟执行编码
                note_list[tick].append(pynbs.Note(tick=tick, layer=layer, instrument=3, key=23))
                new_song.notes.append(pynbs.Note(tick=tick, layer=layer, instrument=3, key=23))
            else:  # 填充绿色的有延迟执行编码
                for note_delay in range(delay):  # 逐渐往后填充1个gt的绿色编码
                    note_list[tick].append(pynbs.Note(tick=tick + note_delay, layer=layer, instrument=1, key=23))
                    new_song.notes.append(pynbs.Note(tick=tick + note_delay, layer=layer, instrument=1, key=23))
            for key in reversed(keyv):
                tick -= 8
                try:  # 如果列不存在，则创建新列
                    note_list[tick]
                except KeyError:
                    note_list[tick] = []
                # 填充声明的音符编码
                note_list[tick].append(pynbs.Note(tick=tick, layer=layer, instrument=0, key=key))
                new_song.notes.append(pynbs.Note(tick=tick, layer=layer, instrument=0, key=key))
            break


def process(in_file: str, out_file: str):
    """
    如果计划没问题的话……tick指的是旧文件某个特定音符的tick，然后它也要与新文件的对应执行编码tick对齐；
    chord指的是tick对应的列音符……
    也许我们是在将传统Minecraft红石音乐转换成第四代编码格式……
    :param in_file:
    :param out_file:
    :return:
    """
    core_song = pynbs.read(in_file + ".nbs")
    new_song = pynbs.new_file(song_name=in_file)
    for tick, chord in core_song:
        # note_list[tick] = chord
        parse(new_song, tick, chord)
    for tick, chord in new_song:
        print("新文件", tick, chord)
    new_song.save(out_file)  # 储存


if __name__ == "__main__":
    file_name = input("请输入处理好的NBS文件名（不含扩展名）：")
    process(file_name, file_name + "-after.nbs")
