import argparse
import sqlite3
import sys
import textwrap

# --- parse arguments ---
def parse_args():
    parser = argparse.ArgumentParser(
        description="Registrar application: show overviews of classes"
    )
    parser.add_argument( "-d", dest="dept", metavar="dept", type=str.lower,
                        help="show only those classes whose department contains dept")
    parser.add_argument("-n", dest="num", metavar = "num", type=str.lower,
                        help = "show only those classes whose course number contains num")
    parser.add_argument("-a", dest="area", metavar = "area", type=str.lower,
                        help = "show only those classes whose distrib area contains area")
    parser.add_argument("-t", dest="title", metavar = "title", type=str.lower,
                        help = " show only those classes whose course title contains title")

    return parser.parse_args()

# -- escape ---
def escape_like(text):
    text = text.replace("\\", "\\\\")
    text = text.replace("%", "\\%")
    text = text.replace("_", "\\_")
    return text

# --- build query based on args ---
def build_query(args):
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

    if args.dept:
        conditions.append("LOWER(crosslistings.dept) LIKE ? ESCAPE '\\'")
        params.append(f"%{escape_like(args.dept)}%")

    if args.num:
        conditions.append("LOWER(crosslistings.coursenum) LIKE ? ESCAPE '\\'")
        params.append(f"%{escape_like(args.num)}%")

    if args.area:
        conditions.append("LOWER(courses.area) LIKE ? ESCAPE '\\'")
        params.append(f"%{escape_like(args.area)}%")

    if args.title:
        conditions.append("LOWER(courses.title) LIKE ? ESCAPE '\\'")
        params.append(f"%{escape_like(args.title)}%")

    if conditions:
        cmd += " WHERE " + " AND ".join(conditions)

    cmd += """
    ORDER BY crosslistings.dept,
             crosslistings.coursenum,
             classes.classid
    """

    return cmd, params

def wrap_text(text):
    return textwrap.fill(
        text,
        width=72,
        subsequent_indent=' ' * 23,
        break_long_words=False,
        break_on_hyphens=False
    )

def print_all(rows):
    print("ClsId Dept CrsNum Area Title")
    print("----- ---- ------ ---- -----")

    for (classid, dept, num, area, title) in rows:
        row = '%5s %4s %6s %4s %s' % (
            classid,
            dept,
            num,
            area or '',
            title
        )
        print(wrap_text(row))


# --- main function ---
def main():
    args = parse_args()
    conn = connect_db()
    cur = conn.cursor()

    sql, params = build_query(args)
    cur.execute(sql, params)
    rows = cur.fetchall()
    
    print_all(rows)
    conn.close()
    sys.exit(0) # normal exit


if __name__ == '__main__':
    main()
