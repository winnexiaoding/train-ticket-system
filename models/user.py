from passlib.hash import sha256_crypt
import pymysql


class User:
    @staticmethod
    def get_user_by_username(connection, uid):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pwd, is_deleted FROM users WHERE uid=%s", (uid,))
                return cursor.fetchone()
        except pymysql.MySQLError as e:
            return None

    @staticmethod
    def create_user(connection, uid, password, uname):
        hashed_password = sha256_crypt.hash(password)
        try:

            with connection.cursor() as cursor:
                sql = f"INSERT INTO users (uid, pwd, uname) VALUES ('{uid}', '{hashed_password}', '{uname}')"
                cursor.execute(sql)
                connection.commit()
                return True
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            connection.rollback()
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    @staticmethod
    def update_password(connection, uid, old_password, new_password) -> bool:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pwd FROM users WHERE uid=%s", (uid,))
                result = cursor.fetchone()
                if result and sha256_crypt.verify(old_password, result[0]):
                    hashed_new_password = sha256_crypt.hash(new_password)
                    cursor.execute("UPDATE users SET pwd=%s WHERE uid=%s", (hashed_new_password, uid))
                    connection.commit()
                    return True
                else:
                    return False
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            connection.rollback()
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    @staticmethod
    def delete_user(connection, uid) -> bool:
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE users SET is_deleted=1 WHERE uid=%s", (uid,))
                connection.commit()
                return True
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            connection.rollback()
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    @staticmethod
    def get_all_users(connection):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE is_deleted=0")
                # 生成列表的列表，列表的每一个元素是元组，包含uid, uname
                result = cursor.fetchall()
                # 转换成列表
                result = [{'uid': item[0], 'name': item[2]} for item in result]
                return result
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    @staticmethod
    def search_user(connection, keyword):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE is_deleted=0 AND (uid LIKE %s OR uname LIKE %s)",
                               ('%' + keyword + '%', '%' + keyword + '%'))
                # 生成列表的列表，列表的每一个元素是元组，包含uid, uname
                result = cursor.fetchall()
                # 转换成列表
                result = [{'uid': item[0], 'name': item[2]} for item in result]
                return result
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    @staticmethod
    def edit_user(connection, uid, password, uname) -> bool:
        try:
            with connection.cursor() as cursor:
                # 验证密码是否正确
                cursor.execute("SELECT pwd FROM users WHERE uid=%s", (uid,))
                result = cursor.fetchone()
                if result and sha256_crypt.verify(password, result[0]):
                    cursor.execute("UPDATE users SET uname=%s WHERE uid=%s", (uname, uid))
                    connection.commit()
                    return True
                else:
                    return False
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            connection.rollback()
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

