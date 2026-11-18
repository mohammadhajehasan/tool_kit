"""حماية ملفات PDF بكلمة مرور (AES-256) وإزالة الحماية — عبر pikepdf."""

import os


class ProtectError(Exception):
    pass


def is_encrypted(src_path: str) -> bool:
    """يخبر إن كان الملف مشفّراً."""
    import pikepdf

    if not os.path.isfile(src_path):
        return False
    try:
        with pikepdf.open(src_path) as pdf:
            return bool(pdf.is_encrypted)
    except pikepdf.PasswordError:
        return True
    except Exception:
        return False


def protect(
    src_path: str,
    output_path: str,
    user_password: str,
    owner_password: str | None = None,
    allow_print: bool = True,
    allow_copy: bool = False,
    allow_modify: bool = False,
) -> str:
    """يشفّر الملف بكلمة مرور مع أذونات قابلة للتحكم."""
    import pikepdf

    if not user_password:
        raise ProtectError("أدخل كلمة المرور أولاً")
    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"الملف غير موجود: {src_path}")

    try:
        pdf = pikepdf.open(src_path)
    except pikepdf.PasswordError:
        raise ProtectError("الملف محمي مسبقاً — استخدم «إزالة الحماية» أولاً")
    except Exception as e:
        raise ProtectError(f"تعذر فتح الملف: {e}")

    try:
        perms = pikepdf.Permissions(
            accessibility=True,
            extract=allow_copy,
            modify_annotation=allow_modify,
            modify_assembly=allow_modify,
            modify_form=allow_modify,
            modify_other=allow_modify,
            print_lowres=allow_print,
            print_highres=allow_print,
        )
        pdf.save(
            output_path,
            encryption=pikepdf.Encryption(
                user=user_password,
                owner=owner_password or user_password,
                R=6,  # AES-256
                allow=perms,
            ),
        )
    finally:
        pdf.close()
    return output_path


def unprotect(src_path: str, output_path: str, password: str) -> str:
    """يزيل التشفير من ملف يملك المستخدم كلمة مروره."""
    import pikepdf

    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"الملف غير موجود: {src_path}")

    try:
        pdf = pikepdf.open(src_path, password=password or "")
    except pikepdf.PasswordError:
        raise ProtectError("كلمة المرور غير صحيحة")
    except Exception as e:
        raise ProtectError(f"تعذر فتح الملف: {e}")

    try:
        pdf.save(output_path)  # حفظ بدون تشفير
    finally:
        pdf.close()
    return output_path
