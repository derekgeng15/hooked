import argparse, textwrap
import sys
import socket, json

# --- helper func to wrap text ---
def wrap_txt(text):
    return "\n".join(textwrap.wrap(
        text,
        width=72,
        subsequent_indent=' ' * 23,
        break_long_words=False,
        break_on_hyphens=False,
        drop_whitespace=True
    ))


# --- parse arguments ---
def parse_args():
    parser = argparse.ArgumentParser(
        prog="regdetails.py",
        description="Registrar application: show details about a class"
    )
    parser.add_argument("host", help="the computer on which the server is running")
    parser.add_argument("port", type=int, help="the port at which the server is listening")
    parser.add_argument("classid", type=int, help="the id of the class whose details should be shown")
    return parser.parse_args()

# --- request details ---
def request_details(host, port, classid):
    req_obj = ["get_details", classid]
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

            resp_str = resp_str.rstrip()
            resp = json.loads(resp_str)
            return resp[0], resp[1]


    except OSError as ex:
        print(f"{sys.argv[0]}: {ex}", file=sys.stderr)
        sys.exit(1)


# --- print details---
def print_details(data):
    
    crosslisting_names = [f"{x['dept']} {x['coursenum']}" for x in data["deptcoursenums"]]

    classid, days, start, end, bldg, room, courseid, area, title, descrip, prereqs, proflist = (
        data["classid"], data["days"], data["starttime"], data["endtime"], data["bldg"], data["roomnum"],
        data["courseid"], data["area"], data["title"], data["descrip"], data["prereqs"],
        data["profnames"]
    )

    print("-------------")
    print("Class Details")
    print("-------------")

    print(f"Class Id: {classid}")
    print(f"Days: {days}")
    print(f"Start time: {start}")
    print(f"End time: {end}")
    print(f"Building: {bldg}")
    print(f"Room: {room}")

    print("--------------")
    print("Course Details")
    print("--------------")

    print(f"Course Id: {courseid}")
    for x in crosslisting_names:
        print(f"Dept and Number: {x}")
    print(f"Area: {area or ''}")

    title_fmt = wrap_txt("Title: " + (title or ""))
    print(f"{title_fmt}")

    desc_fmt = wrap_txt("Description: " + (descrip or ""))
    print(f"{desc_fmt}")

    prereqs_fmt = wrap_txt("Prerequisites: " + (prereqs or ""))
    print(f"{prereqs_fmt}")

    for name in proflist:
        print(f"Professor: {name}")

def main():
    args = parse_args()

    success, data = request_details(args.host, args.port, args.classid)

    if not success:
        print(f"{sys.argv[0]}: {data}", file=sys.stderr)
        sys.exit(1)

    print_details(data)
    sys.exit(0)

if __name__ == '__main__':
    main()