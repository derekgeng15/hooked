import argparse
import sqlite3
import sys
import textwrap

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
    parser.add_argument("classid", type=int,
                        help="the id of the class whose details should be shown")
    return parser.parse_args()

# --- print details---
def print_details(classid, days, start, end, bldg, room, 
                  courseid, area, title, descrip, prereqs, proflist, crosslisting_names):

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


# -- helper function to get rows ---
def fetch_data(cur, classid):
    cur.execute("""
        SELECT classid, courseid, days, starttime, endtime, bldg, roomnum
        FROM classes
        WHERE classid = ?;
    """, (classid,))
    class_row = cur.fetchone()

    if class_row is None:
        return None, None

    courseid = class_row[1]

    cur.execute("""
        SELECT courseid, area, title, descrip, prereqs
        FROM courses
        WHERE courseid = ?;
    """, (courseid,))
    course_row = cur.fetchone()

    cur.execute("""
        SELECT profs.profname
        FROM profs
        JOIN coursesprofs
        ON profs.profid = coursesprofs.profid
        WHERE coursesprofs.courseid = ?
        ORDER BY profs.profname;
    """, (courseid,))
    proflist = [name for (name,) in cur.fetchall()]

    cur.execute("""
        SELECT dept, coursenum
        FROM crosslistings
        JOIN courses
        ON courses.courseid = crosslistings.courseid
        WHERE courses.courseid = ?
        ORDER BY crosslistings.dept, crosslistings.coursenum;
    """, (courseid,))
    crosslisting_names = [f"{dept} {coursenum}" for (dept, coursenum) in cur.fetchall()]

    return class_row, course_row, proflist, crosslisting_names


def get_courseID(args, cur):
    cur.execute(
        "SELECT courseid FROM classes WHERE classid = ?;",
        (args.classid,)
        )
    row = cur.fetchone()

    if row is None:
        print(f"{sys.argv[0]}: no class with classid {args.classid} exists", file=sys.stderr)
        sys.exit(1)

    return row[0]

# --- main function ---
# When executed via a command that contains a valid classid, your regdetails.py must write to stdout the 
# classid, courseid, days, starttime, endtime, bldg, roomnum, dept(s), coursenum(s), area, title, descrip, prereqs, 
# and profname(s) for the class with the given classid. 
def main():
    args = parse_args()
    conn = connect_db()
    cur = conn.cursor()

    try:
        # parse args
        courseid = get_courseID(args, cur)
        class_row, course_row, proflist, crosslisting_names = fetch_data(cur, args.classid)

        # save variables
        (classid, courseid, days, start, end, bldg, room) = class_row
        (_, area, title, descrip, prereqs) = course_row

        print_details(
            classid, days, start, end, bldg, room,
            courseid, area, title, descrip, prereqs, proflist, crosslisting_names
        )

    except sqlite3.Error as exc:
        print(f"{sys.argv[0]}: {exc}", file=sys.stderr)
        sys.exit(1)

    finally:
        conn.close()
    
    sys.exit(2)


if __name__ == '__main__':
    main()