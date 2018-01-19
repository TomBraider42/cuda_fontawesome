from cudatext import *
import cudatext as app
import cudatext_cmd
import os
import re
import codecs


MIN_VERSION = '1.34.1'


class Command:


    title = 'Font Awesome'
    options_filename = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_fontawesome.json')
    options = {'code_format': '<i class="{font} fa-{name}"></i> '}
    codes = []
    version_warning = False


    '''
    load options
    '''
    def __init__(self):

        self.check_app_version()

        if os.path.isfile(self.options_filename):
            with open(self.options_filename) as fin:
                self.options = json.load(fin)


    '''
    read CSS file, add site panel
    '''
    def on_start(self, ed):

        dir = os.path.dirname(__file__)

        with codecs.open(os.path.join(dir, 'vendors', 'fontawesome.css'), 'r', encoding='utf-8', errors='ignore') as text:
            self.parse_css(text)

        id_dlg = self.init_panel()
        app_proc(PROC_SIDEPANEL_ADD_DIALOG, (self.title, id_dlg, os.path.join(dir, 'fontawesome.png')))


    '''
    open config file
    '''
    def show_config(self):

        if not os.path.isfile(self.options_filename):
            with open(self.options_filename, mode="w", encoding='utf8') as fout:
                json.dump(self.options, fout, indent=0)

        file_open(self.options_filename)


    '''
    insert selected icon code in editor
    '''
    def get_icon(self, idd, idc, data):

        # set selected font
        fontid = dlg_proc(idd, DLG_CTL_FIND, prop='fafont')
        cap = dlg_proc(idd, DLG_CTL_PROP_GET, index=fontid).get('cap')
        if cap == 'Brands':
            font = 'fab'
        elif cap == 'Regular':
            font = 'far'
        else:
            font = 'fas'

        # get items
        items = dlg_proc(idd, DLG_CTL_PROP_GET, index=idc).get('items')
        selected = dlg_proc(idd, DLG_CTL_PROP_GET, index=idc).get('val')
        items_names = [i.split('\r')[0] for i in items.split('\t') if i]
        items_codes = [i.split('\r')[1] for i in items.split('\t') if i]

        # create selected code
        name = items_names[int(selected)]
        unicode = items_codes[int(selected)].strip()
        hexcode = ''.join(["%02X " % ord(x) for x in unicode]).strip()
        code = self.options['code_format'].format(font=font, name=name, unicode=unicode, hexcode=hexcode)

        # insert code
        pos = ed.get_carets()[0]
        ed.insert(pos[0], pos[1], code)
        ed.set_caret(pos[0] + len(code), pos[1])
        ed.focus()


    '''
    reload icon list after changing font
    '''
    def set_font(self, idd, idc, data):

        cap = dlg_proc(idd, DLG_CTL_PROP_GET, index=idc).get('cap')
        listid = dlg_proc(idd, DLG_CTL_FIND, prop='falist')

        if cap == 'Brands':
            font = 'Font Awesome 5 Brands Regular'
        elif cap == 'Regular':
            font = 'Font Awesome 5 Free Regular'
        else:
            font = 'Font Awesome 5 Free Solid'
        dlg_proc(idd, DLG_CTL_PROP_SET, index=listid, prop={'font_name': font})


    '''
    create side panel
    '''
    def init_panel(self):

        h = dlg_proc(0, DLG_CREATE)

        n = dlg_proc(h, DLG_CTL_ADD, 'combo_ro')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'fafont',
            'items': 'Solid\tRegular\tBrands',
            'val': 0,
            'align': ALIGN_TOP,
            'y': 0,
            'font_size': 12,
            'act': True,
            'on_change': lambda idd, idc, data: self.set_font(idd, idc, data)
            })

        n = dlg_proc(h, DLG_CTL_ADD, 'filter_listview')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'f_falist',
            'align': ALIGN_TOP,
            'y': 30,
            'font_size': 12,
            'props': (True)
            })

        items = 'x=0\rIcon=45\rText=200\t'
        items = items + '\t'.join(code[0] + '\r ' + chr(int(code[1], 16)) + '\r' + u'\u0080'.join(list(code[0])) for code in self.codes)

        l = dlg_proc(h, DLG_CTL_ADD, 'listview')
        dlg_proc(h, DLG_CTL_PROP_SET, index=l, prop={
            'name': 'falist',
            'items': items,
            'align': ALIGN_CLIENT,
            'font_name': 'Font Awesome 5 Free Solid',
            'font_size': 12,
            'act': True,
            'on_click': lambda idd, idc, data: self.get_icon(idd, idc, data),
            'props': (True)
            })

        return h


    '''
    parse CSS file for icon codes
    '''
    def parse_css(self, text):

        regtag = re.compile(r'(?:.fa-)(.*)(?:\:before)', re.I)
        reghex = re.compile(r'(?:content\:\s*\"\\)(.*)(?:")', re.I)

        line_nr = 0
        name = ''
        hex = ''

        for line in text:
            line_nr += 1

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
                    self.codes.append([name, hex])
                    name = ''


    '''
    check min needed app version
    '''
    def check_app_version(self):

        if app.app_exe_version() < MIN_VERSION and not self.version_warning:
            # warn only once
            self.version_warning = True
            s = ['Plugin "' + os.path.basename(os.path.dirname(__file__)) + '" needs', 'CudaText version >= ' + MIN_VERSION + ' (now ' + app.app_exe_version() + ')']
            print(' '.join(s))
            msg_box('\n'.join(s), app.MB_OK + app.MB_ICONWARNING)
