import os
import re
import pyperclip
import task
import editor
import render as rn
from jsonparse import write_json_archive, write_json_items

render_prefs = {"success": None, "print": True, "print_b": True}


def _get_newid_board(): return task.items[-1]["number"]+1 if task.items else 1


def _get_newid_archive(
): return task.items[-1]["number"]+1 if task.items else 1


def _parse_boards(arg):
    args = arg.split(" ")
    boards = []
    indexes = []
    for index, item in enumerate(args):
        if "@" in item and item[0] == "@" and len(item) != 1 and item[1] != "@":
            boards.append(''.join(item[1:]))
            indexes.append(index)
    args = [y for x, y in enumerate(args) if x not in indexes]
    header = ' '.join(args)
    return header, boards


def timeline():
    render_prefs['print'] = False
    render_prefs['success'] = True
    timeline_dict = {}
    for item in task.items:
        if item['date'][0] not in timeline_dict:
            timeline_dict[item['date'][0]] = [item]
        else:
            timeline_dict[item['date'][0]].append(item)
    for key, value in timeline_dict.items():
        rn.render_items(value, key, print_stats=False, print_day=False)

    c, s, p = rn.calculate_stats()
    rn.pr_stats(c, s, p)


def add_item(arg, item_type):
    if not arg:
        return

    header, boards = _parse_boards(arg)
    num = _get_newid_board()
    typee = item_type
    prior = 1
    det = editor.open_editor() if item_type == "snippet" else None
    if det is not None:
        det = det.strip()
        if not det or det.isspace():
            return

    status = "undone" if item_type == "task" else None
    item = task.Task(typee, num, header,
                     det, status, prior, boards).to_dict()
    task.items.append(item)
    write_json_items()
    render_prefs['success'] = True


def delete(nums):
    if not nums:
        return
    indexes = [x for x, y in enumerate(task.items) if y['number'] in nums]

    for index in indexes:
        task.items[index]["number"] = _get_newid_archive()
        task.archive.append(task.items[index])

    for index in reversed(indexes):
        del task.items[-1 * (len(task.items) - index)]

    if indexes:
        render_prefs['success'] = True
        write_json_items()
        write_json_archive()


def view(nums):
    if len(nums) != 1:
        return

    found = [x for x in task.items if x['number']
             == nums[0] and x['type'] == "snippet"]
    if found:
        render_prefs['success'] = True
        render_prefs['print'] = False
        print("\n"+found[0]['detail'])


def edit_content(nums):
    if len(nums) != 1:
        return

    findex = -1
    for index, item in enumerate(task.items):
        if item['number'] == nums[0] and item['type'] == "snippet":
            findex = index
            break
    if findex != -1:
        render_prefs['success'] = True
        task.items[findex]['detail'] = editor.open_editor(
            contents=task.items[findex]['detail'])
        write_json_items()


def copy_content(nums):
    if len(nums) != 1:
        return

    found = [x for x in task.items if x['number']
             == nums[0] and x['type'] == "snippet"]
    if found:
        pyperclip.copy(found[0]['detail'])
        render_prefs['success'] = True


def find_content(arg):
    for item in task.items:
        if item['type'] == "snippet" and arg in item['detail']:
            indexes = [m.start() for m in re.finditer(arg, item['detail'])]
            content = ""
            start_inx = 0
            last_inx = indexes[-1]
            for index in indexes:
                content = content + item['detail'][start_inx:index] + rn.colors.BLUE + \
                    item['detail'][index:index+len(arg)] + rn.colors.END
                start_inx = index + len(arg)
            content = content + item['detail'][last_inx+len(arg):]
            rn.render_detail(item['header'], content)
            render_prefs['success'] = True
            render_prefs['print'] = False


def find(arg):
    first_entrence = True
    for item in task.items:
        if arg in item['header']:
            indexes = [m.start() for m in re.finditer(arg, item['header'])]
            content = ""
            start_inx = 0
            last_inx = indexes[-1]
            for index in indexes:
                content = content + item['header'][start_inx:index] + rn.colors.BLUE +\
                    item['header'][index:index+len(arg)] + rn.colors.END
                start_inx = index + len(arg)
            content = content + item['header'][last_inx+len(arg):]
            rn.render_find(item, content, True) if first_entrence else rn.render_find(
                item, content)
            first_entrence = False
            render_prefs['success'] = True
            render_prefs['print'] = False


def copy(nums):
    if len(nums) != 1:
        return
    found = [x for x in task.items if x['number'] == nums[0]]
    if found:
        pyperclip.copy(found[0]['header'])
        render_prefs['success'] = True


def restore(nums):
    indexes = [x for x, y in enumerate(task.archive) if y['number'] in nums]

    for index in indexes:
        task.archive[index]["number"] = _get_newid_board()
        task.items.append(task.archive[index])
    for index in reversed(indexes):
        del task.archive[-1 * (len(task.archive) - index)]

    if indexes:
        render_prefs['success'] = True
        write_json_items()
        write_json_archive()


def archive():
    render_prefs['print'] = False
    render_prefs['success'] = None
    rn.render_items(task.archive, "Archive", False)


def check(nums):
    for item in task.items:
        if item['number'] in nums and item["type"] == "task":
            if item['status'] != "done":
                item['status'] = "done"
            else:
                item['status'] = "undone"

            render_prefs['success'] = True
    write_json_items() if render_prefs['success'] else None


def priority(arg):
    nums, prior = arg.rsplit(" ", 1) if " " in arg else (arg, "")
    nums = [int(s) for s in nums.split() if s.isdigit()]

    for item in task.items:
        if item["number"] in nums and prior in task.Task.prip_dict.keys():
            item["priority"] = task.Task.prip_dict[prior]
            render_prefs['success'] = True

    write_json_items() if render_prefs['success'] else None


def star(nums):
    for item in task.items:
        if item['number'] in nums:
            if item['starred']:
                item['starred'] = False
            else:
                item['starred'] = True
            render_prefs['success'] = True

    write_json_items() if render_prefs['success'] else None


def list_boards():
    board_dict = {"My Board": []}
    for item in task.items:
        if not item['board name']:
            board_dict['My Board'].append(item)

        for b in item['board name']:
            if b not in board_dict:
                board_dict[b] = [item]
            else:
                board_dict[b].append(item)

    render_prefs['print'] = False
    render_prefs['success'] = None
    for key, value in board_dict.items():
        rn.render_items(value, key, print_stats=False, print_boards=False)

    c, s, p = rn.calculate_stats()
    rn.pr_stats(c, s, p)


def edit(arg):
    num, header = arg.lsplit(" ", 1) if " " in arg else (arg, "")
    header = header.strip()
    if not header:
        return

    for item in task.items:
        if item['number'] == num:
            render_prefs['success'] = True
            item['header'] = header
            break

    write_json_items() if render_prefs['success'] else None


def oneline():
    render_prefs['print'] = False
    render_prefs['print'] = None
    rn.render_oneline()


def begin(nums):
    for item in task.items:
        if item['number'] in nums and item["type"] == "task":
            if item['status'] != "in-progress":
                item['status'] = "in-progress"

            else:
                item['status'] = "undone"
            render_prefs['success'] = True
    write_json_items() if render_prefs['success'] else None


def refactor(do_archive=True):
    for inx, item in enumerate(task.items):
        item['number'] = inx + 1
    write_json_items()

    if do_archive:
        for inx, item in enumerate(task.archive):
            item['number'] = inx + 1
        write_json_archive()
    render_prefs['success'] = True


def clear(path):
    if os.path.exists(path):
        os.remove(path)
    task.archive.clear()
    refactor(False)
    write_json_archive()
    render_prefs['success'] = True


def attach_to_board(arg):
    nums, book = arg.rsplit(" ", 1) if " " in arg else (arg, "")
    nums = [int(s) for s in nums.split() if s.isdigit()]
    if not book or not nums:
        return

    for item in task.items:
        if item['number'] in nums and item['type']:
            if book not in item['board name']:
                item['board name'].append(book)
                render_prefs['success'] = True

    write_json_items() if render_prefs['success'] else None


def move(arg):
    nums, book = arg.rsplit(" ", 1) if " " in arg else (arg, "")
    nums = [int(s) for s in nums.split() if s.isdigit()]
    if not nums:
        return

    for item in task.items:
        if item['number'] in nums:  # there is some error. check later
            if book not in item['board name']:
                item['board name'].clear()
                bookst = book.strip()
                if bookst:
                    item['board name'].append(bookst)
                render_prefs['success'] = True
    write_json_items() if render_prefs['success'] else None
