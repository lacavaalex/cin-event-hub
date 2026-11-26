"""Troca de senha de um administrador existente, sem expor a nova senha."""

from getpass import getpass

from app.core.security import hash_password
from app.database.database import SessionLocal
from app.repositories.user_repository import get_admin_by_email


def main():
    email = input("E-mail do administrador existente: ").strip()
    password = getpass("Nova senha (minimo 12 caracteres): ")
    confirmation = getpass("Confirme a nova senha: ")

    if len(password) < 12 or password != confirmation:
        print("Senha curta ou confirmacao diferente. Nenhuma alteracao realizada.")
        return

    with SessionLocal() as db:
        admin = get_admin_by_email(db, email)
        if admin is None:
            print("Administrador nao encontrado. Nenhuma alteracao realizada.")
            return
        admin.hashed_password = hash_password(password)
        db.commit()

    print("Senha atualizada. Entre novamente no painel com a nova senha.")


if __name__ == "__main__":
    main()
