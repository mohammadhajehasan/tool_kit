"""
وحدة حماية وتشفير ملفات PDF وإلغاء الحماية.
تستخدم pikepdf (AES-256) لتعيين كلمة مرور وفتح الملفات المحمية.
"""

import os


class ProtectError(Exception):
    """يُرفع عند فشل الحماية أو إلغائها"""
    pass


def protect_pdf(
    input_path: str,
    output_path: str,
    user_password: str,
    owner_password: str | None = None,
    allow_print: bool = True,
    allow_copy: bool = False,
    allow_modify: bool = False,
) -> str:
    """
    يشفر ملف PDF بكلمة مرور (AES-256 إن أمكن).

    user_password: مطلوبة لفتح الملف
    owner_password: لإدارة الصلاحيات (إن تُركت فارغة تُساوى user_password)
    """
    try:
        import pikepdf
        from pikepdf import Permissions, Encryption
    except ImportError as e:
        raise ProtectError("pikepdf غير مثبّت. ثبّته: pip install pikepdf") from e

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")
    if not user_password:
        raise ProtectError("يجب إدخال كلمة مرور لفتح الملف")

    owner = owner_password or user_password
    perms = Permissions(
        accessibility=True,
        extract=allow_copy,
        modify_annotation=allow_modify,
        modify_assembly=allow_modify,
        modify_form=allow_modify,
        modify_other=allow_modify,
        print_highres=allow_print,
        print_lowres=allow_print,
    )

    try:
        with pikepdf.open(input_path) as pdf:
            pdf.save(
                output_path,
                encryption=Encryption(
                    user=user_password,
                    owner=owner,
                    allow=perms,
                    aes=True,
                    R=6,
                ),
            )
    except Exception as e:
        raise ProtectError(f"فشل تشفير الملف: {e}") from e

    return output_path


def unlock_pdf(input_path: str, output_path: str, password: str) -> str:
    """يلغي حماية ملف PDF بعد إدخال كلمة المرور الصحيحة"""
    try:
        import pikepdf
    except ImportError as e:
        raise ProtectError("pikepdf غير مثبّت. ثبّته: pip install pikepdf") from e

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")
    if not password:
        raise ProtectError("يجب إدخال كلمة المرور")

    try:
        with pikepdf.open(input_path, password=password) as pdf:
            pdf.save(output_path)
    except pikepdf.PasswordError as e:
        raise ProtectError("كلمة المرور غير صحيحة") from e
    except Exception as e:
        raise ProtectError(f"فشل إلغاء الحماية: {e}") from e

    return output_path


def is_encrypted(path: str) -> bool:
    """يتحقق إن كان الملف محمياً بكلمة مرور"""
    try:
        import pikepdf
        with pikepdf.open(path) as pdf:
            return bool(pdf.is_encrypted)
    except Exception:
        try:
            import pikepdf
            pikepdf.open(path, password="")
            return False
        except Exception:
            return True
