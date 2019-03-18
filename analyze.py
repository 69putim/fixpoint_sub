# -*- coding: utf-8 -*-
import datetime
import glob
import os
import re
from datetime import timedelta

# --------------
# グローバル変数
# -------------
current_dir = os.path.dirname(os.path.abspath(__file__))  # カレントディレクトリ
log_data_dir = os.path.join(current_dir, "log/")  # logが置いてあるディレクトリへの絶対パス


# デバッグ
# print(current_dir)
# print(log_data_dir)

# -------
# 関数など
# ------

# 指定したlogファイルを読み込む
# Main内でget_log_from_file(test.log)のようにファイル名をしてして使う
def get_log_from_file(file_name):
    file_path = os.path.join(log_data_dir + file_name)
    if not os.path.exists(file_path):
        print('ERROR:指定するファイル名を間違っているまたは、ファイルの内容がありません。\n{0}'.format(file_path))
        quit()
    log_file = open(file_path, 'r', encoding='utf-8')

    log_data = log_file.read()
    log_file.close()

    return log_data


# 複数のlogファイルを読み込む
def read_log_files():
    all_log_data = ''

    # パスが存在しない場合
    if not os.path.exists(log_data_dir):
        print('ERROR:指定されたパスが存在しません。\n{0}'.format(log_data_dir))
        quit()

    # 複数のファイルの内容をall_log_dataにまとめる
    # log_data_dirにある全てのファイル名のリストを作成
    # all_files = ["test.log", "test1.log"]のようにファイル名のみをリスト化
    all_files = [os.path.basename(p) for p in glob.glob(os.path.join(log_data_dir + "*.log")) if os.path.isfile(p)]

    for file_name in all_files:
        all_log_data += get_log_from_file(file_name)

        if len(all_log_data) == 0:
            print('ERROR:指定されたパスにファイルまたは、ファイルの内容がありません。\n{0}'.format(all_log_data))
            quit()

    print(all_files)
    print('ファイル読み込みは完了')

    return all_log_data


# 正規表現を作成
def make_regex():
    # リモートホスト名(ip_address) output_index(0)
    remote_host = r"(\S+)"
    # クライアントの識別子
    remote_logname = " (\S+|-)"
    # 認証ユーザー名
    remote_user = " (\S+|-)"
    # リクエストを受信した時刻([day/month/year:hour:minute:second zone]の書式)
    time_recieved = " \[([^\]]+)\]"
    # リクエストの最初の行
    request_first_line = " ([\w]?[\s]?.*?[\s]?[HTTP]/[\d]+.[\d]+)"
    # 最後のレスポンスのステータス
    statusCode = " ([\d]{3})"
    # HTTPヘッダを除くレスポンスのバイト数。0バイトの場合は「-」と表示される
    response_bytes_clf = " ([\d]+|-)"
    # サーバが受信したリクエストヘッダのReferer
    request_header_referer = " ([http]+[s]?[\:\/\/]+[www\.][\S]+[\.]+[\S]+|-)"
    # サーバが受信したリクエストヘッダのUser-Agent
    request_header_user_agent = " .*?(.+)"
    # # 末尾
    # end = '.*?\n'

    rule = remote_host + remote_logname + remote_user + time_recieved + request_first_line + \
            statusCode + response_bytes_clf + request_header_referer + request_header_user_agent
    # print("正規表現:{0}".format(rule))

    return rule


# 正規表現に従って変換
def do_findall(rule, content):
    # 処理便利のため、"を除く
    content = re.sub('"', '', content)
    # findall実施
    results = re.findall(rule, content)

    if not results:
        print('結果件数：0')
        quit()

    print('結果件数：{0}'.format(len(results)))

    return results


# strをdatetimeオブジェクトに変換
def time_str_to_int(content):
    # contentをタプルから、リストに変換しnew_contentとする
    # (('10.2.3.4', '-', '-', '18/Apr/2005:00:10:47 +0900' --> [('10.2.3.4', '-', '-', '18/Apr/2005:00:10:47 +0900'
    new_content = list(content)
    # 全ての時間表記をdatetimeにする
    for i, row in enumerate(new_content):
        # それぞれの要素がタプルなので、リストに変換する
        # ('10.2.3.4', '-', '-', '18/Apr/2005:00:10:47 +0900' --> ['10.2.3.4', '-', '-', '18/Apr/2005:00:10:47 +0900'
        lst = list(row)
        # strからdatetimeオブジェクトに変換
        lst[3] = datetime.datetime.strptime(lst[3], "%d/%b/%Y:%H:%M:%S %z")
        # それぞれの要素をタプルに戻す
        tpl = tuple(lst)
        new_content[i] = tpl

    # new_contentをタプルに戻す
    tpl_new_content = tuple(new_content)

    return tpl_new_content

#　キーの一覧を作る
# intは0~8：それぞれ、リモートホスト名、クライアントの識別子、・・・、サーバが受信したリクエストヘッダのUser-Agentを示す
def create_dict(data, int):
    log_dict = {}
    for i, line in enumerate(data):
        tmp = {i : line[int]}
        log_dict.update(tmp)

    return log_dict

# キーの種類と数を数える
def key_count(log_dict):
    count_dict = {}
    for v in log_dict.values():
        if v not in count_dict:
            update_data = {v : 1}
            count_dict.update(update_data)
        else:
            count_dict[v] += 1
    return count_dict

# ------
# main
# -----

# 指定したlogファイルを読み込む
data = get_log_from_file("test1.log")
# logフォルダ内の全てのlogファイルを読み込む
# data = read_log_files()

# 扱いやすいように値を変換
regex = make_regex()
results = do_findall(regex, data)
fix_time = time_str_to_int(results)

if __name__ == "__main__":
    print("\n")
    # アクセスの多いローカルホスト
    dict_acc = create_dict(fix_time, 0)
    count_dict_acc = key_count(dict_acc)
    for k, v in sorted(count_dict_acc.items(), key=lambda x:(x[1], x[0]), reverse=True):
        print("host:{0:15s}".format(k), "count:", v)

    print("\n")
    # 各時間毎のアクセス数
    dict_time = create_dict(fix_time, 3)
    count_dict_time = key_count(dict_time)
    for k, v in sorted(count_dict_time.items(), key=lambda x:(x[1], x[0]), reverse=True):
        print("Access_Time:", k, "count:", v)


# start = datetime.datetime(2004, 0o1, 0o1, 0, 0, 0, 0, tzinfo=datetime.timezone(datetime.timedelta(0, 32400)))
# end   = datetime.datetime(2007, 0o1, 0o1, 0, 0, 0, 0, tzinfo=datetime.timezone(datetime.timedelta(0, 32400)))
#
# for target in dict_time:
#     print(target)
#     if start <= target <= end:
#           if target not in dict_time.values():
#               del [target]
#           print(target)
# print(fix_time[0][0])
# print(type(fix_time))


