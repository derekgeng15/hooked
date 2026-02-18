import sys
import json, socket
import argparse, textwrap

# --- parse arguments ---
def parse_args():
    parser = argparse.ArgumentParser(
        prog="regoverviews.py",
        description="Registrar application: show overviews of classes"
    )

    parser.add_argument("-d", dest="dept", metavar="dept", type=str.lower,
                        help="show only those classes whose department contains dept")
    parser.add_argument("-n", dest="num", metavar="num", type=str.lower,
                        help="show only those classes whose course number contains num")
    parser.add_argument("-a", dest="area", metavar="area", type=str.lower,
                        help="show only those classes whose distrib area contains area")
    parser.add_argument("-t", dest="title", metavar="title", type=str.lower,
                        help="show only those classes whose course title contains title")

    parser.add_argument("host", help="the computer on which the server is running")
    parser.add_argument("port", type=int, help="the port at which the server is listening")

    return parser.parse_args()

# --- wrap text ---
def wrap_text(text):
    return textwrap.fill(
        text,
        width=72,
        subsequent_indent=' ' * 23,
        break_long_words=False,
        break_on_hyphens=False
    )

# --- print overview ---
def print_overview(rows):
    print("ClsId Dept CrsNum Area Title")
    print("----- ---- ------ ---- -----")

    for d in rows:
        classid = d["classid"]
        dept = d["dept"]
        num = d["coursenum"]
        area = d["area"]
        title = d["title"]

        row = '%5s %4s %6s %4s %s' % (classid, dept, num, area or '', title)
        print(wrap_text(row))


# --- request details ---
def request_overviews(host, port, dept, num, area, title):

    filters = {
        "dept": dept or "",
        "coursenum": num or "",
        "area": area or "",
        "title": title or ""
    }

    req_obj = ["get_overviews", filters]
    req_str = json.dumps(req_obj)

    try:
        with socket.create_connection((host, port)) as sock:
            in_flo = sock.makefile(mode="r", encoding="utf-8", newline="\n")
            out_flo = sock.makefile(mode="w", encoding="utf-8", newline="\n")

            out_flo.write(req_str + "\n")
            out_flo.flush()

            resp_str = in_flo.readline()
            if resp_str == "":
                raise ConnectionError("server closed connection")

            resp = json.loads(resp_str.rstrip())
            return resp[0], resp[1]

    except OSError as ex:
        print(f"{sys.argv[0]}: {ex}", file=sys.stderr)
        sys.exit(1)

# --- main function ---
def main():
    args = parse_args()
    success, data = request_overviews( args.host, args.port, args.dept, args.num, args.area, args.title)

    if not success:
        print(f"{sys.argv[0]}: {data}", file=sys.stderr)
        sys.exit(1)

    print_overview(data)
    sys.exit(0)


if __name__ == '__main__':
    main()
