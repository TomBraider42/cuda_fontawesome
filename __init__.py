from cudatext import *
import cudatext as app
import cudatext_cmd
import os
import re
import json
import codecs


class Command:


    title = 'Font Awesome'
    options_filename = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_fontawesome.json')
    options = {
        'iconsize': 24,
        'FONT_SOLID': 'Font Awesome 5 Free Solid',
        'FONT_REGULAR': 'Font Awesome 5 Free Regular',
        'FONT_BRANDS': 'Font Awesome 5 Brands Regular',
        'code_format': '<i class="{font} fa-{name}"></i>'
        }
    codes = []


    def __init__(self):
        '''
        load options
        '''
        if os.path.isfile(self.options_filename):
            with open(self.options_filename) as fin:
                self.options.update(json.load(fin))

        self.font = self.options['FONT_SOLID']
        self.h_dlg = None


    def show(self):
        '''
        read CSS file, add site panel
        '''
        dir = os.path.dirname(__file__)

        with codecs.open(os.path.join(dir, 'vendors', 'fontawesome.css'), 'r', encoding='utf-8', errors='ignore') as text:
            self.parse_css(text)

        id_dlg = self.init_panel()
        app_proc(PROC_SIDEPANEL_ADD_DIALOG, (self.title, id_dlg))
        app_proc(PROC_SIDEPANEL_ACTIVATE, self.title)


    def on_state(self, ed, state):
        '''
        update panel after changing theme
        '''
        if self.h_dlg and state == APPSTATE_THEME_UI:
            self.get_theme_colors()
            dlg_proc(self.h_dlg, DLG_CTL_PROP_SET, name='filter', prop={'color': self.color_bg, 'font_color': self.color_font})
            dlg_proc(self.h_dlg, DLG_CTL_PROP_SET, name='falist', prop={'color': self.color_bg})


    def init_panel(self):
        '''
        create side panel
        '''
        h = dlg_proc(0, DLG_CREATE)
        self.h_dlg = h
        fontsize = self.options['iconsize'] // 2

        self.get_theme_colors()

        # font select
        n = dlg_proc(h, DLG_CTL_ADD, 'button_ex')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'fafont',
            'hint': 'used Font',
            'align': ALIGN_TOP,
            'y': 0,
            'color': self.color_bg,
            'font_color': self.color_font,
            'act': True,
            'on_change': lambda idd, idc, data: self.set_font(idd, idc, data)
            })
        self.h_font = dlg_proc(h, DLG_CTL_HANDLE, index=n)
        button_proc(self.h_font, BTN_SET_KIND, BTNKIND_TEXT_CHOICE)
        button_proc(self.h_font, BTN_SET_ARROW, True)
        button_proc(self.h_font, BTN_SET_ARROW_ALIGN, 'C')
        button_proc(self.h_font, BTN_SET_ITEMS, 'Solid Font\nRegular Font\nBrands Font')
        button_proc(self.h_font, BTN_SET_ITEMINDEX, 0)
        button_proc(self.h_font, BTN_SET_FOCUSABLE, False)

        # filter
        f = dlg_proc(h, DLG_CTL_ADD, 'edit')
        dlg_proc(h, DLG_CTL_PROP_SET, index=f, prop={
            'name': 'filter',
            'align': ALIGN_TOP,
            'hint': 'Filter',
            'y': self.options['iconsize'] + 5,
            'color': self.color_bg,
            'font_color': self.color_font,
            'font_size': fontsize,
            'ex0': False, 
            'ex1': False, 
            'ex2': True,
            'act': True,
            'on_change': lambda idd, idc, data: self.fill_list()
            })

        # listbox
        l = dlg_proc(h, DLG_CTL_ADD, 'listbox_ex')
        dlg_proc(h, DLG_CTL_PROP_SET, index=l, prop={
            'name': 'falist',
            'align': ALIGN_CLIENT,
            'color': self.color_bg,
            'on_draw_item': self.callback_listbox_drawitem,
            'on_click': lambda idd, idc, data: self.get_icon(idd, idc, data)
            })

        self.h_list = dlg_proc(h, DLG_CTL_HANDLE, index=l)
        listbox_proc(self.h_list, LISTBOX_SET_ITEM_H, index=self.options['iconsize'])
        listbox_proc(self.h_list, LISTBOX_SET_DRAWN, index=1)

        self.fill_list()

        return h


    def fill_list(self):
        '''
        fill list with items
        '''
        filter = dlg_proc(self.h_dlg, DLG_CTL_PROP_GET, name='filter').get('val')

        listbox_proc(self.h_list, LISTBOX_DELETE_ALL)
        for code in self.codes:
            if filter in code:
                listbox_proc(self.h_list, LISTBOX_ADD, index=-1, text=code)
        listbox_proc(self.h_list, LISTBOX_SET_TOP, index=0)
        listbox_proc(self.h_list, LISTBOX_SET_SEL, index=0)


    def callback_listbox_drawitem(self, id_dlg, id_ctl, data='', info=''):
        '''
        create list item
        '''
        idc = data['canvas']
        r = data['rect']
        index = data['index']
        selected = listbox_proc(self.h_list, LISTBOX_GET_SEL)
        item = listbox_proc(self.h_list, LISTBOX_GET_ITEM, index=index)[0].split('|')
        name = item[0]
        hex = item[1]
        iconsize = self.options['iconsize']

        # set colors
        if index == selected:
            color = self.color_sel_font
            bgcolor = self.color_sel_bg
        else:
            color = self.color_font
            bgcolor = self.color_bg

        canvas_proc(idc, CANVAS_SET_BRUSH, color=bgcolor, style=BRUSH_SOLID)
        canvas_proc(idc, CANVAS_RECT_FILL, x=r[0], y=r[1], x2=r[2], y2=r[3])

        # name
        canvas_proc(idc, CANVAS_SET_FONT, color=color, text='Arial', size=iconsize//2)
        size = canvas_proc(idc, CANVAS_GET_TEXT_SIZE, text=name)
        canvas_proc(idc, CANVAS_TEXT, text=name, x=iconsize+10, y=(r[1]+r[3]-size[1])//2)

        # icon
        canvas_proc(idc, CANVAS_SET_FONT, text=self.font, size=iconsize//2+2)
        canvas_proc(idc, CANVAS_TEXT, text=chr(int(hex, 16)), x=5, y=(r[1]+r[3]-size[1])//2)


    def set_font(self, idd, idc, data):
        '''
        reload icon list after changing font
        '''
        sel = button_proc(self.h_font, BTN_GET_ITEMINDEX)
        if sel == 2:
            self.font = self.options['FONT_BRANDS']
        elif sel == 1:
            self.font = self.options['FONT_REGULAR']
        else:
            self.font = self.options['FONT_SOLID']

        self.fill_list()


    def get_icon(self, idd, idc, data):
        '''
        insert selected icon code in editor
        '''
        # set selected font
        sel = button_proc(self.h_font, BTN_GET_ITEMINDEX)
        if sel == 2:
            font = 'fab'
        elif sel == 1:
            font = 'far'
        else:
            font = 'fas'

        # get items
        index_sel = listbox_proc(self.h_list, LISTBOX_GET_SEL)
        item = listbox_proc(self.h_list, LISTBOX_GET_ITEM, index=index_sel)[0].split('|')

        # create selected code
        name = item[0]
        hexcode = item[1]
        unicode = chr(int(hexcode, 16))
        code = self.options['code_format'].format(font=font, name=name, unicode=unicode, hexcode=hexcode)

        # insert code
        pos = ed.get_carets()[0]
        ed.insert(pos[0], pos[1], code)
        ed.set_caret(pos[0] + len(code), pos[1])
        ed.focus()


    def parse_css(self, text):
        '''
        parse CSS file for icon codes
        '''
        regtag = re.compile(r'(?:.fa-)(.*)(?:\:before)', re.I)
        reghex = re.compile(r'(?:content\:\s*\"\\)(.*)(?:")', re.I)

        name = ''
        hex = ''

        for line in text:
            ls = line.strip()

            # find tag
            foundtag = regtag.findall(line)
            for tag in foundtag:
                if tag:
                    name = tag

            # find hex
            foundhex = reghex.findall(line)
            for hex in foundhex:
                if name and hex:
                    self.codes.append(name + '|' + hex)
                    name = ''


    def show_config(self):
        '''
        open config file
        '''
        with open(self.options_filename, mode="w", encoding='utf8') as fout:
            json.dump(self.options, fout, indent=2)

        file_open(self.options_filename)


    def get_theme_colors(self):
        '''
        get colors from current theme
        '''
        ui = app_proc(PROC_THEME_UI_DICT_GET, '')
        self.color_bg = ui['TreeBg']['color']
        self.color_font = ui['TreeFont']['color']
        self.color_sel_bg = ui['TreeSelBg']['color']
        self.color_sel_font = ui['TreeSelFont']['color']
