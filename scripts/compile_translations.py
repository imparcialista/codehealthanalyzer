#!/usr/bin/env python3
"""Script para compilar traduções do CodeHealthAnalyzer.

Este script compila os arquivos .po em arquivos .mo para uso em produção.
"""

import os
import subprocess
from pathlib import Path


def compile_po_files():
    """Compila todos os arquivos .po encontrados."""
    project_root = Path(__file__).parent.parent
    locale_dir = project_root / "locale"

    if not locale_dir.exists():
        print(f"Diretório locale não encontrado: {locale_dir}")
        return False

    compiled_count = 0

    # Procurar por arquivos .po
    for po_file in locale_dir.rglob("*.po"):
        mo_file = po_file.with_suffix(".mo")

        try:
            # Tentar usar msgfmt primeiro
            subprocess.run(
                ["msgfmt", "-o", str(mo_file), str(po_file)],
                capture_output=True,
                text=True,
                check=True,
            )

            print(
                f"✅ Compilado: {po_file.relative_to(project_root)} -> {mo_file.relative_to(project_root)}"
            )
            compiled_count += 1

        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: compilar usando Python puro
            try:
                compile_po_with_python(po_file, mo_file)
                print(
                    f"✅ Compilado (Python): {po_file.relative_to(project_root)} -> {mo_file.relative_to(project_root)}"
                )
                compiled_count += 1
            except Exception as e:
                print(f"❌ Erro ao compilar {po_file}: {e}")

    print(f"\n📊 Total de arquivos compilados: {compiled_count}")
    return compiled_count > 0


def compile_po_with_python(po_file, mo_file):
    """Compila arquivo .po usando Python puro (fallback)."""
    import struct

    # Ler arquivo .po
    translations = {}
    current_msgid = None
    current_msgstr = None
    in_msgid = False
    in_msgstr = False

    with open(po_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith("msgid "):
                # Salvar tradução anterior se existir
                if current_msgid is not None and current_msgstr is not None:
                    if current_msgid:  # Não incluir string vazia
                        translations[current_msgid] = current_msgstr

                # Nova msgid
                current_msgid = line[6:].strip('"')
                current_msgstr = None
                in_msgid = True
                in_msgstr = False

            elif line.startswith("msgstr "):
                current_msgstr = line[7:].strip('"')
                in_msgid = False
                in_msgstr = True

            elif line.startswith('"') and (in_msgid or in_msgstr):
                # Continuação de string
                content = line.strip('"')
                if in_msgid and current_msgid is not None:
                    current_msgid += content
                elif in_msgstr and current_msgstr is not None:
                    current_msgstr += content

            elif line == "" or line.startswith("#"):
                # Linha vazia ou comentário - resetar flags
                in_msgid = False
                in_msgstr = False

    # Adicionar última tradução
    if current_msgid is not None and current_msgstr is not None and current_msgid:
        translations[current_msgid] = current_msgstr

    # Criar arquivo .mo (formato binário simplificado)
    keys = list(translations.keys())
    values = list(translations.values())

    # Cabeçalho do arquivo .mo
    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + sum(len(k.encode("utf-8")) for k in keys)

    with open(mo_file, "wb") as f:
        # Magic number
        f.write(struct.pack("<I", 0x950412DE))
        # Version
        f.write(struct.pack("<I", 0))
        # Number of entries
        f.write(struct.pack("<I", len(keys)))
        # Offset of key table
        f.write(struct.pack("<I", 7 * 4))
        # Offset of value table
        f.write(struct.pack("<I", 7 * 4 + 8 * len(keys)))
        # Hash table size (0 = no hash table)
        f.write(struct.pack("<I", 0))
        # Offset of hash table
        f.write(struct.pack("<I", 0))

        # Key table
        offset = keystart
        for key in keys:
            key_bytes = key.encode("utf-8")
            f.write(struct.pack("<I", len(key_bytes)))
            f.write(struct.pack("<I", offset))
            offset += len(key_bytes)

        # Value table
        offset = valuestart
        for value in values:
            value_bytes = value.encode("utf-8")
            f.write(struct.pack("<I", len(value_bytes)))
            f.write(struct.pack("<I", offset))
            offset += len(value_bytes)

        # Keys
        for key in keys:
            f.write(key.encode("utf-8"))

        # Values
        for value in values:
            f.write(value.encode("utf-8"))


def create_pot_template():
    """Cria o arquivo template .pot para traduções."""
    project_root = Path(__file__).parent.parent
    locale_dir = project_root / "locale"
    pot_file = locale_dir / "codehealthanalyzer.pot"

    # Criar diretório se não existir
    locale_dir.mkdir(exist_ok=True)

    # Encontrar arquivos Python
    python_files = []
    for py_file in project_root.rglob("*.py"):
        # Pular arquivos de build, cache, etc.
        if any(
            part.startswith(".") or part in ["build", "dist", "__pycache__"]
            for part in py_file.parts
        ):
            continue
        python_files.append(str(py_file))

    try:
        # Extrair strings usando xgettext
        cmd = [
            "xgettext",
            "--language=Python",
            "--keyword=_",
            "--keyword=ngettext:1,2",
            "--output=" + str(pot_file),
            "--from-code=UTF-8",
            "--package-name=CodeHealthAnalyzer",
            "--package-version=1.0.0",
            "--msgid-bugs-address=contato@luarco.com.br",
        ] + python_files

        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Template criado: {pot_file.relative_to(project_root)}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar template: {e}")
        return False
    except FileNotFoundError:
        print("❌ xgettext não encontrado. Instale o gettext.")
        return False


def main():
    """Função principal."""
    print("🌐 Compilando traduções do CodeHealthAnalyzer...\n")

    # Criar template se solicitado
    if "--create-pot" in os.sys.argv:
        print("📝 Criando template de tradução...")
        create_pot_template()
        print()

    # Compilar traduções
    success = compile_po_files()

    if success:
        print("\n🎉 Traduções compiladas com sucesso!")
    else:
        print("\n❌ Falha ao compilar traduções.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
