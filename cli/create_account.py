#!/usr/bin/python
"""
    Create User Account
    ===================

"""

import argparse
from sulcilab.database import SessionLocal, sulcilab_cli
from sulcilab.core.user import PUserCreate, create_admin_user, create_user


@sulcilab_cli
def main():
    parser = argparse.ArgumentParser(description="Create a new user account")
    parser.add_argument('email', type=str, help='User\'s E-mail')
    parser.add_argument('username', type=str, help='User\'s name')
    parser.add_argument('password', type=str, help='User\'s password')
    parser.add_argument('--admin', dest="admin", default=False, action="store_true", help='Add admin privileges')
    args = parser.parse_args()

    user = PUserCreate(
        email=args.email,
        username=args.username,
        password=args.password,
    )

    if args.admin:
        create_admin_user(SessionLocal(), user)
    else:
        create_user(SessionLocal(), user)

if __name__ == "__main__":
    main()
