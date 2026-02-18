#!/usr/bin/env python3
import os, sys
import socket, json, threading
import argparse
import sqlite3

SERVER_ERROR_MESSAGE = "A server error occurred. Please contact the system administrator."

# --- connect to the database ---
def connect_db():
    return sqlite3.connect("reg.sqlite")


# --- handle client ---
def handle_client(sock):
    with sock:
        in_flo = sock.makefile(mode='r', encoding='utf-8', newline='\n')
        out_flo = sock.makefile(mode='w', encoding='utf-8', newline='\n')

        try:
            line = in_flo.readline()
            if line == "":
                return
            line = line.rstrip()

            req = json.loads(line)
            cmd = req[0]

            if cmd == "get_overviews":
                data = get_overviews_from_db(req[1])
                resp = [True, data]
            elif cmd == "get_details":
                details = get_details_from_db(req[1])
                resp = [True, details]
            else:
                resp = [False, "Invalid request."]

            out_flo.write(json.dumps(resp) + "\n")
            out_flo.flush()

        except (sqlite3.OperationalError, sqlite3.DatabaseError) as ex:
            print(f"{sys.argv[0]}: {ex}", file=sys.stderr)
            out_flo.write(json.dumps([False, SERVER_ERROR_MESSAGE]) + "\n")
            out_flo.flush()

        except ValueError as ex:
            out_flo.write(json.dumps([False, str(ex)]) + "\n")
            out_flo.flush()

        except Exception as ex:
            print(f"{sys.argv[0]}: {ex}", file=sys.stderr)
            try:
                out_flo.write(json.dumps([False, SERVER_ERROR_MESSAGE]) + "\n")
                out_flo.flush()
            except Exception:
                pass

# -- escape ---
def escape_like(text):
    text = text.replace("\\", "\\\\")
    text = text.replace("%", "\\%")
    text = text.replace("_", "\\_")
    return text

# --- build query based on args ---
def build_overview_query(filters):
    cmd = """
    SELECT classes.classid,
           crosslistings.dept,
           crosslistings.coursenum,
           courses.area,
           courses.title
    FROM classes
    JOIN courses
      ON courses.courseid = classes.courseid
    JOIN crosslistings
      ON crosslistings.courseid = classes.courseid
    """

    conditions = []
    params = []

    dept = filters.get("dept", "") or ""
    coursenum = filters.get("coursenum", "") or ""
    area = filters.get("area", "") or ""
    title = filters.get("title", "") or ""

    if dept:
        conditions.append("LOWER(crosslistings.dept) LIKE ? ESCAPE '\\'")
        params.append(f"%{escape_like(dept.lower())}%")

    if coursenum:
        conditions.append("LOWER(crosslistings.coursenum) LIKE ? ESCAPE '\\'")
        params.append(f"%{escape_like(coursenum.lower())}%")

    if area:
        conditions.append("LOWER(courses.area) LIKE ? ESCAPE '\\'")
        params.append(f"%{escape_like(area.lower())}%")

    if title:
        conditions.append("LOWER(courses.title) LIKE ? ESCAPE '\\'")
        params.append(f"%{escape_like(title.lower())}%")

    if conditions:
        cmd += " WHERE " + " AND ".join(conditions)

    cmd += """
    ORDER BY crosslistings.dept,
             crosslistings.coursenum,
             classes.classid
    """
    return cmd, params

# --- function to get class overviews from db ---
def get_overviews_from_db(filters):
    conn = connect_db()
    try:
        cur = conn.cursor()
        cmd, params = build_overview_query(filters)
        cur.execute(cmd, params)
        rows = cur.fetchall()
        result = []
        for (classid, dept, num, area, title) in rows:
            result.append({
                "classid": classid,
                "dept": dept,
                "coursenum": num,
                "area": area or "",
                "title": title or ""
            })
        return result
    finally:
        conn.close()

# -- helper function to get details from database using sql ---
def sql_cmds_details(cur, classid):

    # --- check class maps to course ---
    cur.execute(
        "SELECT courseid FROM classes WHERE classid = ?;",
        (classid,)
        )
    row = cur.fetchone()

    if row is None:
        raise ValueError(f"no class with classid {classid} exists")

    # --- obtain class data ---
    cur.execute("""
        SELECT classid, courseid, days, starttime, endtime, bldg, roomnum
        FROM classes
        WHERE classid = ?;
    """, (classid,))
    class_row = cur.fetchone()
    (classid, courseid, days, start, end, bldg, room) = class_row

    courseid = class_row[1]
    
    # --- obtain course info ---
    cur.execute("""
        SELECT courseid, area, title, descrip, prereqs
        FROM courses
        WHERE courseid = ?;
    """, (courseid,))
    course_row = cur.fetchone()
    (_, area, title, descrip, prereqs) = course_row

    # --- obtain prof list ---
    cur.execute("""
        SELECT profs.profname
        FROM profs
        JOIN coursesprofs
        ON profs.profid = coursesprofs.profid
        WHERE coursesprofs.courseid = ?
        ORDER BY profs.profname;
    """, (courseid,))
    proflist = [name for (name,) in cur.fetchall()]

    # --- obtain crosslisting names ---
    cur.execute("""
        SELECT dept, coursenum
        FROM crosslistings
        JOIN courses
        ON courses.courseid = crosslistings.courseid
        WHERE courses.courseid = ?
        ORDER BY crosslistings.dept, crosslistings.coursenum;
    """, (courseid,))
    
    deptcoursenums = [
        {"dept": dept, "coursenum": coursenum}
        for (dept, coursenum) in cur.fetchall()
    ]

    # --- build the full dictionary ---
    details = {
        "classid": classid,
        "days": days,
        "starttime": start,
        "endtime": end,
        "bldg": bldg,
        "roomnum": room,
        "courseid": courseid,
        "deptcoursenums": deptcoursenums,
        "area": area or "",
        "title": title or "",
        "descrip": descrip or "",
        "prereqs": prereqs or "",
        "profnames": proflist
    }

    return details

# --- function to get class details from db ---
def get_details_from_db(classid):
    conn = connect_db()
    try:
        cur = conn.cursor()
        return sql_cmds_details(cur, classid)
    finally:
        conn.close()

# --- main function ---
def main():
    parser = argparse.ArgumentParser(
        prog="regserver.py",
        description="Server for the registrar application"
    )
    parser.add_argument("port", type=int, help="the port at which the server should listen")
    args = parser.parse_args()

    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if os.name != 'nt':
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_sock.bind(("", args.port))
        server_sock.listen()

    except OSError as ex:
        print(f"{sys.argv[0]}: {ex}", file=sys.stderr)
        sys.exit(1)

    while True:
        try:
            sock, _ = server_sock.accept()
            threading.Thread(target=handle_client, args=(sock,), daemon=True).start()
        except Exception as ex:
            print(f"{sys.argv[0]}: {ex}", file=sys.stderr)


if __name__ == "__main__":
    main()
