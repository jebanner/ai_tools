#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import locale

def check_encoding():
    """检查系统编码设置"""
    print(f"Default Encoding: {sys.getdefaultencoding()}")
    print(f"Filesystem Encoding: {sys.getfilesystemencoding()}")
    print(f"Locale Encoding: {locale.getpreferredencoding()}")
    print(f"LANG: {os.environ.get('LANG', 'Not Set')}")
    print(f"LC_ALL: {os.environ.get('LC_ALL', 'Not Set')}")
    print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'Not Set')}")

def main():
    """Run administrative tasks."""
    # 检查编码设置
    check_encoding()
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wxcloudrun.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main() 