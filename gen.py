import os
import xml.dom.minidom
import xml
import gzip

protocol_path = 'c:\\mkoshp-tex\\304\\xmlreports\\'
source_path = 'c:\\mkoshp-tex\\304\\runs\\'

def get_string_status(s):
    return {
        "OK" : "OK",
        "WA" : "Неправильный ответ",
        "ML" : "Превышение лимита памяти",
        "SE" : "Security error",
        "CF" : "Ошибка проверки,<br/>обратитесь к администраторам",
        "PE" : "Неправильный формат вывода",
        "RT" : "Ошибка во время выполнения программы",
        "TL" : "Превышено максимальное время работы",     
        "WT" : "Превышено максимальное общее время работы",     
        "SK" : "Пропущен",     
    }[s]


def get_source_from_file(filename): 
    if os.path.isfile(filename):
        myopen = open
    else:
        filename += '.gz'
        myopen = gzip.open
    try:
        xml_file = myopen(filename, 'rb')
        try:
            res = xml_file.read()
            try:
                return str(res, encoding='UTF-8')
            except TypeError:
                return res
        except Exception as e:
            xml_file = myopen(filename, 'r', encoding='cp1251')
            res = xml_file.read()
            try:
                return str(res, encoding='UTF-8')
            except TypeError:
                return res
    except IOError:
        return ''

def get_from_file(filename): 
    if os.path.isfile(filename):
        myopen = open
    else:
        filename += '.gz'
        myopen = gzip.open
    try:
        xml_file = myopen(filename, 'rb')
        try:
            xml_file.readline()
            xml_file.readline()
            res = xml_file.read()
            try:
                return str(res, encoding='UTF-8')
            except TypeError:
                return res
        except Exception as e:
            return str(e)
    except IOError:
        return ''

def get_protocol(run_id): 
    filename = submit_protocol_path(run_id)
    if filename != '':
        return get_from_file(filename)
    else:
        raise "e";

def submit_source_path(run_id):
    run = int(run_id)
    run_id = str(run_id)
    while len(run_id) < 6:
        run_id = '0' + run_id
    p3 = run // 32 % 32
    p2 = run // 32 // 32 % 32
    p1 = run // 32 // 32 // 32

    return source_path + str(p1) + '\\' + str(p2) + '\\' + str(p3) + '\\' + run_id

def submit_protocol_path(run_id):
    run = int(run_id)
    run_id = str(run_id)
    while len(run_id) < 6:
        run_id = '0' + run_id
    p3 = run // 32 % 32
    p2 = run // 32 // 32 % 32
    p1 = run // 32 // 32 // 32

    return protocol_path + str(p1) + '\\' + str(p2) + '\\' + str(p3) + '\\' + run_id

def get_compilation_protocol(run_id): 
    filename = submit_protocol_path(run_id)
#        return filename
    if filename:
        if os.path.isfile(filename):
            myopen = lambda x,y : open(x, y, encoding='utf-8')
        else:
            filename += '.gz'
            myopen = gzip.open
        try:
            xml_file = myopen(filename, 'r')
            try:
                res = xml_file.read()
                try:
                    return str(res, encoding='UTF-8')
                except TypeError:
                    return res
            except Exception as e:
                return e
        except IOError as e:
            return e
    else:
        return ''

def get_tested_protocol_data(run_id):
    return parsetests(xml.dom.minidom.parseString(str(get_protocol(run_id))))

def parsetests(xml):
    res = {}
    res['tests'] = {}
    test_count = 0
    if xml:
        rep = xml.getElementsByTagName('testing-report')[0]
        res['tests_count'] = int(rep.getAttribute('run-tests'))
        res['status'] = get_string_status(rep.getAttribute('status'))
        for node in xml.getElementsByTagName('test'):
            number = node.getAttribute('num')
            status = node.getAttribute('status')
            time = node.getAttribute('time')
            try:
                comment = node.getElementsByTagName('checker')[0].firstChild.nodeValue
            except:
                if status == 'RT':
                    try:
                        comment = node.getElementsByTagName('stderr')[0].firstChild.nodeValue
                    except:
                        comment = ''
            real_time = node.getAttribute('real-time')
            max_memory_used = node.getAttribute('max-memory-used')
            test_count += 1
            try:
               time = int(time)
            except ValueError:
               time = 0

            try:
               real_time = int(real_time)
            except ValueError:
               real_time = 0
               
            test = {'status': status, 
                    'string_status': get_string_status(status), 
                    'real_time': real_time, 
                    'time': time,
                    'max_memory_used' : max_memory_used,
                    'comment' : comment
                   }
            res['tests'][number] = test
    return res


def get_source_tex(run_id):
    source = get_source_from_file(submit_source_path(run_id))
    source = source.replace('\r\n', '\n')
    res = '\n\\begin{lstlisting}[' + 'language=c++, label=r{0}, caption=Решение №{0}]'.format(int(run_id))
    res += '\n' + source + '\n'
    res += '\\end{lstlisting}\n\n'
    return res

def get_protocol_tex(run_id):
    protocol = get_tested_protocol_data(run_id)   
    res = '''\\begin{longtabu} to \\linewidth{|p{1cm}|p{2.5cm}|p{1.5cm}|p{2.5cm}|p{1.5cm}|p{5cm}|}\
\\caption{Протокол проверки №3492}\\\\\
\\hline\
№ теста & Результат & ЦПУ, сек. & Общее время, сек. & Память & Комментарий по результату работы \\\\\
\\hline\n'''
    for num, test in protocol['tests'].items():
        res += '{0} & {1} & {2} & {3} & {4} & {5}\\\\\\hline\n'.format(num, test['status'], test['time'], test['real_time'], test['max_memory_used'], '\\begin{verbatim}\n' + test['comment'] + '\n\\end{verbatim}')
    res += '\\end{longtabu}'
    return res

def get_run_tex(run_id, time, school, name, lang_name, prob_name):
    protocol = get_tested_protocol_data(run_id)
    run_id = int(run_id)
    res = '''На {0} минуте олимпиады {1} ``{2}\'\' отправила на проверку решение по задаче {3} на языке программирования {4} (Решение №{5})\
, которое получило вердикт ``{6}\'\' (Протокол проверки №{5})'''.format(time, school, name, prob_name, lang_name, run_id, protocol['status'])
    res += get_source_tex(run_id)
    res += get_protocol_tex(run_id)
    return res

if __name__ == '__main__':
    runs = {1219, 1217, 1218, 1216}
    for run_id in runs:
        with open(str(run_id) + '.tex', "w", encoding='utf8') as f:
            f.write(get_run_tex(run_id, 28, 'команда Гимназии №1543', 'Суслики', 'GNU C++ 4.7', 'A.``Слоники\'\''))
    #print(get_tested_protocol_data(run_id))
    #print(get_from_file(submit_source_path(run_id)))